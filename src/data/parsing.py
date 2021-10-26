import pandas as pd

def parse_txt(txt_file):
    """Parse mimic txt file
    Parameters
    ----------
    txt_file: str
        Path to txt_file

    Returns
    -------
    df: pd.DataFrame
        Dataframe of clinical data
    """
    with open(txt_file) as f:
        lines = f.readlines()
    event_dict = dict()
    for idx, line in enumerate(lines):   
        splits = line.split("\t")
        event_dict[idx] = {"ts": splits[0]}
        event_dict[idx]["event"] = splits[1]
        rest = splits[2:]
        for column in rest:
            column_name, column_value = column.split("=")
            event_dict[idx][column_name] = column_value.split("\n")[0]
    df = pd.DataFrame.from_dict(event_dict, orient="index")

    return df