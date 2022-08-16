import pandas as pd


class Record:
    def __init__(self, time,
                 type=None,
                 redundancy=None,
                 window_size=None,
                 generation_window=None,
                 average_feedback=None,
                 generation_size=None,
                 loss_rate=None,
                 new_coded_packets_count=0,
                 extra_packets_count=0,
                 total_sent_packets=0,
                 coded_packets_count=0,
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
        self.average_feedback = average_feedback
        self.generation_size = generation_size
        self.loss_rate = loss_rate
        self.new_coded_packets_count = new_coded_packets_count
        self.extra_packets_count = extra_packets_count
        self.total_sent_packets = total_sent_packets
        self.received_packets = received_packets
        self.effective_packets = effective_packets
        self.linearly_dependent_packets = linearly_dependent_packets
        self.redundant_packets = redundant_packets
        self.coded_packets_count = coded_packets_count

    def to_dict(self):
        return {
            'time': self.time,
            'type': self.type,
            'redundancy': self.redundancy,
            'window size': self.window_size,
            'generation window': self.generation_window,
            'average feedback': self.average_feedback,
            'generation size': self.generation_size,
            'loss rate': self.loss_rate,
            'new coded packets count': self.new_coded_packets_count,
            'extra packets count': self.extra_packets_count,
            'total sent packets': self.total_sent_packets,
            'received packets': self.received_packets,
            'effective packets': self.effective_packets,
            'linearly dependent packets': self.linearly_dependent_packets,
            'redundant packets': self.redundant_packets,
            'coded packets count': self.coded_packets_count
        }


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
              average_feedback=None,  # average_redundancy
              generation_size=None,
              loss_rate=None,
              new_coded_packets_count=0,
              extra_packets_count=0,
              total_sent_packets=0,
              coded_packets_count=0,
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
        record.average_feedback = average_feedback
        record.generation_size = generation_size
        record.loss_rate = loss_rate
        record.new_coded_packets_count = new_coded_packets_count
        record.extra_packets_count = extra_packets_count
        record.total_sent_packets = total_sent_packets
        record.received_packets = received_packets
        record.effective_packets = effective_packets
        record.linearly_dependent_packets = linearly_dependent_packets
        record.redundant_packets = redundant_packets
        record.coded_packets_count = coded_packets_count
        self.insert_record(record=record, time=time)

    def get_record(self, time=0):
        if(time > len(self.data)-1):
            new_record = Record(time=time)
            self.insert_record(record=new_record, time=time)
            return new_record
        return self.data[time]

    def get_data(self):
        result: list[Record] = []
        for val in self.data:
            if val != None:
                result.append(val)

        return result

    def get_analytics_data_frame(self):
        data = self.get_data()
        df = pd.DataFrame.from_records(
            [record.to_dict() for record in data])
        return df
