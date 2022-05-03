import json
from numpy.linalg import matrix_rank
import numpy as np
import galois
from encoder import Encoder


encoder = Encoder(field_order=2**8, generation_size=8,
                  packet_size=16, total_size=42350)


systematic_packets = encoder.create_packet_vector(force_to_recreate=True)
number_of_generations = encoder.get_generation_count(systematic_packets)

packets_to_send = []
for generation in range(number_of_generations):
    generation_packets = encoder.get_packets_by_generation_id(
        systematic_packets, generation)
    coded_packet = encoder.create_coded_packet(
        generation_packets, generation_id=generation)
    packets_to_send = packets_to_send + generation_packets + [coded_packet]

print("syst len: ", len(systematic_packets))
print("gen count: ", number_of_generations)
print("total len: ", len(packets_to_send))


for p in packets_to_send:
    # if(p.generation_id == 0):
    # print("\ndata:\n", p.data)
    # print("coef vector:\n", p.coefficient_vector)
    # print("gen ID:", p.generation_id)
    print(p.generation_id, p.generation_size, p.coefficient_vector)
