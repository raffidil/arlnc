import galois
import simpy
from decoder import Decoder
from encoder import Encoder
from packet import Packet

import numpy as np

from analytics import Analytics
from cable import Cable
from response_packet import ResponsePacket


def are_same(A, B):
    rows = len(A)
    cols = len(A[0])
    for i in range(rows):
        for j in range(cols):
            if (A[i][j] != B[i][j]):
                return False
    return True


class BlockBasedRLNC:
    def __init__(self, field_order=2**8,
                 generation_size=16,
                 packet_size=1024,
                 total_size=16384,
                 initial_window_size=1,
                 initial_redundancy=1,
                 exponential_loss_param=0.05,
                 ge_loss_good_to_bad=0.027,
                 ge_loss_bad_to_good=0.25,
                 ee_loss_error=0.25,
                 loss_rate=0,
                 seed=42,
                 force_to_recreate_new_data=False,
                 loss_mode="constant",
                 approach="arlnc"):  # arlnc, standard
        self.field_order = field_order
        self.generation_size = generation_size  # number of packets in a gen
        self.packet_size = packet_size  # bytes
        self.total_size = total_size
        self.exponential_loss_param = exponential_loss_param
        self.ge_loss_good_to_bad = ge_loss_good_to_bad
        self.ge_loss_bad_to_good = ge_loss_bad_to_good
        self.ee_loss_error = ee_loss_error
        self.loss_rate = loss_rate
        self.loss_mode = loss_mode
        self.force_to_recreate_new_data = force_to_recreate_new_data
        self.approach = approach
        self.GF = galois.GF(field_order, repr="int")
        self.encoder = Encoder(GF=self.GF, generation_size=generation_size,
                               packet_size=packet_size, total_size=total_size,
                               initial_window_size=initial_window_size,
                               initial_redundancy=initial_redundancy,
                               seed=seed)
        self.decoder = Decoder(GF=self.GF, generation_size=generation_size)
        self.seed = seed

    def get_encoder(self):
        return self.encoder

    def get_decoder(self):
        return self.decoder

    def sender(self, env: simpy.Environment, cable, encoder: Encoder, analytics: Analytics):
        extra_packets_to_send: list[Packet] = []
        while encoder.is_all_generations_delivered() == False:
            yield env.timeout(1)
            current_generation_window = encoder.get_next_window()

            packets_to_send: list[Packet] = []

            if(len(current_generation_window) > 0):
                # create systematic and coded packets of the current window
                print('*** current redundancy:', encoder.redundancy)
                for index, generation_id in enumerate(current_generation_window):
                    generation_systematic_packets = encoder.get_generation_by_id(
                        generation_id).packets
                    generation_coded_packets = encoder.create_coded_packet_vector(
                        generation_id=generation_id, count=encoder.redundancy)
                    packets_to_send = packets_to_send + \
                        generation_systematic_packets + generation_coded_packets

            print('\n')
            new_count = len(packets_to_send)
            extra_count = len(extra_packets_to_send)
            total_count = new_count + extra_count
            print('Sender  :: send gens:', current_generation_window,
                  "new: %d, extra: %d, total: %d - at time(%d)" % (new_count,
                                                                   extra_count, total_count, env.now))

            loss_rate = cable.put(packets_to_send+extra_packets_to_send)
            coded_packets_count = (
                len(current_generation_window) * encoder.redundancy) + len(extra_packets_to_send)
            print("^^^ coded packets count", coded_packets_count)
            analytics.track(time=env.now,
                            redundancy=encoder.redundancy,
                            window_size=encoder.generation_window_size,
                            generation_window=current_generation_window,
                            loss_rate=loss_rate,
                            extra_packets_count=extra_count,
                            new_coded_packets_count=new_count,
                            total_sent_packets=total_count,
                            coded_packets_count=coded_packets_count,
                            type="send")

            response: ResponsePacket = yield cable.get()

            if(len(response.feedback_list) > 0 if response.feedback_list else False):
                extra_packets_to_send: list[Packet] = []
                print('Sender  :: Feedback received from decoder: time(%d)' % env.now)
                if(self.approach == 'arlnc'):
                    average_feedback = encoder.update_encoding_redundancy_and_window_size_by_response(
                        response.feedback_list)
                    analytics.track(time=env.now,
                                    average_feedback=average_feedback,
                                    type="feedback")

                if(self.approach == 'standard'):
                    average_feedback = encoder.calculate_average_feedback(
                        response.feedback_list)
                    analytics.track(time=env.now,
                                    average_feedback=average_feedback,
                                    type="feedback")

            for feedback in response.feedback_list:
                # print('gen id:', feedback.generation_id,
                #       'needs', feedback.needed, "packet")
                generation_id = feedback.generation_id
                needed = feedback.needed
                if(needed <= 0):  # the generation has been decoded successfully
                    encoder.update_generation_delivery(generation_id, True)
                    if(feedback.generation_id > encoder.last_received_feedback_gen_id):
                        encoder.update_last_received_feedback_gen_id(
                            feedback.generation_id)
                    continue
                generation_coded_packets = encoder.create_coded_packet_vector(
                    generation_id=generation_id, count=needed)
                extra_packets_to_send = extra_packets_to_send + generation_coded_packets

                # update the last received feedback generation id
                # to keep track the generation delivery image of the Decoder
                if(feedback.generation_id > encoder.last_received_feedback_gen_id):
                    encoder.update_last_received_feedback_gen_id(
                        feedback.generation_id)

        print('\nNo packets to send, all packets are delivered successfully\n')

    def receiver(self, env, cable, decoder: Decoder, analytics: Analytics):
        while True:
            # Get event for message pipe
            received_packets = yield cable.get()
            effective, linearly_dependent, redundant, buff = decoder.recover_data(
                received_packets)
            print("Receiver:: get total:", len(
                received_packets), " & effective:", effective, "packets at time(%d)" % env.now)
            response_packet = decoder.create_response_packet()
            print("Receiver:: send acknowledgement at time(%d)" % env.now)
            analytics.track(time=env.now,
                            received_packets=len(received_packets),
                            effective_packets=effective,
                            linearly_dependent_packets=linearly_dependent,
                            redundant_packets=redundant,
                            type="receive")
            cable.put_response(response_packet)

    def initialize_packets(self):
        print('Initializing packets...')
        encode_gen_buff = self.encoder.create_systematic_packets_generation_buffer(
            force_to_recreate=self.force_to_recreate_new_data)
        return encode_gen_buff

    def run_simulation(self) -> Analytics:
        encoder = self.get_encoder()
        decoder = self.get_decoder()

        self.initialize_packets()
        # Setup and start the simulation
        print('Starting the simulation...')

        env = simpy.Environment()
        analytics = Analytics()

        cable = Cable(env, 1, loss_mode=self.loss_mode, loss_rate=self.loss_rate,
                      exponential_loss_param=self.exponential_loss_param,
                      ge_loss_bad_to_good=self.ge_loss_bad_to_good,
                      ge_loss_good_to_bad=self.ge_loss_good_to_bad,
                      ee_loss_error=self.ee_loss_error,
                      seed=self.seed)
        env.process(self.sender(env, cable, encoder, analytics))
        env.process(self.receiver(env, cable, decoder, analytics))

        env.run()

        systematic_data = encoder.get_systematic_data()
        decoded_data = decoder.get_decoded_data()
        same = are_same(systematic_data, decoded_data)

        if same:
            print('Sent and received packets are identical!')
        else:

            print('Sent and received packets are NOT identical')

        return analytics
