from multiprocessing.dummy import Array
import random
import re
import numpy as np
import galois
from packet import Packet


class Decoder:
    def __init__(self, field_order=2**8, generation_size=16, packet_size=1024, total_size=16384):
        self.field_order = field_order
        self.generation_size = generation_size  # number of packets in a gen
        self.packet_size = packet_size  # bytes
        self.total_size = total_size
        self.GF = galois.GF(field_order, display="int")

    def recover_generation_data(self, packets: list[Packet], generation_id=1):
        generation: list[Packet] = []
        coefficients = []
        data = []
        for packet in packets:
            if(packet.generation_id == generation_id):
                generation = generation + [packet]

        generation_size = generation[0].generation_size

        number_of_packets = len(generation)
        redundant_packet_margin = number_of_packets - generation_size

        if(redundant_packet_margin > 0):
            generation = generation[0:generation_size]

        for packet in generation:
            coefficients = coefficients + [packet.coefficient_vector]
            data = data + [packet.data]

        coefficients = self.GF(coefficients)
        data = self.GF(data)

        coefficients_rank = np.linalg.matrix_rank(coefficients)

        if(coefficients_rank == generation_size):
            return np.linalg.solve(coefficients, data)

        else:
            print("\n\nERROR: not enough information to decode the original packet!\n")
            print("required additional coded packets: ",
                  generation_size-coefficients_rank)
            return []
