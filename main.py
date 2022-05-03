import json
from numpy.linalg import matrix_rank
import numpy as np
import galois
from encoder import Encoder


encoder = Encoder(field_order=2**8, generation_size=8,
                  packet_size=16, total_size=4450)


packets_to_send = encoder._helper_prepare_data_to_send(
    force_to_recreate=True, redundancy=4)


for p in packets_to_send:
    # if(p.generation_id == 0):
    # print("\ndata:\n", len(p.data))
    # print("coef vector:\n", p.coefficient_vector)
    # print("gen ID:", p.generation_id)
    print(p.generation_id, p.generation_size, p.coefficient_vector)
