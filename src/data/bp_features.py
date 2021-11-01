import pandas as pd
import numpy as np
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
        vals = df.values[:,0]
    except:
        vals = df.values[:,1]
    peaks, _ = find_peaks(vals)
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
    try:
        vals = df.values[:,0]
    except:
        vals = df.values[:,1]
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
    #print(only_dias)
        
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


def avg_bp(x, time_chunk, time_window = 60,waveform_type = 'ABP'):
    """ Get diastolic blood pressures for a abp waveform
    
    Parameters
    ----------
    x : pd.DataFrame
        DataFrame of waveform data
        
    time_chunk: int
        number of seconds that waveform will be averaged over
        
    time_window: int
        number of seconds between each average
        
    waveform_type: str
        column of interest for waveform in primary dataframe to pull the waveform data from
    
    Returns
    -------
    new_df : pd.Dataframe
        dataframe with data about each average bp
        
        columns:
            start_window : index of start of average
            end_window : index of end of average
            avg_sys : average systolic pressure over time chunk
            avg_dias : average diastolic pressure over time chunk
            avg_map : average mean arterial pressure over time chunk
        
    """
    x = x[[waveform_type]]
    start_window = x.index[0]
    end_window = x.index[-1]
    time_window = (time_window * 1000) // 8
    time_chunk = (time_chunk * 1000) // 8
    new_df = pd.DataFrame(columns = ['start_window', 'end_window', 'avg_sys','avg_dias','avg_map', 'all_values'])
    for cur_window in range(start_window + time_chunk, end_window, time_window):
        
        x_sub = x.loc[cur_window-time_chunk:cur_window]
        sys_pressure = get_sys_bp(x_sub)
        dias_pressure = get_dias_bp(x_sub)
        avg_sys = np.mean([x[1] for x in sys_pressure])
        avg_dias = np.mean([x[1] for x in dias_pressure])
        avg_maps = (avg_sys + 2 * (avg_dias))/3
        print(x_sub.tolist())
        all_values = np.array(x_sub.tolist())
        cur_row = pd.DataFrame(data = {'start_window':[cur_window-time_chunk], 'end_window':[cur_window], 
                                       'avg_sys':[avg_sys], 'avg_dias':[avg_dias], 'avg_map':[avg_maps],'all_values':all_values})
        #print(cur_row)
        new_df = new_df.append(cur_row)
    new_df.sort_values('start_window')
    new_df = new_df.reset_index()
    new_df = new_df[['start_window', 'end_window', 'avg_sys', 'avg_dias','avg_map']]
    return new_df