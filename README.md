# Block Based RLNC simulator for Ms.c. thesis

This repository contains the block based rlnc message passing protocol based on systematic encoding. The code redundancy and generation window size is adjusting with a specific algorithm which is based on receiver's ACK.

The implementation is in Python and the simulation uses `simpy`, a discrete-event simulation tool for python.

### Installation

1. Clone the repository

1. `cd` into `rlnc` directory

1. install the dependencies

```bash
pip install -r requirements.txt
```

### Usage

You can run the simulation simply by running `main.py`.

```bash
python main.py
```

All configuration can be passed to the simulation as parameters for `BlockBasedRLNC` class constructor.

### Example

```python
from block_based_rlnc import BlockBasedRLNC

simulation = BlockBasedRLNC(
                field_order=2**8, generation_size=16,
                packet_size=16, total_size=1024*32,
                initial_redundancy=1, initial_window_size=1,
                ge_loss_good_to_bad=0.05, ge_loss_bad_to_good=0.2,
                exponential_loss_param=0.045,
                loss_rate=0.15, ee_loss_error=0.25, seed=2,
                force_to_recreate_new_data=True,
                loss_mode="ge", approach="arlnc")

data = simulation.run_simulation()

```

Example of visualization of the results can be found in `rlnc/report.ipynb` jupyter notebook.
