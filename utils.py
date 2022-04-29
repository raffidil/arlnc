from pydoc import cram
import random
import re
import numpy as np
import galois


def create_random_bytestring(total_size, packet_size):  # both in bytes
    binary_string = ""
    zero_margin = ""
    # number of zeroes required for make the created bytes mod of packet size
    required_additional_zeroes = (
        packet_size - (total_size % packet_size)) % packet_size

    for i in range(total_size * 8):
        temp = str(random.randint(0, 1))
        binary_string += temp

    for i in range(required_additional_zeroes * 8):
        zero_margin += "0"

    result = zero_margin + binary_string
    with open('output.binary', 'w') as f:
        f.write(result)
    return result


def read_random_string():
    with open('output.binary', 'r') as f:
        s = f.read()
        return s


def create_packet_matrix(total_size=64, packet_size=8):  # packet_size: byte
    binary_string = create_random_bytestring(total_size, packet_size)
    binary_data_array = re.findall('........', binary_string)
    data = []
    for i in binary_data_array:
        data = data + [int(i, 2)]
    # print(data)
    matrix = GF(np.reshape(data, (-1, packet_size)))
    return matrix


# generation size = number of systematic packets in the gen
def create_random_coefficient_vector():
    coefficient_vector = []
    for i in range(generation_size):
        temp = random.randint(0, field_order-1)
        coefficient_vector += [temp]
    return GF(np.array(coefficient_vector))


def create_random_coefficient_matrix(count=1):
    coefficient_matrix = []
    for i in range(count):
        coefficient_matrix = coefficient_matrix + \
            [create_random_coefficient_vector()]
    result = GF(np.array(coefficient_matrix))
    return result


def create_coded_packet_matrix(coefficient_matrix, packet_matrix):
    return coefficient_matrix.dot(packet_matrix)


field_order = 2**8
generation_size = 15  # number of packets in a gen
packet_size = 8  # bytes
total_size = generation_size * packet_size

GF = galois.GF(field_order, display="int")

packet_matrix = create_packet_matrix(total_size, packet_size)
coefficient_matrix = create_random_coefficient_matrix(3)
coded_matrix = create_coded_packet_matrix(coefficient_matrix, packet_matrix)

print(np.shape(coefficient_matrix))
print(np.shape(packet_matrix))

print("packets: ", packet_matrix, "\n")
print("coefficient: ", coefficient_matrix, "\n")
print("coded packets: ", coded_matrix, "\n")
