from typing import List
import os
from datetime import datetime

from src.log import CSVLog
from src.sim import Sim

readme = """
About this simulation:

n_buses: N_BUSES
n_runs: N_RUNS
n_steps: N_STEPS
"""


def run(n_buses: List[int], n_runs: int, n_steps: int):
    path = os.path.join("data", f"sim_" + str(datetime.now()).replace(" ", "_"))
    os.makedirs(path)

    with open(os.path.join(path, "readme.txt"), "a") as f:
        f.write(readme
                .replace("N_BUSES", str(n_buses))
                .replace("N_RUNS", str(n_runs))
                .replace("N_STEPS", str(n_steps)))

    for bus_i in n_buses:
        for run_i in range(n_runs):
            sim = Sim(n_buses=bus_i, log=CSVLog(path=path, msg=f"{bus_i}buses_#{run_i}_"))
            sim.run(n_steps)


if __name__ == "__main__":
    run(n_buses=[15], n_runs=1, n_steps=10000)
