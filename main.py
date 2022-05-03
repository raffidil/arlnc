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

generation_7_packets = encoder.get_packets_by_generation_id(
    packets_to_send, 7)

result = decoder.recover_generation(generation_7_packets, 7)


for p in generation_7_packets:
    print(p.generation_id, p.generation_size, p.coefficient_vector)

for p in generation_7_packets:
    print("data", p.data)

print("\n")

for p in result:
    print(p)
