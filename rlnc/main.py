
from block_based_rlnc import BlockBasedRLNC

base_config = dict(field_order=2**8, generation_size=16,
                   packet_size=16, total_size=1024*32,
                   initial_redundancy=1, initial_window_size=1,
                   ge_loss_good_to_bad=0.05, ge_loss_bad_to_good=0.2,
                   exponential_loss_param=0.045,
                   ee_loss_error=0.10, seed=24,
                   force_to_recreate_new_data=True)


config = dict(loss_mode="exponential", approach="arlnc")

applied_config = base_config | config

rlnc = BlockBasedRLNC(**applied_config)

data = rlnc.run_simulation()
