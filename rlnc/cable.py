import simpy
import numpy as np


class Cable(object):
    def __init__(self, env, delay, loss_rate=0, loss_mode="constant",
                 exponential_loss_param=0.05,
                 ge_loss_good_to_bad=0.027,
                 ge_loss_bad_to_good=0.25,
                 ee_loss_error=0.25, seed=42):
        self.env = env
        self.delay = delay
        self.loss_rate = loss_rate
        self.store = simpy.Store(env)
        self.loss_mode = loss_mode  # constant or exponential
        self.exponential_loss_param = exponential_loss_param
        self.ge_loss_good_to_bad = ge_loss_good_to_bad
        self.ge_loss_bad_to_good = ge_loss_bad_to_good
        self.ee_loss_error = ee_loss_error
        self.gilbert_elliot_state = 'good'  # 'good' or 'bad' or 'error'
        self.packets_rnd_state = np.random.default_rng(seed=seed)
        self.probability_rnd_state = np.random.RandomState(seed)

    def latency(self, value, delay):
        yield self.env.timeout(delay)
        self.store.put(value)

    def put(self, value, loss_rate=None):
        loss_applied_packets, applied_loss_rate = self.apply_loss_to_packets(
            value, loss_rate=loss_rate or self.loss_rate)
        print('@@@ cable loss rate:', applied_loss_rate, ', time:', self.env.now)

        self.env.process(self.latency(loss_applied_packets, delay=self.delay))
        return applied_loss_rate

    # TEMPORARY: separate from put to insure reliable delivery (no loss)
    def put_response(self, value):
        self.env.process(self.latency(value, delay=1))

    def get(self):
        return self.store.get()

    def apply_loss_to_packets(self, packets: list, loss_rate=0):
        number_of_packets = len(packets)

        if(self.loss_mode == "constant"):
            applied_loss_rate = loss_rate
        elif(self.loss_mode == "exponential"):
            applied_loss_rate = np.round((
                2**(self.exponential_loss_param*number_of_packets)-1)/100, 3)
        elif(self.loss_mode == "ge"):
            probability = self.probability_rnd_state.uniform(0, 1)
            if(self.gilbert_elliot_state == 'good'):
                if(probability <= self.ge_loss_good_to_bad):
                    self.gilbert_elliot_state = 'bad'
                    applied_loss_rate = 1
                else:
                    applied_loss_rate = 0
            elif(self.gilbert_elliot_state == 'bad'):
                if(probability <= self.ge_loss_bad_to_good):
                    self.gilbert_elliot_state = 'good'
                    applied_loss_rate = 0
                else:
                    applied_loss_rate = 1
        elif(self.loss_mode == "ee"):
            probability = self.probability_rnd_state.uniform(0, 1)
            if(self.gilbert_elliot_state == 'good'):
                if(probability <= self.ge_loss_good_to_bad):
                    self.gilbert_elliot_state = 'bad'
                    applied_loss_rate = 1
                elif(probability > self.ge_loss_good_to_bad and
                     probability <= self.ge_loss_good_to_bad + self.ee_loss_error):
                    self.gilbert_elliot_state = 'error'
                    applied_loss_rate = loss_rate
                else:
                    applied_loss_rate = 0
            elif(self.gilbert_elliot_state == 'bad'):
                if(probability <= self.ge_loss_bad_to_good):
                    self.gilbert_elliot_state = 'good'
                    applied_loss_rate = 0
                elif(probability > self.ge_loss_bad_to_good and
                     probability <= self.ge_loss_bad_to_good + self.ee_loss_error):
                    self.gilbert_elliot_state = 'error'
                    applied_loss_rate = loss_rate
                else:
                    applied_loss_rate = 1
            elif(self.gilbert_elliot_state == 'error'):
                if(probability <= self.ge_loss_bad_to_good):
                    self.gilbert_elliot_state = 'good'
                    applied_loss_rate = 0
                elif(probability > self.ge_loss_bad_to_good and
                     probability <= self.ge_loss_bad_to_good + self.ge_loss_good_to_bad):
                    self.gilbert_elliot_state = 'bad'
                    applied_loss_rate = 1
                else:
                    applied_loss_rate = loss_rate

        if(applied_loss_rate > 1):
            applied_loss_rate = 1
        number_of_lost_packets = int(
            np.ceil(number_of_packets*applied_loss_rate))

        if(len(packets) == 0):
            return []
        if(number_of_lost_packets == number_of_packets and applied_loss_rate < 1):
            # in case of one packet
            number_of_lost_packets = number_of_lost_packets - 1

        lost_packets_index = self.packets_rnd_state.choice(
            number_of_packets, size=number_of_lost_packets, replace=False)
        result = []
        for index, packet in enumerate(packets):
            if(index not in lost_packets_index):
                result = result + [packet]
        return result, applied_loss_rate
