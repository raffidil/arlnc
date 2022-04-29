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
generation_size = 16  # number of packets in a gen
packet_size = 1024  # bytes
total_size = generation_size * packet_size

GF = galois.GF(field_order, display="int")

packet_matrix = create_packet_matrix(total_size, packet_size)
coefficient_matrix = create_random_coefficient_matrix(3)
coded_matrix = create_coded_packet_matrix(coefficient_matrix, packet_matrix)

print("packets:\n ", packet_matrix, "\n")
print("coefficients:\n ", coefficient_matrix, "\n")
print("coded packets:\n ", coded_matrix, "\n")

# remove last 3 packet during the transmission
received_systematic_packets = packet_matrix[0:14, :]
# assume that the all coded packets received successfully
received_coded_packets = coded_matrix[:, :]
received_coefficients_matrix = coefficient_matrix[:, :]

received_systematic_packets_count = np.shape(
    received_systematic_packets)[0]
received_coded_packets_count = np.shape(
    received_coded_packets)[0]

redundant_packet_margin = (
    received_systematic_packets_count + received_coded_packets_count) - generation_size

if(redundant_packet_margin > 0):
    received_coded_packets = received_coded_packets[0:len(
        received_coded_packets)-redundant_packet_margin, :]
    received_coefficients_matrix = received_coefficients_matrix[0:len(
        received_coefficients_matrix)-redundant_packet_margin, :]

received_packets = GF(np.concatenate(
    (received_systematic_packets, received_coded_packets)))
received_coefficients = GF(np.concatenate(
    (GF(np.eye(received_systematic_packets_count, generation_size, dtype="int")), received_coefficients_matrix)))


received_coefficients_rank = np.linalg.matrix_rank(received_coefficients)
print("received coef. rank:", received_coefficients_rank)

if(received_coefficients_rank == generation_size):
    x = np.linalg.solve(received_coefficients, received_packets)
    print("\nrecovered packets:\n ", x)
    print("\nData size: ", total_size, " byte")
    print("\nPacket size: ", packet_size, " byte")
    print("\nWare all packets recovered? ",
          np.array_equal(x, packet_matrix))
else:
    print("\n\nERROR: not enough information to decode the original packet!\n")
    print("required additional coded packets: ",
          generation_size-received_coefficients_rank)
