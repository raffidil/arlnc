import re
import numpy as np
import galois
from os.path import exists
from packet import Packet
from generation_buffer import GenerationBuffer
from generation import Generation
from response_packet import Feedback


class Encoder:
    def __init__(self, GF, generation_size=16, packet_size=1024, total_size=16384, initial_window_size=4, initial_redundancy=4, seed=42):
        self.field_order = GF.order
        self.field_degree = int(np.log2(self.field_order))
        if not np.log2(self.field_order).is_integer():
            raise TypeError(
                'Error while creating the galois field: Field order must be a positive and integer power of 2')
        self.generation_size = generation_size  # number of packets in a gen
        self.packet_size = packet_size  # bytes
        self.total_size = total_size
        self.GF = galois.GF(self.field_order, display="int")
        self.generation_buffer = GenerationBuffer(
            GF)  # used for storing systematic packets
        self.generation_count = int(
            np.ceil(total_size/packet_size/generation_size))
        self.generation_window_size = initial_window_size
        self.generation_current_window = []
        self.redundancy = initial_redundancy
        self.last_received_feedback_gen_id = -1
        self.max_redundancy = generation_size
        self.gws_flag = 0
        self.rnd_state = np.random.RandomState(seed)

    def create_random_binary_string(self):  # both in bytes
        binary_string = ""
        zero_margin = ""
        # number of zeroes required for make the created bytes mod of packet size
        required_additional_zeroes = (
            self.packet_size - (self.total_size % self.packet_size)) % self.packet_size

        for i in range(self.total_size * self.field_degree):
            temp = str(self.rnd_state.randint(0, 1))
            binary_string += temp

        for i in range(required_additional_zeroes * self.field_degree):
            zero_margin += "0"

        result = zero_margin + binary_string
        with open('output.binary', 'w') as f:
            f.write(result)
        return result

    def make_matrix_from_binary_string(self, binary_string):
        binary_data_array = re.findall('.' * self.field_degree, binary_string)
        data = []
        for i in binary_data_array:
            data = data + [int(i, 2)]
        matrix = self.GF(np.reshape(data, (-1, self.packet_size)))
        return matrix

    def read_random_binary_string(self):
        with open('output.binary', 'r') as f:
            binary_string = f.read()
            return binary_string

    def create_packet_vector(self, force_to_recreate=False) -> list[Packet]:
        file_exists = exists("output.binary")
        binary_string = ""
        if(file_exists and not force_to_recreate):
            binary_string = self.read_random_binary_string()
        else:
            binary_string = self.create_random_binary_string()
        byte_matrix = self.make_matrix_from_binary_string(binary_string)

        number_of_packets = len(byte_matrix)
        number_of_packets_from_incomplete_generation = number_of_packets % self.generation_size
        first_incomplete_generation_packet_index = number_of_packets - \
            number_of_packets_from_incomplete_generation

        packet_vector = []
        for index, row in enumerate(byte_matrix):
            generation_size = self.generation_size
            if index >= first_incomplete_generation_packet_index:
                generation_size = number_of_packets_from_incomplete_generation
            generation_id = int(index/self.generation_size)
            packet_index_in_generation = index % self.generation_size
            coefficients = np.zeros(generation_size, dtype="int")
            coefficients[packet_index_in_generation] = 1
            new_packet = Packet(
                data=row, coefficient_vector=coefficients, generation_id=generation_id, generation_size=generation_size)
            packet_vector = packet_vector + [new_packet]
        return packet_vector

    def get_generation_count(self, packets: list[Packet]) -> int:
        return int(np.ceil(len(packets)/self.generation_size))

    def get_systematic_data(self):
        result = []
        for index, generation in enumerate(self.generation_buffer.buffer):
            for j, packet in enumerate(generation.packets):
                result.append(packet.data)
        return self.GF(result)

    def get_packets_by_generation_id(self, packets: list[Packet], generation_id: int) -> list[Packet]:
        result: list[Packet] = []
        for packet in packets:
            if(packet.generation_id == generation_id):
                result = result + [packet]
        return result

    def create_systematic_packets_generation_buffer(self, force_to_recreate=False):
        systematic_packets = self.create_packet_vector(
            force_to_recreate=force_to_recreate)
        number_of_generations = self.get_generation_count(
            systematic_packets)

        for generation_id in range(number_of_generations):
            generation_packets = self.get_packets_by_generation_id(
                systematic_packets, generation_id)
            generation_size = generation_packets[0].generation_size
            new_generation = Generation(
                generation_size=generation_size, generation_id=generation_id, packets=generation_packets, GF=self.GF)
            self.generation_buffer.insert(new_generation, generation_id)
        return self.generation_buffer

    def create_random_coefficient_vector(self, size):
        coefficient_vector = []
        for i in range(size):
            temp = self.rnd_state.randint(0, self.field_order-1)
            coefficient_vector += [temp]
        return self.GF(np.array(coefficient_vector))

    def create_coded_packet(self, generation_id: int) -> Packet:
        systematic_packets = self.get_generation_by_id(
            generation_id).packets
        packet_set_generation_size = systematic_packets[0].generation_size
        random_coefficient_vector = self.create_random_coefficient_vector(
            packet_set_generation_size)
        random_coefficient_1D_matrix = random_coefficient_vector.reshape(
            (-1, packet_set_generation_size))

        packet_data_matrix = []
        for packet in systematic_packets:
            if(packet.generation_id == generation_id):
                packet_data_matrix = packet_data_matrix + \
                    [self.GF(packet.data)]

        packet_data_galois_matrix = self.GF(packet_data_matrix)
        coded_packet_data = random_coefficient_1D_matrix.dot(
            packet_data_galois_matrix)[0]  # returns 1xN matrix => turn to vector
        coded_packet = Packet(
            data=coded_packet_data, coefficient_vector=random_coefficient_vector, generation_id=generation_id, generation_size=packet_set_generation_size)
        return coded_packet

    def create_coded_packet_vector(self, generation_id: int, count=1) -> list[Packet]:
        coded_packets_list = []
        for i in range(count):
            coded_packet = self.create_coded_packet(
                generation_id)
            coded_packets_list = coded_packets_list + [coded_packet]
        return coded_packets_list

    def get_next_window(self, window_size=None):
        # calculate the next generation window with size of window_size
        # from the highest received feedback gen_id
        # objective: (until at least one packet from each generation has received to the decoder)
        size = window_size or self.generation_window_size
        generation_last_index = self.generation_count - 1
        next_window = []
        if(self.last_received_feedback_gen_id >= generation_last_index):  # no generation remains
            next_window = []
        elif(self.last_received_feedback_gen_id == -1):  # first window
            if(size > self.generation_count):
                next_window = [i for i in range(0, self.generation_count)]
            else:
                next_window = [i for i in range(
                    0, size)]
        else:
            next_first_item = self.last_received_feedback_gen_id+1
            next_last_item = self.last_received_feedback_gen_id+size
            if(next_last_item > generation_last_index):
                next_window = [i for i in range(
                    next_first_item, self.generation_count)]
            else:
                next_window = [i for i in range(
                    next_first_item, next_last_item+1)]

        self.generation_current_window = next_window
        return next_window

    def is_all_generations_delivered(self):
        for i, generation in enumerate(self.generation_buffer.buffer):
            if(generation.has_delivered != True):
                return False
        return True

    def get_generation_by_id(self, generation_id):
        return self.generation_buffer.get_element(generation_id)

    def update_generation_delivery(self, generation_id, status=True):
        generation = self.generation_buffer.get_element(
            generation_id)
        generation.has_delivered = status
        self.generation_buffer.insert(generation, generation_id)

    def update_last_received_feedback_gen_id(self, last_received_gen_id: int):
        self.last_received_feedback_gen_id = last_received_gen_id

    def calculate_average_feedback(self, feedback_list: list[Feedback]):
        needed_sum = 0
        number_of_responses_in_current_window = 0
        average_feedback = 0
        # extracting the needed response belonging to the last generation window
        for index, feedback in enumerate(feedback_list):
            if feedback.generation_id in self.generation_current_window:
                needed_sum = needed_sum + feedback.needed
                number_of_responses_in_current_window += 1

        if(number_of_responses_in_current_window == 0 and len(self.generation_current_window) > 0):
            average_feedback = self.generation_size

        if(number_of_responses_in_current_window > 0):
            average_feedback = int(
                np.ceil(needed_sum/number_of_responses_in_current_window))

        print('&&& avg feedback:', average_feedback)
        return average_feedback

    def update_encoding_redundancy_and_window_size_by_response(self, feedback_list: list[Feedback]):
        # update the encoding redundancy according to the feedback response
        # if the average of received response feedbacks (needed) of current generation
        # is positive: increase one, if it's negative: decrease one

        average_feedback = self.calculate_average_feedback(feedback_list)

        thresh1 = int(
            np.floor(self.generation_size*0.25))
        thresh2 = int(
            np.floor(self.generation_size*0.5))
        thresh3 = int(
            np.floor(self.generation_size*0.75))

        if(average_feedback >= thresh3):
            self.generation_window_size = 1
            self.redundancy = 1
        elif(average_feedback >= thresh1 and average_feedback < thresh3 and self.generation_window_size != 1):
            self.generation_window_size = int(
                np.ceil(self.generation_window_size/2))
            self.redundancy = int(np.ceil(self.redundancy/2))
        elif(average_feedback > 0 and average_feedback < thresh1):
            if(self.redundancy < self.max_redundancy):
                self.redundancy += 1
            self.gws_flag += 1
            if(self.gws_flag >= thresh1 and self.generation_window_size != 1):
                self.generation_window_size -= 1
                self.gws_flag = 0

        if(average_feedback == 0):
            self.generation_window_size += 1

        elif(average_feedback < 0 and average_feedback > -thresh2):
            if(self.redundancy > 1):
                self.redundancy -= 1  # min redundancy is 1
            self.gws_flag -= 1
            if(self.gws_flag <= -thresh1):
                self.generation_window_size += 1
                self.gws_flag = 0
        elif(average_feedback <= -thresh2):
            self.generation_window_size *= 2
            self.redundancy = int(np.ceil(self.redundancy/2))

        return average_feedback
