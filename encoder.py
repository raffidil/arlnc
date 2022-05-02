from multiprocessing.dummy import Array
import random
import re
import numpy as np
import galois
from os.path import exists
from packet import Packet


class Encoder:
    def __init__(self, field_order=2**8, generation_size=16, packet_size=1024, total_size=16384):
        self.field_order = field_order
        self.generation_size = generation_size  # number of packets in a gen
        self.packet_size = packet_size  # bytes
        self.total_size = total_size
        self.GF = galois.GF(field_order, display="int")

    def create_random_binary_string(self):  # both in bytes
        binary_string = ""
        zero_margin = ""
        # number of zeroes required for make the created bytes mod of packet size
        required_additional_zeroes = (
            self.packet_size - (self.total_size % self.packet_size)) % self.packet_size

        for i in range(self.total_size * 8):
            temp = str(random.randint(0, 1))
            binary_string += temp

        for i in range(required_additional_zeroes * 8):
            zero_margin += "0"

        result = zero_margin + binary_string
        with open('output.binary', 'w') as f:
            f.write(result)
        return result

    def make_matrix_from_binary_string(self, binary_string):
        binary_data_array = re.findall('........', binary_string)
        data = []
        for i in binary_data_array:
            data = data + [int(i, 2)]
        matrix = self.GF(np.reshape(data, (-1, self.packet_size)))
        return matrix

    def read_random_binary_string(self):
        with open('output.binary', 'r') as f:
            binary_string = f.read()
            return binary_string

    def create_packet_vector(self) -> list[Packet]:
        file_exists = exists("output.binary")
        binary_string = ""
        if(file_exists):
            binary_string = self.read_random_binary_string()
        else:
            binary_string = self.create_random_binary_string()
        byte_matrix = self.make_matrix_from_binary_string(binary_string)

        packet_vector = []
        for index, row in enumerate(byte_matrix):
            generation_id = int(index/self.generation_size)
            packet_index_in_generation = index % self.generation_size
            coefficients = np.zeros(self.generation_size, dtype="int")
            coefficients[packet_index_in_generation] = 1
            new_packet = Packet(
                data=row, coefficient_vector=coefficients, generation_id=generation_id)
            packet_vector = packet_vector + [new_packet]
        return packet_vector

    def get_generation_count(self, packets: list[Packet]) -> int:
        return int(np.ceil(len(packets)/self.generation_size))

    def get_packets_by_generation_id(self, packets: list[Packet], generation_id: int) -> list[Packet]:
        result = []
        for packet in packets:
            if(packet.generation_id == generation_id):
                result = result + [packet]
        return result

    def create_random_coefficient_vector(self):
        coefficient_vector = []
        for i in range(self.generation_size):
            temp = random.randint(0, self.field_order-1)
            coefficient_vector += [temp]
        return self.GF(np.array(coefficient_vector))

    def create_coded_packet(self, systematic_packets: list[Packet], generation_id: int):
        random_coefficient_vector = self.create_random_coefficient_vector()
        random_coefficient_1D_matrix = random_coefficient_vector.reshape(
            (-1, self.generation_size))

        packet_data_matrix = []
        for packet in systematic_packets:
            if(packet.generation_id == generation_id):
                packet_data_matrix = packet_data_matrix + \
                    [self.GF(packet.data)]

        packet_data_galois_matrix = self.GF(packet_data_matrix)
        coded_packet_data = random_coefficient_1D_matrix.dot(
            packet_data_galois_matrix)[0]  # returns 1xN matrix => turn to vector
        coded_packet = Packet(
            data=coded_packet_data, coefficient_vector=random_coefficient_vector, generation_id=generation_id)
        return coded_packet
