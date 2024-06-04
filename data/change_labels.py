# We determined that the last four of original labels (Benign, Accelerator, Fuzzing,
# CorrelatedSignal, MaxEngineCoolantTemp, MaxSpeedometer, ReverseLight)
# were too specific and not very useful. Here, we iterate through the original
# files and change the labels to: Benign, Accelerator, Fuzzing, Fabrication, Masquerade.
# The original road_work.py code should produce these new labels
# (we updated the get_attack_label function), but we didn't test it with the new labels
# because it takes several nights to run (on a 2019 MacBook Pro).


from os import listdir
import pandas as pd


def main():
    in_path = "processed-road-old-labels/attacks/"
    out_path = "processed-road/attacks/"

    for file in listdir(in_path):
        if file.endswith(".csv"):
            print("cooking {f}...".format(f=file))
            df = pd.read_csv(in_path + file)
            if "accelerator" in file or "fuzzing" in file:
                # keep "Accelerator" and "Fuzzing" labels from old system
                pass
            elif "masquerade" in file:
                # for files with "masquerade" in the name,
                # labels were either "Benign" or a type of attack.
                # change non-benign labels to "Masquerade"
                df.loc[df["Label"] != "Benign", ["Label"]] = "Masquerade"
            else:
                # label the rest as "Fabrication"
                df.loc[df["Label"] != "Benign", ["Label"]] = "Fabrication"
            a = df.loc[df["Label"] != "Benign"]
            print("there are {n} rows that are not benign".format(n=len(a)))
            print(a, "\n\n")
            # write df to new file
            df.to_csv(out_path + file, mode="w", index=False, header=True)


if __name__ == '__main__':
    main()
