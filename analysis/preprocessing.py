import pandas as pd
import numpy as np

from src.actions import *


def preprocess(df_raw):
    # type coercion
    for col in ["object_type", "action", "status"]:
        df_raw[col] = df_raw[col].astype("category")
    df_raw["data"] = pd.to_numeric(df_raw["data"].replace("None", ""))

    # there are two copies of each event, one logged on dispath and one logged on completion
    # we want to merge these together
    dispatched = (df_raw[df_raw["status"] == "DISPATCHED"]
        .rename(columns={"time": "dispatch_time", "data": "dispatch_data"})
        .drop("status", axis=1))

    # just take event_id and time from this one
    finished = (df_raw[df_raw["status"] == "FINISHED"][["event_id", "time", "data"]]
        .rename(columns={"time": "finish_time", "data": "cb_data"}))

    # merge them back together to get start and end times for every event
    df = pd.merge(dispatched, finished, how="left", on="event_id")
    
    # calculate duration column
    df['duration'] = df['finish_time'] - df['dispatch_time']

    # drop events that were in progress when the sim ended
    df = df[df["finish_time"].notna()]

    # reorder columns
    df = df[["event_id", "action", "object_type", "object_id", "dispatch_time", "finish_time", "duration", "dispatch_data", "cb_data"]]

    return df


def ignore_burnin(df, mins):
    """Remove any events that were dispatched before some time
    
    Args:
        df: a pandas dataframe, output of the `preprocess` function
        mins: the new start of history
    """
    return df[df["dispatch_time"] > mins]


def max_queue_len(df):
    """Finds the longest queue length that occured during the sim
    
    Args:
        df: a pandas dataframe, output of the `preprocess` function
    """
    return np.max(df[df["action"] == STOP_PASSENGER_JOIN]["cb_data"])


def make_passenger_df(df):
    """Computes relevant statistics for each passenger in the sim and makes a dataframe
    
    Args:
        df: a pandas dataframe, output of the `preprocess` function
    """
    transit_times = (df
        [df["action"] == PASSENGER_DISEMBARK]
        [["object_id", "dispatch_data", "cb_data"]]
        .rename(columns={"dispatch_data": "stops_traveling", "cb_data": "transit_duration"})
    )

    # Combines information from two different kinds of actions for each passenger
    # resulting in a dataframe that knows when the passenger joined the queue and when they sat down
    # on the bus
    wait_times = pd.merge(
        df[df["action"] == PASSENGER_JOIN_QUEUE][["object_id", "dispatch_time"]]
            .rename(columns={"dispatch_time": "queue_time"}),
        df[df["action"] == PASSENGER_EMBARK][["object_id", "finish_time"]]
            .rename(columns={"finish_time": "seated_time"}),
        on="object_id"
    )

    # the information we actually want -- the time they spent waiting
    wait_times["wait_duration"] = wait_times["seated_time"] - wait_times["queue_time"]
    wait_times = wait_times.drop(["queue_time"], axis=1)

    # combine all our information about each passenger
    new = pd.merge(transit_times, wait_times, on="object_id")
    new["wait_transit_ratio"] = new["wait_duration"]/new["transit_duration"]

    # reorder columns and return
    return new[["object_id", "stops_traveling", "seated_time", "wait_duration", "transit_duration", "wait_transit_ratio"]]
