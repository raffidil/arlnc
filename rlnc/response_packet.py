class Feedback:
    def __init__(self, generation_id, needed):
        self.generation_id = generation_id
        self.needed = needed


class ResponsePacket:
    def __init__(self, feedback_list: list[Feedback] = []):
        self.feedback_list = feedback_list

    def add_feedback(self, generation_id, needed):
        self.feedback_list = self.feedback_list + \
            [Feedback(generation_id, needed)]
