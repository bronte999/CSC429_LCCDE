# Processed ROAD Dataset

## Original Dataset
Description from [Zendodo](https://zenodo.org/records/10462796) download: "The Real ORNL Automotive Dynamometer (ROAD) CAN IDS dataset consistis of over 3.5 hours of one vehicle's CAN data. ROAD contains ambient data recorded during a diverse set of activities, and attacks of increasing stealth with multiple variants and instances of real (i.e. non-simulated) fuzzing, fabrication, unique advanced attacks, and simulated masquerade attacks. In addition to the 'raw' CAN format, the data is also provided in a the signal time series format for many of the CAN captures." \
\
Research paper: \
```Verma ME, Bridges RA, Iannacone MD, Hollifield SC, Moriano P, Hespeler SC, et al. (2024) A comprehensive guide to CAN IDS data and introduction of the ROAD dataset. PLoS ONE 19(1): e0296879. https://doi.org/10.1371/journal.pone.0296879```

## Processing
The original dataset had raw CAN captures in .log files and translated the captures to signals in .csv files. 
We converted the .log files to .csv files with the features: Time, Id, Byte1, Byte2, Byte3, Byte4, Byte5, Byte6, Byte7, Byte8, Label. 
Since the timestamps are shifted uniformly by a scalar for each individual file, we recommend excluding the Time column when you use the dataset.
In addition, we used the provided metadata to label the captures as a type of attack or benign. 
The labels are: Benign, Accelerator, Fuzzing, CorrelatedSignal, MaxEngineCoolantTemp, MaxSpeedometer, ReverseLight. 
To use a different set of labels (e.g. Benign, Accelerator, Fuzzing, Fabrication, Masquerade), you can modify the get_attack_label function in "data/road_work.py", or change the label column in the individual attack files. \
\
The 33 individual attacks can be found in "data/processed-road/attacks/", and the zipped .csv file containing all of the attacks is "data/processed-road/road.csv.zip" (zipped due to GitHub file size constraints).
The code for data processing is in the file "data/road_work.py". The ambient data is not converted due to large file size, but (untested) code to convert the ambient data is provided.
The road_work code expects the file tree to have the original dataset in the relative "./road-dataset/" directory, as follows:

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
