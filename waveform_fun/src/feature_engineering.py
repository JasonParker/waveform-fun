import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def get_sys_bp(df):
    """ Get systolic blood pressures for a abp waveform
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame of waveform data
    
    Returns
    -------
    only_sys : list of tuples
        Location and magnitudes of systolic blood pressures
    """
    try:
        vals = df.values[:,1]
    except:
        vals = df.values[:,0]
    #try:
    #    vals = df.values[:,1]
    #except:
    peaks, _ = find_peaks(vals, height=0)
    max_values = [(i, v) for i, v in zip(df.index[peaks], vals[peaks])]
    only_sys = list()
    i = 0
    while (i+1) < len(max_values):
        if max_values[i][1] < max_values[i+1][1]:
            only_sys.append(max_values[i+1])
        else:
            only_sys.append(max_values[i])
        i += 2
        
    return only_sys

def get_dias_bp(df):
    """ Get diastolic blood pressures for a abp waveform
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame of waveform data
    
    Returns
    -------
    only_dias : list of tuples
        Location and magnitudes of systolic blood pressures
    """
    #try:
    #    vals = df.values[:,0]
    #except:
    #    vals = df.values[:,1]
    try:
        vals = df.values[:,1]
    except:
        vals = df.values[:,0]
    peaks, _ = find_peaks(1 / vals)
    max_values = [(i, v) for i, v in zip(df.index[peaks], vals[peaks])]
    only_dias = list()
    i = 0
    while (i+1) < len(max_values):
        if max_values[i][1] < max_values[i+1][1]:
            only_dias.append(max_values[i+1])
        else:
            only_dias.append(max_values[i])
        i += 2
        
    return only_dias

def calc_map(sys, dias):
    """Calculate mean arterial blood pressure
    
    Assumes the equation: (SBPS + 2 x DBPS) / 3
    """
    sbps = np.array([i[1] for i in sys])
    dbps = np.array([i[1] for i in dias])
    
    sidx = np.array([i[0] for i in sys])
    didx = np.array([i[0] for i in dias])
    
    maps = (sbps + 2*dbps) / 3
    indices = np.mean([sidx, didx], axis=0)
    
    return indices, maps

def format_df(df, record, t0):
    """ Format df
    """
    df["time"] = df.index * 0.008 # from 8 ms to 1 s
    df["ts"] = df["time"].apply(lambda x: record["waveform_record"]["base_datetime"] \
                                + datetime.timedelta(seconds=x))

    df["age"] = record["raw_data"]["Age"]
    df["sex"] = record["raw_data"]["Sex"]
    df["clinical"] = record["raw_data"]["Clinical"]

    surrogate = t0[record["raw_data"]["Wave"]]
    df["before_t0"] = df["ts"].apply(lambda x: x < surrogate)

    #name = df["clinical"]
    #if not os.path.isdir("data/mimic2db"):
    #    os.mkdir("data/mimic2db")
    #fs.get(f'{bucket_name}/mimic2cdb/{name}/{name}.txt', f'data/mimic2db/{name}/{name}.txt')

    #clinical = parse_txt(f"data/mimic2db/{name}/{name}.txt")

    return df
