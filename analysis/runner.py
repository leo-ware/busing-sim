from typing import List
import os
from datetime import datetime
from time import time

from src.log import CSVLog, LogFilter
from src.sim import Sim
from src.actions import BUS_MOVE

readme = """
About this simulation:

n_buses: N_BUSES
n_runs: N_RUNS
n_steps: N_STEPS
"""


def run(n_buses: List[int], n_runs: int, sim_duration: int):
    start_time = time()

    path = os.path.join("data", f"sim_" + str(datetime.now()).replace(" ", "_"))
    os.makedirs(path)

    with open(os.path.join(path, "readme.txt"), "a") as f:
        f.write(readme
                .replace("N_BUSES", str(n_buses))
                .replace("N_RUNS", str(n_runs))
                .replace("SIM_DURATION", str(sim_duration)))

    for bus_i in n_buses:
        for run_i in range(n_runs):

            log=CSVLog(path=path, msg=f"{bus_i}_{run_i}")
            log = LogFilter(log, keep=lambda r: r.action != BUS_MOVE)

            sim = Sim(n_buses=bus_i, log=log)
            sim.run(stop_time=sim_duration)
    
    print(f"success! run completed in {(time() - start_time)/60} minutes")


if __name__ == "__main__":
    run(n_buses=[5], n_runs=1, sim_duration=2*60)
