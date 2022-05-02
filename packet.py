class Packet:
    def __init__(self, data, coefficient_vector, generation_id):
        self.data = data  # vector of bytes
        self.coefficient_vector = coefficient_vector
        self.generation_id = generation_id
        self.packet_size = len(self.data)  # number of bytes in data
