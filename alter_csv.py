import pandas as pd
import csv

# Adds a new column with a specific string value
def add_column_to_csv(input_csv, output_csv, new_column_name, string_value):
    df = pd.read_csv(input_csv)
    df[new_column_name] = string_value
    df.to_csv(output_csv, index=False)


# Removes the lines with empty values
def remove_empty_lines(input_csv_path, output_csv_path):
    with open(input_csv_path, 'r', newline='') as input_file:
        reader = csv.reader(input_file)
        filtered_lines = [line for line in reader if all(field.strip() for field in line)]
    
    with open(output_csv_path, 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(filtered_lines)

# Takes the T and R and rewrites as Benign or the attack type
def process_csv(input_csv_path, output_csv_path):
    with open(input_csv_path, 'r', newline='') as input_file:
        reader = csv.reader(input_file)
        processed_lines = []

        for line in reader:
            if line[-2] == 'R':
                processed_line = line[:-2] + ["Benign"]
            elif line[-2] == 'T':
                processed_line = line[:-2] + [line[-1]]
            else:
                processed_line = line
            
            processed_lines.append(processed_line)
    
    with open(output_csv_path, 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(processed_lines)

# Pads the missing bytes to ensure consitency
def pad_missing_bytes(input_csv_path, output_csv_path):
    with open(input_csv_path, 'r', newline='') as input_file:
        reader = csv.reader(input_file)
        processed_rows = []
        for row in reader:
            try:
                label_index = row.index('R')
                label = 'R'
            except ValueError:
                label_index = row.index('T')
                label = 'T'

            for i in range(2, 9):
                val = ''
                if row[i] == '' or row[i] == 'T' or row[i] == 'R':
                    row[i] = '00'
                row[10] = label
                
            
            processed_rows.append(row)

    with open(output_csv_path, 'w', newline='') as output_file:
        writer = csv.writer(output_file)
        writer.writerows(processed_rows)

# Removes only the third colum *Can be changed to any
def remove_third_column(input_csv_path, output_csv_path):
   with open(input_csv_path, 'r', newline='') as input_file:
        with open(output_csv_path, 'w', newline='') as output_file:
            reader = csv.reader(input_file)
            writer = csv.writer(output_file)

            for row in reader:
                # Write all columns except the third one (index 2)
                writer.writerow(row[:2] + row[3:])
