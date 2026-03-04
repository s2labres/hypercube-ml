## How to reproduce results from "Beyond the TESSERACT"

Please notice that the experiments in this repo are very data intensive.
To foster reproducibility, we provide the data, trained models, and evaluation results
at [url].
Please download the archive and uncompress it, then copy the `data` folder into the homonymous directory.
Similarly, copy the `trained_models` and `evaluation_results` folders in the corresponding
directories.

We also provide the scripts to resample the datasets in the `timestamps-experiment-1`,
`markets`, and `sampling` experiments. However, we don't provide the code to 
download the APKs or the VirusTotal reports that are needed. The APKs can be downloaded from AndroZoo,
while the reports can be obtained from VirusTotal (one API key per person with a limit of 500
requests/day). Alternatively, reports can be obtained from VirusShare, which allows more daily requests but 
does not usually contain reports for all requested malware.

### Setup
After downloading the data, create a python (3.12) environment, activate it, and
install dependencies.
1. `python -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`


### Timestamps

#### Experiment 1

In `data/timestamps/experiments_1`, you will find two folders:
1. `transcend_emulation`
2. `transcend_sampled_today`

which contain 5 datasets, each sampled according to Section IV.B.

All 10 datasets can also be resampled from scratch by running: `python -m experiments.timestamps.experiment_1.dataset_sampler`.

To plot Figure 3 in the paper, run:
`python -m experiments.timestamps.experiment_1.figure_3_generator`


#### Experiment 2

To generate Table II in Section IV.B. run:

`python -m experiments.timestamps.experiment_2.table_2_generator`

To generate Table III in Section IV.B. run:

`python -m experiments.timestamps.experiment_2.table_3_generator`.


### Temporal Luck

#### Motivational plot

The motivational plots highlighting the existence of the "temporal luck" phenomenon
(Figure 4 in Section V.A. and Figure 9 in Appendix E) can be obtained by running:

`python -m experiments.temporal_luck.motivational.motivational_plots {DrebinSVM|DeepDrebin|MalScan|RAMDA|HCC} {APIGraph|Transcendent}`

To obtain the data from scratch, you need to:
1. Train all the models with `python -m experiments.temporal_luck.motivational.train_all`
2. Evaluate all trained models with `python -m experiments.temporal_luck.motivational.evaluate_all`

#### Table IV

Table IV in Section V.B. shows the AUT (one year windows) for the two datasets; furthermore, it presents the average AUT
and standard deviation.

To obtain the table, run:

