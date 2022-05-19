from packet import Packet
import numpy as np


class Generation:
    def __init__(self, generation_size, generation_id, GF, packets=[]):
        # used for store the packets that their coefficients are linearly independent
        self.packets: list[Packet] = packets
        self.generation_size = generation_size
        self.generation_id = generation_id
        self.decoded_data = []
        self.has_delivered = False
        self.has_recovered = False
        self.GF = GF

    def store_decoded_data(self, data):
        self.decoded_data = data

    def get_decoded_data(self):
        return self.decoded_data

    def deliver_data(self):
        self.has_delivered = True

    def add_packet(self, packet: Packet):
        self.packets.append(packet)

    def get_coefficients(self):
        coefficients = []
        for packet in self.packets:
            coefficients = coefficients + [packet.coefficient_vector]
        return coefficients

    def get_rank(self):
        coefficients = self.get_coefficients()
        coefficients = self.GF(coefficients)
        coefficients_rank = np.linalg.matrix_rank(coefficients)
        return coefficients_rank
