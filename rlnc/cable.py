import simpy


from numpy.random import default_rng
import numpy as np


def apply_loss_to_packets(packets: list, loss_rate=0, loss_mode="constant", exponential_loss_param=0.05):
    number_of_packets = len(packets)

    if(loss_mode == "constant"):
        applied_loss_rate = loss_rate
    elif(loss_mode == "exponential"):
        applied_loss_rate = np.round((
            2**(exponential_loss_param*number_of_packets)-1)/100, 3)
    elif(loss_mode == "ge"):
        probability = np.random.uniform(0, 1)
        if(probability >= 0.2):
            applied_loss_rate = 0
        else:
            applied_loss_rate = 1

    if(applied_loss_rate > 1):
        applied_loss_rate = 1
    number_of_lost_packets = int(np.ceil(number_of_packets*applied_loss_rate))

    if(len(packets) == 0):
        return []
    if(number_of_lost_packets == number_of_packets and applied_loss_rate < 1):
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
    return result, applied_loss_rate


class Cable(object):
    def __init__(self, env, delay, loss_rate=0, loss_mode="constant", exponential_loss_param=0.05):
        self.env = env
        self.delay = delay
        self.loss_rate = loss_rate
        self.store = simpy.Store(env)
        self.loss_mode = loss_mode  # constant or exponential
        self.exponential_loss_param = exponential_loss_param

    def latency(self, value):
        yield self.env.timeout(self.delay)
        self.store.put(value)

    def put(self, value, loss_rate=None):
        loss_applied_packets, applied_loss_rate = apply_loss_to_packets(
            value, loss_rate=loss_rate or self.loss_rate,
            loss_mode=self.loss_mode,
            exponential_loss_param=self.exponential_loss_param)
        print('@@@ cable loss rate:', applied_loss_rate, ', time:', self.env.now)
        self.env.process(self.latency(loss_applied_packets))
        return applied_loss_rate

    # TEMPORARY: separate from put to insure reliable delivery (no loss)
    def put_response(self, value):
        self.env.process(self.latency(value))

    def get(self):
        return self.store.get()
