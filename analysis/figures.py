from itertools import product
import matplotlib.pyplot as plt

from src.actions import *

def duration_primitive_actions(df):
    fig, axes = plt.subplots(2, 2, figsize=(10, 10))

    actions = [STOP_PASSENGER_JOIN, BUS_MOVE, PASSENGER_EMBARK, PASSENGER_DISEMBARK]
    these_axes = [axes[i, j] for i, j in product([0, 1], [0, 1])]

    for action, ax in zip(actions, these_axes):
        ax.hist(df[df["action"] == action]['duration'], bins=20)
        ax.set_title(action)
        ax.set_ylabel("# events")
        ax.set_xlabel("duration")

    fig.suptitle("Duration of Primitive Actions", size=16)
    
    return fig
