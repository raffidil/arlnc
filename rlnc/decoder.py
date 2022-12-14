import numpy as np
from generation_buffer import GenerationBuffer
from generation import Generation
from packet import Packet
from response_packet import ResponsePacket


class Decoder:
    def __init__(self, GF, generation_size=16):
        self.generation_size = generation_size  # number of packets in a gen
        self.GF = GF
        self.generation_buffer = GenerationBuffer(GF)

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
            print("E: genSize,gen_id,number_of_packs,redund_pck_mrg,rank", generation_size,
                  generation_id, number_of_packets, redundant_packet_margin, coefficients_rank)
            return []

    def recover_data(self, packets: list[Packet]):
        effective_packets_count = 0
        linearly_dependent_count = 0  # packets that don't have decoding value
        redundant_count = 0  # packets that their generation had decoded
        for packet in packets:
            generation_id = packet.generation_id
            generation_size = packet.generation_size
            current_generation = self.generation_buffer.get_element(
                generation_id)

            if(current_generation == None):
                new_generation = Generation(
                    generation_size=generation_size, generation_id=generation_id, GF=self.GF)
                new_generation.add_packet(packet)
                current_generation = new_generation

            else:
                if(current_generation.has_recovered or len(current_generation.packets) == generation_size):
                    current_generation.increase_number_of_received_packets()
                    self.generation_buffer.insert(
                        current_generation, generation_id)
                    redundant_count += 1
                    # skip the packet (packet is redundant), all data has recovered before
                    continue

                next_coefficients = self.GF(current_generation.get_coefficients() +
                                            [packet.coefficient_vector])
                next_coefficients_rank = np.linalg.matrix_rank(
                    next_coefficients)

                if(len(next_coefficients) != next_coefficients_rank):
                    print('\npacket is dependant to previous ones, drop\n')
                    linearly_dependent_count += 1
                    continue  # not saving the dependant packet for decoding

                current_generation.add_packet(packet)

            # because we ensure the linear independency of all stored packets, the next line is similar to
            # checking the equality of stored packets length with gen_size
            current_generation_rank = current_generation.get_rank()
            if(current_generation_rank == generation_size):
                # to do: stop timer for the gen
                recovered_generation_data = self.recover_generation_data(
                    current_generation.packets, generation_id)
                current_generation.has_recovered = True
                current_generation.store_decoded_data(
                    recovered_generation_data)
            # else:
                # to do: restart timer for gen i
            current_generation.increase_number_of_received_packets()
            self.generation_buffer.insert(current_generation, generation_id)
            effective_packets_count += 1
        return effective_packets_count, linearly_dependent_count, redundant_count, self.generation_buffer

    def create_response_packet(self):
        # get last not empty generation id
        response_packet = ResponsePacket()
        last_received_generation_id = next(s for s in reversed(
            self.generation_buffer.buffer) if s).generation_id
        for generation_id in range(last_received_generation_id + 1):
            generation = self.generation_buffer.get_element(generation_id)
            if(generation == None):
                print('== gen id %d is not received, fill with needed %d' %
                      (generation_id, self.generation_size))
                response_packet.add_feedback(
                    generation_id, self.generation_size)
                continue
            # if(generation.has_recovered):
            #     continue
            # rank = generation.get_rank()
            generation_size = generation.generation_size
            response_packet.add_feedback(
                generation_id, generation_size-generation.number_of_received_packets)
        return response_packet

    def get_decoded_data(self):
        result = []
        for i, generation in enumerate(self.generation_buffer.buffer):
            generation_decoded_data = generation.decoded_data
            for j, decoded_data in enumerate(generation_decoded_data):
                result.append(decoded_data)
        return self.GF(result)
