from multiprocessing.dummy import Array
import random
import re
import numpy as np
import galois
from os.path import exists
from packet import Packet


class Decoder:
    def __init__(self, field_order=2**8, generation_size=16, packet_size=1024, total_size=16384):
        self.field_order = field_order
        self.generation_size = generation_size  # number of packets in a gen
        self.packet_size = packet_size  # bytes
        self.total_size = total_size
        self.GF = galois.GF(field_order, display="int")
