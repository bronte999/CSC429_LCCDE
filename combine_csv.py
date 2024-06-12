import pandas as pd

# Concats each csv to the end of the previous
def concatenate_csv_files_line_by_line(csv_files, output_csv):
    with open(output_csv, 'w') as output_file:
        for i, file in enumerate(csv_files):
            with open(file, 'r') as input_file:
                if i == 0:
                    for line in input_file:
                        output_file.write(line)
                else:
                    next(input_file)
                    for line in input_file:
                        output_file.write(line)


csv_files = [
    './Data/DoS_data.csv',
    './Data/Fuzzy_data.csv',
    './Data/Gear_data.csv',
    './Data/Normal_data.csv',
    './Data/RPM_data.csv'
]

# output_csv = './Data/combo.csv'
# concatenate_csv_files_line_by_line(csv_files, output_csv)
