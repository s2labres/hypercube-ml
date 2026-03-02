## How to reproduce results from "Beyond the TESSERACT"

Please notice that the experiments in this repo are very data intensive.
We provide the data we used for reproducibility at [url].
Please download the archive and unpack it into the `data` folder.

We also provide the scripts to resample the datasets in the `timestamps-experiment-1`,
`markets`, and `sampling` experiments. However, we don't provide the code to 
download the APKs or the VirusTotal reports that needed. The APKs can be downloaded from AndroZoo,
while the reports can be obtained from VirusTotal (one key per person with a limit of 500
requests/day). Alternatively, reports can be obtained from VirusShare, which has 
allows mode daily requests but may not contain all the requested reports.

### Setup
After downloading the data, create a python (3.12) environment, activate it, and
install dependencies.
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`


### Timestamps

#### Experiment 1

In `data/timestamps/experiments_1`