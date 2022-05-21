import galois
from decoder import Decoder
from encoder import Encoder
from packet import Packet

from numpy.random import default_rng
import numpy as np
import random


class BlockBasedRLNC:
    def __init__(self, field_order=2**8, generation_size=16, packet_size=1024, total_size=16384, initial_window_size=4, initial_redundancy=4):
        self.field_order = field_order
        self.generation_size = generation_size  # number of packets in a gen
        self.packet_size = packet_size  # bytes
        self.total_size = total_size
        self.GF = galois.GF(field_order, display="int")
        self.encoder = Encoder(GF=self.GF, generation_size=generation_size,
                               packet_size=packet_size, total_size=total_size,
                               initial_window_size=initial_window_size,
                               initial_redundancy=initial_redundancy)
        self.decoder = Decoder(GF=self.GF, generation_size=generation_size,
                               packet_size=packet_size, total_size=total_size)

    def get_encoder(self):
        return self.encoder

    def get_decoder(self):
        return self.decoder

    def _prepare_data_to_send(self, force_to_recreate=False, redundancy=1) -> tuple[list[Packet], list[Packet]]:
        systematic_packets = self.encoder.create_packet_vector(
            force_to_recreate=force_to_recreate)
        number_of_generations = self.encoder.get_generation_count(
            systematic_packets)

        packets_to_send: list[Packet] = []
        for generation in range(number_of_generations):
            generation_packets = self.encoder.get_packets_by_generation_id(
                systematic_packets, generation)
            coded_packets = self.encoder.create_coded_packet_vector(
                generation_packets, generation_id=generation, count=redundancy)
            packets_to_send = packets_to_send + generation_packets + coded_packets
        return packets_to_send, systematic_packets

    def _apply_loss_to_packets(self, packets: list[Packet], loss_rate=0.1):
        number_of_packets = len(packets)
        number_of_lost_packets = int(np.ceil(number_of_packets*loss_rate))
        rng = default_rng()
        lost_packets_index = rng.choice(
            number_of_packets, size=number_of_lost_packets, replace=False)
        result = []
        for index, packet in enumerate(packets):
            if(index not in lost_packets_index):
                result = result + [packet]
        # shuffle the packets to emulate the out-of-order delivery
        # random.shuffle(result)
        return result
