# Processed ROAD Dataset


## Original Dataset
Description from [Zenodo](https://zenodo.org/records/10462796) download: 
"The Real ORNL Automotive Dynamometer (ROAD) CAN IDS dataset consistis of over 3.5 hours of one vehicle's CAN data. ROAD contains ambient data recorded during a diverse set of activities, and attacks of increasing stealth with multiple variants and instances of real (i.e. non-simulated) fuzzing, fabrication, unique advanced attacks, and simulated masquerade attacks. In addition to the 'raw' CAN format, the data is also provided in a the signal time series format for many of the CAN captures." \
\
Research paper: \
```Verma ME, Bridges RA, Iannacone MD, Hollifield SC, Moriano P, Hespeler SC, et al. (2024) A comprehensive guide to CAN IDS data and introduction of the ROAD dataset. PLoS ONE 19(1): e0296879. https://doi.org/10.1371/journal.pone.0296879```


## Processing
The original dataset had raw CAN captures in .log files and translated the captures to signals in .csv files. 
We converted the .log files to .csv files with the features: 
`Time, Id, Byte1, Byte2, Byte3, Byte4, Byte5, Byte6, Byte7, Byte8, Label`.

We used the provided metadata to label the captures as a type of attack or Benign.
The labels are: `Benign, Accelerator, Fuzzing, Fabrication, Masquerade`. 
To use a different set of labels, you can modify the get_attack_label() function in `data/road_work.py`, 
or change the label column in the individual attack files (see `change_labels.py`). \
Since the timestamps are shifted uniformly by a scalar for each individual file, 
we recommend excluding the Time column or doing further processing when you use the dataset.
\

The zipped file containing all of the labelled captures from the 33 attack files is 
`data/processed-road/road.csv.zip` (zipped due to GitHub file size limitations).
The individual labelled attack files can be found in `data/processed-road/attacks/`.
The code for data processing is in the file `data/road_work.py`. 
We did not process the ambient data due to the large file sizes, but (untested) code to convert the ambient data is provided.
The road_work code expects the original dataset to be in the relative `./road-dataset/` directory, as follows:

* data/
  * processed-road/
    * ambient/
    * attacks/
  * **road-dataset/**
    * ambient/
      * ambient_dyno_drive_basic_long.log
      * ...
    * attacks/
      * accelerator_attack_drive_1.log
      * ...
  * **road_work.py**
