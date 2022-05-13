import json
from numpy.linalg import matrix_rank
import numpy as np
import galois
from block_based_rlnc import BlockBasedRLNC


rlnc = BlockBasedRLNC(field_order=2**8, generation_size=8,
                      packet_size=16, total_size=4250)
encoder = rlnc.get_encoder()
decoder = rlnc.get_decoder()


packets_to_send = rlnc._prepare_data_to_send(
    force_to_recreate=True, redundancy=4)


generation_buffer = decoder.recover_data(packets_to_send)

number_of_decoded_packets = 0
for generation in generation_buffer.buffer:
    number_of_decoded_packets += len(generation.decoded_data)

print("\n packets from generation to send: \n")
selected_generation = encoder.get_packets_by_generation_id(
    packets_to_send, 7)

print("systematic packets: ")
for index, p in enumerate(selected_generation):
    print(p.data)
    if(index == 7):
        print('\n coded packets:')

# for p in generation_7_packets:
#     print(p.generation_id, p.generation_size, p.coefficient_vector)


received_packets = rlnc._apply_loss_to_packets(
    selected_generation, loss_rate=0.2)

# print("\n loss applies packets: \n")
# for p in loss_applied_packets:
#     print(p.generation_id, p.generation_size, p.coefficient_vector)

# for p in loss_applied_packets:
#     print(p.data)


print("\n recovered packets:")
result = decoder.recover_generation_data(received_packets, 7)
for p in result:
    print(p)
