
from block_based_rlnc import BlockBasedRLNC


# rlnc = BlockBasedRLNC(field_order=2**8, generation_size=16,
#                       packet_size=16, total_size=1024*32,
#                       initial_redundancy=10, initial_window_size=4, exponential_loss_param=0.05)
# data = rlnc.run_simulation()

base_config = dict(field_order=2**8, generation_size=16,
                   packet_size=16, total_size=1024*64,
                   initial_redundancy=1, initial_window_size=1,
                   ge_loss_good_to_bad=0.05, ge_loss_bad_to_good=0.2,
                   exponential_loss_param=0.045,
                   ee_loss_error=0.25, seed=2,
                   force_to_recreate_new_data=False)

config = dict(loss_mode="ge", adjust_algorithm="none")

applied_config = base_config | config

rlnc = BlockBasedRLNC(**applied_config)

data = rlnc.run_simulation()


# for index, record in enumerate(data):
#     if(record.type == 'send'):
#         print(
#             f'time: {record.time} - SEND - loss rate: {record.loss_rate} - redundancy: {record.redundancy} - window size: {record.window_size} - new,extra,total: {record.new_coded_packets_count},{record.extra_packets_count},{record.extra_packets_count+record.new_coded_packets_count} - window: {record.generation_window}')
#     if(record.type == 'feedback'):
#         print(
#             f'time: {record.time} - FEEDBACK - avg. needed red: {record.average_feedback} - redundancy: {record.redundancy}')
#     if(record.type == 'receive'):
#         print(
#             f'time: {record.time} - RECEIVE - received: {record.received_packets} - effectiveness: {np.round(record.effective_packets/(record.received_packets),2) if record.received_packets!=0 else None} - lin. dependant: {record.linearly_dependent_packets} - redundant: {record.redundant_packets}')
# print('--- END ---')


# to do
# - prepare the whole generation if the needed is higher than generation_loss_threshold for next transmission (test with loss=0.95 and R=1)
# - add gilbert-elliot loss model as option
