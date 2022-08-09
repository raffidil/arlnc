class Packet:
    def __init__(self, data, coefficient_vector, generation_id, generation_size):
        self.data = data  # vector of bytes
        self.coefficient_vector = coefficient_vector
        self.generation_id = generation_id
        self.generation_size = generation_size
