from generation import Generation


class GenerationBuffer:
    def __init__(self):
        self.buffer: list[Generation | None] = []

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
