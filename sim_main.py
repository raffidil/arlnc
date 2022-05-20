
import simpy
import numpy as np
from block_based_rlnc import BlockBasedRLNC
from decoder import Decoder
from encoder import Encoder
from packet import Packet

from cable import Cable


def sender(env: simpy.Environment, cable, encoder: Encoder):

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
            print('Sender:: send gens:', current_generation_window,
                  "total:", len(packets_to_send), "time:", env.now)
            cable.put(packets_to_send)

        response = yield cable.get()
        print('Sender receive:', response, "\n")
        # print('Sender: Received ACK %d while %s' % (env.now, ack))
        # for index, generation_id in enumerate(current_generation_window):
        #     encoder.update_generation_delivery(generation_id, True)


def receiver(env, cable, decoder: Decoder):
    while True:
        # Get event for message pipe

        received_packets = yield cable.get()
        print("Receiver:: total:", len(received_packets), "time:", env.now)
        decoder.recover_data(received_packets)
        # print([p.generation_id for i, p in enumerate(received_packets)])
        # for i, p in enumerate(received_packets):
        #     print(p.generation_id)
        # for packet in received_packets:
        #     decoder.handle_decode(packet)

        # decoder_buffer = decoder.recover_data(received_packets)
        # print('Receiver: Received this at %d while %s' % (env.now, msg))
        cable.put('Receiver sent ACK at %d' % env.now)

# ___________________________________________#


rlnc = BlockBasedRLNC(field_order=2**8, generation_size=8,
                      packet_size=16, total_size=4250)
encoder = rlnc.get_encoder()
decoder = rlnc.get_decoder()


encode_gen_buff = encoder.create_systematic_packets_generation_buffer(
    force_to_recreate=True)

# Setup and start the simulation
print('Event Latency')
env = simpy.Environment()

cable = Cable(env, 1)
env.process(sender(env, cable, encoder))
env.process(receiver(env, cable, decoder))

env.run()
