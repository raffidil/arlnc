class Record:
    def __init__(self, time,
                 type=None,
                 redundancy=None,
                 window_size=None,
                 generation_window=None,
                 average_needed_packets=None,  # average_redundancy
                 generation_size=None,
                 loss_rate=None,
                 new_coded_packets_count=None,
                 extra_packets_count=None,
                 # decoder
                 received_packets=None,
                 effective_packets=None,
                 linearly_dependent_packets=None,
                 redundant_packets=None):
        self.time = time
        self.type = type
        self.redundancy = redundancy
        self.window_size = window_size
        self.generation_window = generation_window
        self.average_needed_packets = average_needed_packets
        self.generation_size = generation_size
        self.loss_rate = loss_rate
        self.new_coded_packets_count = new_coded_packets_count
        self.extra_packets_count = extra_packets_count
        self.received_packets = received_packets
        self.effective_packets = effective_packets
        self.linearly_dependent_packets = linearly_dependent_packets
        self.redundant_packets = redundant_packets


class Analytics:

    def __init__(self):
        self.data: list[Record] = []

    def insert_record(self, time: int, record: Record):
        last_element_index = len(self.data) - 1
        if time > last_element_index:
            delta = time-last_element_index
            self.data = self.data + [None] * delta
        self.data[time] = record

    def track(self, time,
              type=None,
              redundancy=None,
              window_size=None,
              generation_window=None,
              average_needed_packets=None,  # average_redundancy
              generation_size=None,
              loss_rate=None,
              new_coded_packets_count=None,
              extra_packets_count=None,
              # decoder
              received_packets=None,
              effective_packets=None,
              linearly_dependent_packets=None,
              redundant_packets=None):
        record = self.get_record(time)
        record.type = type
        record.redundancy = redundancy
        record.window_size = window_size
        record.generation_window = generation_window
        record.average_needed_packets = average_needed_packets
        record.generation_size = generation_size
        record.loss_rate = loss_rate
        record.new_coded_packets_count = new_coded_packets_count
        record.extra_packets_count = extra_packets_count
        record.received_packets = received_packets
        record.effective_packets = effective_packets
        record.linearly_dependent_packets = linearly_dependent_packets
        record.redundant_packets = redundant_packets
        self.insert_record(record=record, time=time)

    def get_record(self, time=0):
        if(time > len(self.data)-1):
            new_record = Record(time=time)
            self.insert_record(record=new_record, time=time)
            return new_record
        return self.data[time]

    def get_analytics(self):
        res: list[Record] = []
        for val in self.data:
            if val != None:
                res.append(val)

        return res
