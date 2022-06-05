from pydoc import cram
import random
import re
import numpy as np
import galois
from os.path import exists


# field_order = 2**8
# generation_size = 16  # number of packets in a gen
# packet_size = 1024  # bytes
# total_size = generation_size * packet_size

# GF = galois.GF(field_order, display="int")

# packet_matrix = create_packet_matrix(total_size, packet_size)
# coefficient_matrix = create_random_coefficient_matrix(3)
# coded_matrix = create_coded_packet_matrix(coefficient_matrix, packet_matrix)

# print("packets:\n ", packet_matrix, "\n")
# print("coefficients:\n ", coefficient_matrix, "\n")
# print("coded packets:\n ", coded_matrix, "\n")

# # remove last 3 packet during the transmission
# received_systematic_packets = packet_matrix[0:14, :]
# # assume that the all coded packets received successfully
# received_coded_packets = coded_matrix[:, :]
# received_coefficients_matrix = coefficient_matrix[:, :]

# received_systematic_packets_count = np.shape(
#     received_systematic_packets)[0]
# received_coded_packets_count = np.shape(
#     received_coded_packets)[0]

# redundant_packet_margin = (
#     received_systematic_packets_count + received_coded_packets_count) - generation_size

# if(redundant_packet_margin > 0):
#     received_coded_packets = received_coded_packets[0:len(
#         received_coded_packets)-redundant_packet_margin, :]
#     received_coefficients_matrix = received_coefficients_matrix[0:len(
#         received_coefficients_matrix)-redundant_packet_margin, :]

# received_packets = GF(np.concatenate(
#     (received_systematic_packets, received_coded_packets)))
# received_coefficients = GF(np.concatenate(
#     (GF(np.eye(received_systematic_packets_count, generation_size, dtype="int")), received_coefficients_matrix)))


# received_coefficients_rank = np.linalg.matrix_rank(received_coefficients)
# print("received coef. rank:", received_coefficients_rank)

# if(received_coefficients_rank == generation_size):
#     x = np.linalg.solve(received_coefficients, received_packets)
#     print("\nrecovered packets:\n ", x)
#     print("\nData size: ", total_size, " byte")
#     print("\nPacket size: ", packet_size, " byte")
#     print("\nWare all packets recovered? ",
#           np.array_equal(x, packet_matrix))
# else:
#     print("\n\nERROR: not enough information to decode the original packet!\n")
#     print("required additional coded packets: ",
#           generation_size-received_coefficients_rank)

# a = read_random_string()
# print(a)
