import json
import pandas as pd
from os import listdir
from time import ctime, time
from typing import Optional


def hexstr_matches(data: str, inj: Optional[str]) -> bool:
    """Returns whether captured hex string matches injected string
    (injected string uses 'X' as wildcard).
    """
    if inj is None:
        return True  # always match for no injected string
    if len(inj) != len(data):
        return False
    # match every char, wildcard in inj always matches
    wildcard = "X"
    for i in range(len(data)):
        if inj[i] != wildcard and inj[i] != data[i]:
            return False
    return True


def pairs_list(s: str) -> list[str]:
    """Converts string to list, where each element has 2 letters. If the
    length of the string is odd, truncates the last letter.
    """
    lst = []
    for i in range(1, len(s), 2):
        lst.append(s[i-1] + s[i])
    return lst


def within_interval(timestamp: float, interval: Optional[tuple[float, float]]) -> bool:
    """Returns whether timestamp is within start/end interval, inclusive.
    If the interval is None, returns True.
    """
    if interval is None:
        return True
    return interval[0] <= timestamp <= interval[1]


def get_attack_label_OLD(attack_name: str) -> str:
    """Defines the Labels for attacks.
    NOTE: this was used for the original labels, but we determined that the
    original labels were too specific and not very useful. See the
    updated get_attack_label function for better labels.
    """
    labels = {"accelerator": "Accelerator",
           "fuzzing": "Fuzzing",
           "correlated_signal": "CorrelatedSignal",
           "max_engine_coolant_temp": "MaxEngineCoolantTemp",
           "max_speedometer": "MaxSpeedometer",
           "reverse_light": "ReverseLight"}
    # each attack name is expected to contain exactly one of the keys
    for k in labels.keys():
        if k in attack_name:
            return labels[k]
    # attacks should all be in the dict of labels
    raise ValueError("unexpected attack type")


def get_attack_label(attack_name: str) -> str:
    """Defines the Labels for attacks based on the name of the file."""
    if "accelerator" in attack_name:
        return "Accelerator"
    elif "fuzzing" in attack_name:
        return "Fuzzing"
    elif "masquerade" in attack_name:
        return "Masquerade"
    else:
        # label the rest as fabrication
        return "Fabrication"


def get_inj_id(inj_id: Optional[str]) -> Optional[str]:
    """Returns processed injection id:
    either a string with exactly 3 chars or None.
    """
    # original injection_id was a string starting with "0x" followed by up to 3 hex letters, "XXX", or None
    if inj_id is None:
        return None
    if inj_id[0] != "X":
        inj_id = inj_id[2:]  # remove leading "0x"
        if len(inj_id) < 3:
            inj_id = "0" * (3 - len(inj_id)) + inj_id  # pad to 3 chars with zeroes
    # capitalize all letters to match ids in log files
    return inj_id.upper()


def convert_attack_to_csv(infile: str, outfile: str, features: list, metadata: dict, attack_name: str) -> pd.DataFrame:
    """Converts the ROAD dataset .log files for attacks into .csv files."""
    df = pd.DataFrame(columns=features)

    # Label for the type of attack in this file, based on name of attack file
    attack_label = get_attack_label(attack_name)
    # injected data: an 8-byte hex string or None
    inj_data = metadata["injection_data_str"]
    if inj_data is not None:
        inj_data = inj_data.upper()
    inj_id = get_inj_id(metadata["injection_id"])

    inj_interval = metadata["injection_interval"]
    found_inj_interval = True if inj_interval is None else False

    count = 0
    with open(infile, "r") as file:
        for line in file:
            capture = line.strip().split()
            # adjust start and end intervals to compare with capture time
            if not found_inj_interval:
                offset = float(capture[0][1:-1])  # time of first capture
                print("offset:", offset)
                inj_interval = (metadata["injection_interval"][0] + offset,
                                metadata["injection_interval"][1] + offset)
                print("adjusted attack interval:", inj_interval)
                found_inj_interval = True

            cap_time = float(capture[0][1:-1])  # timestamp of capture
            cap_id = capture[2][0:3]  # CAN bus Arbitration ID
            cap_bytes = capture[2][4:]  # contents of 8-byte data field
            # row for this capture contains timestamp (to 6 decimals), id, and the 8 bytes
            row = [f"{cap_time:.6f}", cap_id] + pairs_list(cap_bytes)

            if hexstr_matches(cap_id, inj=inj_id) and hexstr_matches(cap_bytes, inj=inj_data) and within_interval(cap_time, inj_interval):
                # label as attack
                row.append(attack_label)
            else:
                # label as benign
                row.append("Benign")
            df.loc[len(df)] = row  # append processed data to dataframe

            count += 1
            if count % 10000 == 0:
                print("finished {c} lines at {s} ({t})".format(c=count, s=time(), t=ctime()))

    # output
    df.to_csv(outfile, index=False)
    print("converted {i} to {o}".format(i=infile, o=outfile))
    return df


