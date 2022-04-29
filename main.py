import json
from numpy.linalg import matrix_rank
import numpy as np
import galois

from utils import create_random_bytestring


GF = galois.GF(2**8, display="int")


# GF8 = galois.GF(2**3, display="int")
# print(GF8.arithmetic_table("+"))
# print(GF8.arithmetic_table("-"))


# A = ([[0, 1], [2, 1]])
# b = ([20, 40])

# x = np.linalg.solve(A, b)
# print(x)


packet1 = GF([2, 52, 32, 4, 255, 67, 56, 45, 75])  # 72bit
packet2 = GF([4, 51, 46, 97, 100, 145, 34, 29, 11])  # 72bit
packet3 = GF([2, 58, 63, 62, 131, 43, 54, 65, 76])  # 72bit
packet4 = GF([5, 56, 50, 101, 119, 76, 45, 243, 250])  # 72bit
packet5 = GF([10, 59, 51, 102, 105, 54, 65, 76, 3])  # 72bit


co1 = GF([2, 1, 32, 55, 76])  # 40bit (5 packet)
co2 = GF([4, 6, 57, 3, 65])  # 40bit (5 packet)
co3 = GF([1, 22, 71, 6, 83])  # 40bit (5 packet)

coef_rank = np.linalg.matrix_rank([co1, co2, co3])
print("coef. rank:", coef_rank)

coded1 = co1[0]*packet1 + co1[1]*packet2 + co1[2] * \
    packet3 + co1[3]*packet4 + co1[4]*packet5

coded2 = co2[0]*packet1 + co2[1]*packet2 + co2[2] * \
    packet3 + co2[3]*packet4 + co2[4]*packet5

coded3 = co3[0]*packet1 + co3[1]*packet2 + co3[2] * \
    packet3 + co3[3]*packet4 + co3[4]*packet5


A = GF([[0, 1, 0, 0, 0], [0, 0, 1, 0, 0], co1, co2, co3])
b = GF([packet2, packet3, coded1, coded2, coded3])

received_coef_rank = np.linalg.matrix_rank([co1, co2, co3])
print("received coef. rank:", received_coef_rank)


x = np.linalg.solve(A, b)
print(x)

# print('coded: ', coded)  # 40bit
# # print(GF([1, 5])*GF([2, 6]))


# received1 = packet2

# print('recover packet 1: ', (coded-packet2)/GF(2))
