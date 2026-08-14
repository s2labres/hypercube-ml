# Hypercube-ML

This repository contains the link to the hypercube dataset, and the code for the 
**Statistically representative, TESSERACT-guided Application Sampling strategy (STAS)** and for the rolling time
window evaluations with the **Average Area Under Time (A-AUT)** as introduced in:

>  T. Chow, M. D'Onghia, L. Linhardt, Z. Kan, D. Arp, L. Cavallaro, F. Pierazzi, "**Beyond the TESSERACT: Trustworthy Dataset Curation for Sound Evaluations of Android Malware Classifiers**", IEEE SaTML 2026.

If using this code or dataset for research, please cite us:

```bibtex
@inproceedings{chow2025breaking,
  title = {{Beyond the TESSERACT: Trustworthy Dataset Curation for Sound Evaluations of Android Malware Classifiers}},
  author = {Chow, Theo and D'Onghia, Mario and Linhardt, Lorenz and Kan, Zeliang and Arp, Daniel and Cavallaro, Lorenzo and Pierazzi, Fabio},
  year = {2026},
  booktitle = {{IEEE} Conference on Secure and Trustworthy Machine Learning ({SaTML})},
}
```

Furthermore, the code for reproducing the results in the paper can be found in the `experiments` folder.

## Table of Contents

