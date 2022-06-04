
import simpy
import numpy as np
from analytics import Analytics
from block_based_rlnc import BlockBasedRLNC
from decoder import Decoder
from encoder import Encoder
from packet import Packet

from cable import Cable
from response_packet import ResponsePacket


def sender(env: simpy.Environment, cable, encoder: Encoder, analytics: Analytics):
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

        loss_rate = cable.put(packets_to_send+extra_packets_to_send)
        analytics.track(time=env.now,
                        redundancy=encoder.redundancy,
                        window_size=encoder.generation_window_size,
                        generation_window=current_generation_window,
                        loss_rate=loss_rate,
                        extra_packets_count=extra_count,
                        new_coded_packets_count=new_count,
                        type="send")

        response: ResponsePacket = yield cable.get()

        if(len(response.feedback_list) > 0 if response.feedback_list else False):
            extra_packets_to_send: list[Packet] = []
            print('Sender  :: Feedback received from decoder: time(%d)' % env.now)
            average_additional_redundancy = encoder.update_encoding_redundancy_and_window_size_by_response(
                response.feedback_list)
            analytics.track(time=env.now,
                            redundancy=encoder.redundancy,
                            average_needed_packets=average_additional_redundancy,
                            type="feedback")

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


def receiver(env, cable, decoder: Decoder, analytics: Analytics):
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

# ___________________________________________#


rlnc = BlockBasedRLNC(field_order=2**8, generation_size=8,
                      packet_size=16, total_size=16384,
                      initial_redundancy=10, initial_window_size=4)
encoder = rlnc.get_encoder()
decoder = rlnc.get_decoder()


encode_gen_buff = encoder.create_systematic_packets_generation_buffer(
    force_to_recreate=True)

# Setup and start the simulation
print('Start Simulation')

env = simpy.Environment()
analytics = Analytics()

cable = Cable(env, 1, loss_mode="exponential",
              exponential_loss_param=0.05)
env.process(sender(env, cable, encoder, analytics))
env.process(receiver(env, cable, decoder, analytics))

env.run()

analytics_data = analytics.get_analytics()
for index, record in enumerate(analytics_data):
    # if(record.type == 'send'):
    #     print(
    #         f'time: {record.time} - SEND - loss rate: {record.loss_rate} - redundancy: {record.redundancy} - window size: {record.window_size} - new,extra,total: {record.new_coded_packets_count},{record.extra_packets_count},{record.extra_packets_count+record.new_coded_packets_count} - window: {record.generation_window}')
    # if(record.type == 'feedback'):
    #     print(
    #         f'time: {record.time} - FEEDBACK - avg. needed red: {record.average_needed_packets} - redundancy: {record.redundancy}')
    if(record.type == 'receive'):
        print(
            f'time: {record.time} - RECEIVE - received: {record.received_packets} - effectiveness: {np.round(record.effective_packets/record.received_packets,2)} - lin. dependant: {record.linearly_dependent_packets} - redundant: {record.redundant_packets}')
print('--- END ---')

# to do
# - change redundancy and window dynamic
#   - calculate the next window size from current response
#     (number of extra packets that corresponds the network loss rate)
# - prepare the whole generation if the needed is higher than generation_loss_threshold for next transmission (test with loss=0.95 and R=1)
# - dynamic loss
# - add analytics
