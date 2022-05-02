import json
from numpy.linalg import matrix_rank
import numpy as np
import galois
from encoder import Encoder

# from utils import create_coded_packet_matrix, create_packet_matrix, create_random_coefficient_matrix


encoder = Encoder(field_order=2**8, generation_size=8,
                  packet_size=16, total_size=128)


systematic_packets = encoder.create_packet_vector()
coded_packet = encoder.create_coded_packet(systematic_packets, generation_id=0)


for p in systematic_packets:
    print(p.data)
    print(p.coefficient_vector)
    print(p.generation_id)

print("\n", coded_packet.data, "\n", coded_packet.generation_id,
      "\n", coded_packet.coefficient_vector)
