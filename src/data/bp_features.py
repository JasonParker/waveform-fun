import pandas as pd
import numpy as np
from scipy.signal import find_peaks
from dateutil.rrule import rrule, SECONDLY
from datetime import timedelta

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

def clean_bp_summary(df):
    good_sys = df['avg_sys'] >= 30 & df['avg_sys'].notnull()
    good_dias = df['avg_dias'] >= 10 & df['avg_dias'].notnull()
    has_outcome = df['hypotensive_in_15'].notnull()
    print('cleaning data')
    df['include_in_model'] = np.where(good_sys & good_dias & has_outcome, 1, 0)
    
    return df


def create_lookback(df, time=1):
    """Create lookback windows for each row
    time is in minutes
    """
    time_diff = df.iloc[1].start_window_time - df.iloc[0].start_window_time
    time_diff = time_diff.seconds / 60 # Conversion from s to min.
    if time_diff > time:
        raise ValueError("Lookback window time must be greater or equal to the time windows")
    n_skips = time / time_diff  # Example: lookback is 10 minutes, window of 5: 10 / 5 = look back two windows

    lb_array = np.zeros(df.shape[0])
    for index, row in df.iterrows():
        lb_idx = int(index - n_skips)
        if lb_idx < min(df.index):
            lb_array[index] = None
        else:
            lookback = df.iloc[lb_idx]
            lb_array[index] = lookback["avg_map"]

    df[f"lb_{time}_map"] = lb_array

    return df



def avg_bp(df, time_chunk, time_window = 60,waveform_type = 'ABP'):
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
    x = df[[waveform_type]]
    start_window = df.index[0]
    start_window_time = df.loc[start_window,'ts']
    print(start_window_time)
    end_window = df.index[-1]
    end_window_time = df.loc[end_window,'ts']
    print(end_window_time)
    print(type(end_window_time))
    time_window = (time_window * 1000) // 8
    time_chunk = (time_chunk * 1000) // 8
    new_df = []#pd.DataFrame(columns = ['wave', 'start_window', 'end_window', 'avg_sys','avg_dias','avg_map', 'all_values'])
    for cur_time in range(start_window + time_chunk, end_window, time_window):     
    #for cur_time in rrule(freq = SECONDLY, interval = time_window, 
    #                      dtstart = start_window_time + timedelta(seconds = time_chunk),until = end_window_time):
        print(cur_time)
        #print(new_df.shape)
        #df_sub =  df[(df.index >= (cur_time - time_chunk)) & (df.index < cur_time)]
        x_sub = df_sub.loc[cur_time - time_chunk : cur_time, waveform_type]
        #x_sub = df_sub[[waveform_type]]
        sys_pressure = get_sys_bp(x_sub)
        dias_pressure = get_dias_bp(x_sub)
        avg_sys = np.nanmean([x[1] for x in sys_pressure])
        avg_dias = np.nanmean([x[1] for x in dias_pressure])
        avg_maps = (avg_sys + 2 * (avg_dias))/3
        #print(df_sub.loc[cur_window-time_chunk,'ts'])
        all_values = x_sub[waveform_type].to_numpy()
        #print(df_sub.head())
        try:
            cur_row = pd.DataFrame(data = {'wave': [df["wave"].values[0]], 'start_window':[df_sub.index[0]],
                                           'start_window_time':[start_window_time],
                                       'end_window':[df_sub.index[-1]], 'end_window_time':[end_window_time],
                                       'avg_sys':[avg_sys], 'avg_dias':[avg_dias], 'avg_map':[avg_maps],'all_values': [all_values]})
        except KeyError:
            continue
        #print(cur_row)
        new_df.append(cur_row)
        
    new_df = pd.concat(new_df, axis = 0)
    new_df = new_df.sort_values('start_window')
    new_df = new_df.reset_index()
    try:
        new_df = new_df[['wave', 'start_window', 'end_window','start_window_time','end_window_time',
                     'avg_sys', 'avg_dias','avg_map','all_values']]
        new_df['current_hypotensive'] = np.where(new_df['avg_map'] <= 65, 1,0)
        new_df['hypotensive_in_15'] = new_df['current_hypotensive'].shift(periods=-15)
        print('going to clean data')
        new_df = clean_bp_summary(new_df)
        return new_df
    except KeyError:
        return None

  