- [Hypercube Dataset](#hypercube-dataset)
- [How-to](#how-to)
  - [Setup](#setup)
  - [Use the library](#use-the-library)
  - [Reproduce paper results](#reproduce-paper-results)
- [📧 Contact](#-contact)

## Hypercube Dataset

The **Hypercube** dataset can be found at this link: [Hypercube dataset](https://liveuclac-my.sharepoint.com/:f:/g/personal/ucacier_ucl_ac_uk/IgDzMmmiN5p9TKbxnEKQXil-AYUPiXFrWDpeJZlawtm0jnQ?e=P9ybkn)

The `load.py` script is just an example, and we recommend to refer to the [Android Malware Detectors library](https://github.com/s2labres/android_malware_detectors) for proper loading of the dataset.

The "hypercube" folder contains the dataset sampled in the [IEEE SaTML 2026 version of the paper](https://discovery.ucl.ac.uk/id/eprint/10220473/1/chow-satml26.pdf) (i.e., sampled with VTT=2). It includes two sub-folders: "original" (as described in the SaTML26 paper, sampled from 2021-23) and "extended_2024" (including sampled collected from 2021-2024 using the STAS methodology).

The "legacy versions" include a sampling of the dataset done with VTT=4, which resulted from an [older arXiv version of the paper](https://arxiv.org/abs/2506.23814v1). 

Relevant changelog for the dataset folder:
* **12-08-2026** The `load.py` example script (found in the dataset folder) was modified to use VTT=2 (instead of 4). 
* **13-07-2026** The main VTT=2 Dataset has been separated into: original (2021-2023) and extended_2024 (2021-2024).
* **29-06-2026**: RAMDA features for the official hypercube have been updated.

## How-to

### Setup

We recommend installing this repo as a pip package. Either run `pip install .` from within the directory or add the 
following line to your `requirements` file:

`git+ssh://git@github.com/s2labres/hypercube-ml.git@main#egg=hypercube-ml`

### Use the library

Both the library and the experiments are built on top of the 
[Android Malware Detectors library](https://github.com/s2labres/android_malware_detectors) developed by S2Lab. 
To perform A-AUT-based evaluations, we recommend using the library interface.

For example, when implementing a new malware detector, this should extend 
`android_malware_detectors.detectors.base.base_detector.BaseDetector` and implement the following methods:


```python
from android_malware_detectors.detectors.base.base_detector import BaseDetector


class MyNewMalwareDetector(BaseDetector):
    def __init__(self, save_directory):
        super().__init__(self, save_directory, name="My New Malware Detector")
        '''Rest of My Code'''
    
    def _train_preprocessing(self, dataset_dict, labels_dict, *args, **kwargs):
        """
        Here I receive a dataset {hash: features} and a dictionary {hash: label}
        and output the preprocessed version of them (if needed). 
        For example, a Dataset generator for Keras or a Dataloader in PyTorch.
        """
        pass
    
    def _train_classifier(self, dataset, labels, *args, **kwargs):
        """
        Here I perform the required actions to train my model. 
        dataset and labels are what will be outputted by your _train_preprocessing.
        """
        pass
    
    def _test_preprocessing(self, dataset_dict, *args, **kwargs):
        """
        Similar to _train_preprocessing but for test time.
        """
        pass
    
    def _predict(self, dataset, *args, **kwargs):
        """
        Analogous to _train_classifier but for test time.
        dataset is what will be outputted by your _test_preprocessing.
        """
    
```
Please refer to the Android Malware Detectors library repo for further information.

To perform a **Temporal Luck** evaluation as discussed in the paper, you can use the `TemporalLuckEvaluator` 
made available by the library.

The following example shows how to perform a Temporal Luck evaluation using 6 months for training and 12 for testing.
Notice that you can register multiple classifiers and multiple datasets per classifier. Being built on the Android 
Malware Detectors library (https://github.com/s2labres/android_malware_detectors), it assumes that the dataset is 
accompanied by a meta file where information such as timestamps and number of detections is provided for each sample.

```python
import os
import datetime

from hypercube.temporal_luck.temporal_luck_evaluator import TemporalLuckEvaluator


temporal_luck_evaluator = TemporalLuckEvaluator()
temporal_luck_evaluator.register_classifier_class("MyNewMalwareDetector", MyNewMalwareDetector)
temporal_luck_evaluator.register_dataset("dataset_1")
temporal_luck_evaluator.register_vtt("dataset_1", 5)
temporal_luck_evaluator.register_meta_path("dataset_1", "path_to_meta_file")
temporal_luck_evaluator.register_date_type("dataset_1", "vt_first_submission_date")
temporal_luck_evaluator.register_dataset_for_classifier("dataset_1", "MyNewMalwareDetector", "path_to_features_for_dataset_1")

dataset_start_date, dataset_end_date = datetime.date(2021, 1, 1), datetime.date(2023, 12, 1)
time_granularity, time_granularity_value = "monthly", 1
training_window_length, test_window_length = 6, 12
trainined_detectors_dir = "trained_detectors/"

temporal_luck_evaluator.train_all(dataset_start_date, dataset_end_date, training_window_length, test_window_length, 
                                  time_granularity, time_granularity_value, trainined_detectors_dir)


results_dir = "temporal_luck_results/"
temporal_luck_evaluator.evaluate_all(trainined_detectors_dir, dataset_start_date, dataset_end_date, results_dir,
                                     time_granularity, time_granularity_value, training_window_length, test_window_length)
```


To sample a new dataset using **STAS**, you can use the `STASSampler` provided with this library.
You will need a json file describing the population you want to sample from, where each entry contains the 
hash, timestamp, and number of detections of each sample. For example:

```
[
    {
        "sha256": "e5c7c8e4bfb9822e9cbaf9d6b639a6b10dcfb92ffc67bcf6345efa752c8b3f46",
        "vt_detection": 15,
        "dex_date": "2015-12-01"
    }
]
```

Notice that the keys for hashes, timestamps, and number of detections are fully customizable. See the 
following example:

```python
import datetime

from hypercube.stas.sampler import STASSampler


stas_sampler = STASSampler("path_to_your_population_descriptor_file", 
                           sample_hash_type="custom_hash_key", 
                           timestamp_type="custom_timestamp_key",
                           detections_key="custom_detection_key", vtt=5)

dataset_start_date, dataset_end_date = datetime.date(2021, 1, 1), datetime.date(2023, 1, 1)
new_dataset_hash_list = stas_sampler.sample_dataset(dataset_start_date, dataset_end_date, time_granularity="monthly",
                                                    time_granularity_value=1, malware_percentage=0.1)
```

### Reproduce paper results

To reproduce the results in the original paper, refer to `experiments/reproduce_results.md`.

*The code and data for the experiments on VTT and App Market is not yet available but will be soon released.*

## 📧 Contact

For questions regarding the status of this research or this repository, please contact Dr Mario D'Onghia at m.donghia@ucl.ac.uk.