def convert_ambient_to_csv(infile: str, outfile: str, features: list) -> pd.DataFrame:
    """Converts ROAD dataset ambient .log files into .csv files."""
    df = pd.DataFrame(columns=features)

    count = 0
    with open(infile, "r") as file:
        for line in file:
            capture = line.strip().split()
            cap_time = float(capture[0][1:-1])  # timestamp of capture
            cap_id = capture[2][0:3]  # CAN bus Arbitration ID
            cap_bytes = capture[2][4:]  # contents of 8-byte data field
            # row for this capture contains timestamp (6 decimals), id, and the 8 bytes
            row = [f"{cap_time:.6f}", cap_id] + pairs_list(cap_bytes)

            row.append("Benign")  # label as benign, all ambient captures are benign
            df.loc[len(df)] = row  # append processed data to dataframe

            count += 1
            if count % 10000 == 0:
                print("finished {c} lines at {s} ({t})".format(c=count, s=time(), t=ctime()))

    # output
    df.to_csv(outfile, index=False)
    print("converted {i} to {o}".format(i=infile, o=outfile))
    return df


def logs_to_csvs():
    """Converts .log files in the ROAD dataset to .csv files.
    Skips files if already present in the out directory.
    """
    ambient_in_path = "road-dataset/ambient/"
    ambient_out_path = "processed-road/ambient/"
    attack_in_path = "road-dataset/attacks/"
    attack_out_path = "processed-road/attacks/"

    features = ["Time", "Id", "Byte1", "Byte2", "Byte3", "Byte4",
            "Byte5", "Byte6", "Byte7", "Byte8", "Label"]

    # convert the attack log files to csv
    attacks_finished = listdir(attack_out_path)
    with open(attack_in_path + "capture_metadata.json", "r") as f:
        metadata = json.load(f)
        for file in metadata.keys():
            if file + ".csv" in attacks_finished:
                print("skipping {f}".format(f=file))
            else:
                print("starting {f}...".format(f=file))
                convert_attack_to_csv(attack_in_path + file + ".log",
                                      attack_out_path + file + ".csv",
                                      features,
                                      metadata[file],
                                      file)
            print()
    print("\n\nfinished converting attack logs to csv\n\n")

    # uncomment this to convert the ambient log files to csv (this part is not tested)
    # ambient_finished = listdir(ambient_out_path)
    # with open(ambient_in_path + "capture_metadata.json", "r") as f:
    #     metadata = json.load(f)
    #     for file in metadata.keys():
    #         if file + ".csv" in ambient_finished:
    #             print("skipping {f}".format(f=file))
    #         else:
    #             print("starting {f}...".format(f=file))
    #             convert_ambient_to_csv(ambient_in_path + file + ".log",
    #                                    ambient_out_path + file + ".csv",
    #                                    features)
    #         print()
    # print("\n\nfinished converting ambient logs to csv\n\n")


def combine_csvs():
    """Combines .csv files that all have the same columns
    into one .csv file.
    """
    # https://stackoverflow.com/a/69514652

    in_dirs = ["processed-road/attacks/"]  # just do attacks (include "processed-road/ambient/" in the list to also do ambient)
    out_dir = "processed-road/"
    out_file = "road.csv"

    write_header = True
    for d in in_dirs:
        print("\n\ncombining csvs in {d}...\n\n".format(d=d))
        for file in listdir(d):
            file = d + file  # relative path to file
            if file.endswith(".csv"):
                print("working on {f}".format(f=file))
                df = pd.read_csv(file)
                # append to outfile
                df.to_csv(out_dir + out_file, mode="a",
                          index=False,
                          header=write_header)
                print("appended data from {i} to {o}\n".format(i=file, o=out_dir + out_file))
                write_header = False  # only write header once
        print("\n\nfinished combining csvs in {d}\n\n".format(d=d))


def main():
    # currently, this is set up to convert attack .log files to .csv,
    # see the function implementations to also include ambient data
    logs_to_csvs()
    combine_csvs()


if __name__ == '__main__':
    main()
