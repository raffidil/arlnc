
import simpy
import numpy as np
from block_based_rlnc import BlockBasedRLNC
from decoder import Decoder
from encoder import Encoder
from packet import Packet

from cable import Cable
from response_packet import ResponsePacket


def sender(env: simpy.Environment, cable, encoder: Encoder):
    extra_packets_to_send: list[Packet] = []
    while encoder.is_all_generations_delivered() == False:
        yield env.timeout(1)
        current_generation_window = encoder.get_next_window()
        packets_to_send: list[Packet] = []

        if(len(current_generation_window) > 0):
            # create systematic and coded packets of the current window
            for index, generation_id in enumerate(current_generation_window):
                generation_systematic_packets = encoder.get_generation_by_id(
                    generation_id).packets
                generation_coded_packets = encoder.create_coded_packet_vector(
                    systematic_packets=generation_systematic_packets,
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

        cable.put(packets_to_send+extra_packets_to_send)

        response: ResponsePacket = yield cable.get()

        if(len(response.feedback_list) > 0 if response.feedback_list else False):
            extra_packets_to_send: list[Packet] = []
            print('Sender  :: Feedback received from decoder: time(%d)' % env.now)
        for feedback in response.feedback_list:
            print('gen id:', feedback.generation_id,
                  'needs', feedback.needed, "packet")
            generation_id = feedback.generation_id
            needed = feedback.needed
            if(needed <= 0):  # the generation has been decoded successfully
                encoder.update_generation_delivery(generation_id, True)
                if(feedback.generation_id > encoder.last_received_feedback_gen_id):
                    encoder.update_last_received_feedback_gen_id(
                        feedback.generation_id)
                continue
            generation_systematic_packets = encoder.get_generation_by_id(
                generation_id).packets
            generation_coded_packets = encoder.create_coded_packet_vector(
                systematic_packets=generation_systematic_packets,
                generation_id=generation_id, count=needed)
            extra_packets_to_send = extra_packets_to_send + generation_coded_packets

            # update the last received feedback generation id
            # to keep track the generation delivery image of the Decoder
            if(feedback.generation_id > encoder.last_received_feedback_gen_id):
                encoder.update_last_received_feedback_gen_id(
                    feedback.generation_id)
    print('\n No packets to send, all packets are delivered successfully')


def receiver(env, cable, decoder: Decoder):
    while True:
        # Get event for message pipe
        received_packets = yield cable.get()
        print("Receiver:: get total:", len(
            received_packets), "packets at time(%d)" % env.now)
        decoder.recover_data(received_packets)
        response_packet = decoder.create_response_packet()
        print("Receiver:: send acknowledgement at time(%d)" % env.now)
        cable.put_response(response_packet)

# ___________________________________________#


rlnc = BlockBasedRLNC(field_order=2**8, generation_size=8,
                      packet_size=16, total_size=4250, initial_redundancy=4)
encoder = rlnc.get_encoder()
decoder = rlnc.get_decoder()


encode_gen_buff = encoder.create_systematic_packets_generation_buffer(
    force_to_recreate=True)

# Setup and start the simulation
print('Start Simulation')

env = simpy.Environment()

cable = Cable(env, 1, loss_rate=0.4)
env.process(sender(env, cable, encoder))
env.process(receiver(env, cable, decoder))

env.run()

# to do
# - change redundancy and window dynamic
#   - calculate the next window size from current response
#     (number of extra packets that corresponds the network loss rate)
#   - calculate the redundancy size from current response needed packets count
# - prepare the whole generation if the needed is higher than generation_loss_threshold for next transmission
