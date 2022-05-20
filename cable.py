import simpy


from numpy.random import default_rng
import numpy as np


def apply_loss_to_packets(packets: list, loss_rate=0.1):
    number_of_packets = len(packets)
    number_of_lost_packets = int(np.ceil(number_of_packets*loss_rate))
    if(number_of_lost_packets == number_of_packets and loss_rate < 1):
        # in case of one packet
        number_of_lost_packets = number_of_lost_packets - 1
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


class Cable(object):
    def __init__(self, env, delay):
        self.env = env
        self.delay = delay
        self.store = simpy.Store(env)

    def latency(self, value):
        yield self.env.timeout(self.delay)
        self.store.put(value)

    def put(self, value, loss_rate=0.1):
        loss_applied_packets = apply_loss_to_packets(value, loss_rate)
        self.env.process(self.latency(loss_applied_packets))

    # TEMPORARY: separate from put to insure reliable delivery (no loss)
    def put_response(self, value):
        self.env.process(self.latency(value))

    def get(self):
        return self.store.get()
