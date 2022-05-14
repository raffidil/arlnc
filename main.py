import json
from numpy.linalg import matrix_rank
import numpy as np
import galois
from block_based_rlnc import BlockBasedRLNC


def areSame(A, B):
    rows = len(A)
    cols = len(A[0])
    for i in range(rows):
        for j in range(cols):
            if (A[i][j] != B[i][j]):
                return False
    return True


rlnc = BlockBasedRLNC(field_order=2**8, generation_size=8,
                      packet_size=16, total_size=4250)
encoder = rlnc.get_encoder()
decoder = rlnc.get_decoder()


packets_to_send, systematic_packets = rlnc._prepare_data_to_send(
    force_to_recreate=True, redundancy=4)


received_packets = []
total_generations_count = packets_to_send[-1].generation_id + 1
for generation_id in range(total_generations_count):
    generation_packets = encoder.get_packets_by_generation_id(
        packets_to_send, generation_id)
    loss_applied_to_generation_packets = rlnc._apply_loss_to_packets(
        generation_packets, loss_rate=0.2)
    received_packets = received_packets + loss_applied_to_generation_packets

print("sys. packets count:", len(systematic_packets))
print("all packets count (sys. + coded):", len(packets_to_send))
print("received packets count (after appling loss):", len(received_packets))

generations_buffer = decoder.recover_data(received_packets)
generations_buffer_data = generations_buffer.get_buffer_data()

print("recovered packets count:", len(generations_buffer_data))

original_data = []
for systematic_packet in systematic_packets:
    original_data = original_data + [systematic_packet.data]


print("identical:", areSame(original_data, generations_buffer_data))


# _____ one generation code/decode ______
# print("\n packets from generation to send: \n")
# selected_generation = encoder.get_packets_by_generation_id(
#     packets_to_send, 7)

# print("systematic packets: ")
# for index, p in enumerate(selected_generation):
#     print(p.data)
#     if(index == 7):
#         print('\n coded packets:')

# # for p in generation_7_packets:
# #     print(p.generation_id, p.generation_size, p.coefficient_vector)


# received_packets = rlnc._apply_loss_to_packets(
#     selected_generation, loss_rate=0.2)

# # print("\n loss applies packets: \n")
# # for p in loss_applied_packets:
# #     print(p.generation_id, p.generation_size, p.coefficient_vector)

# # for p in loss_applied_packets:
# #     print(p.data)


# print("\n recovered packets:")
# result = decoder.recover_generation_data(received_packets, 7)
# for p in result:
#     print(p)
# _________________________________________
