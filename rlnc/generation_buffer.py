from generation import Generation


class GenerationBuffer:
    def __init__(self, GF):
        self.buffer: list[Generation | None] = []
        self.GF = GF

    def insert(self, element: Generation, index: int):
        last_element_index = len(self.buffer) - 1
        if index > last_element_index:
            delta = index-last_element_index
            self.buffer = self.buffer + [None] * delta
        self.buffer[index] = element

    def get_buffer(self):
        return self.buffer

    def get_element(self, index=0):
        if(index > len(self.buffer)-1):
            return None
        return self.buffer[index]

    def get_buffer_data(self):
        result = []
        for generation in self.buffer:
            if generation is None:
                result.append(None)
                continue
            if generation.has_recovered:
                for packet_data in generation.decoded_data:
                    result = result + [packet_data]
        return self.GF(result)
