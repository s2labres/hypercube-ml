# Hypercube-ML

This repository contains the code for the 
**Statistically representative, TESSERACT-guided Application Sampling strategy (STAS)** and for performing the rolling time
window evaluation with the **Average Area Under Time (A-AUT)** as introduced in:

> **"Beyond the TESSERACT: Trustworthy Dataset Curation for Sound Evaluations of Android Malware Classifiers"**

> *Authors: T. Chow, M. D'Onghia, L. Linhardt, Z. Kan, D. Arp, L. Cavallaro, F. Pierazzi*

If using this code for research, please cite us:

```bibtex
@inproceedings{chow2025breaking,
  title = {{Beyond the TESSERACT: Trustworthy Dataset Curation for Sound Evaluations of Android Malware Classifiers}},
  author = {Chow, Theo and D'Onghia, Mario and Linhardt, Lorenz and Kan, Zeliang and Arp, Daniel and Cavallaro, Lorenzo and Pierazzi, Fabio},
  year = {2026},
  booktitle = {{IEEE} Conference on Secure and Trustworthy Machine Learning ({SaTML})},
}
```

Furthermore, the code for reproducing the results in the paper can be found in the `experiments` folder.

The **Hypercube** dataset and all the data used in the paper can be found here:

[Hypercube dataset and paper data](https://liveuclac-my.sharepoint.com/:f:/g/personal/ucacier_ucl_ac_uk/IgDzMmmiN5p9TKbxnEKQXil-AYUPiXFrWDpeJZlawtm0jnQ?e=P9ybkn)
 

## How-to

### Setup

We recommend installing this repo as a pip package. Either run `pip install .` from within the directory or add the 
following line to your `requirements` file:

`git+ssh://git@github.com/s2labres/hypercube-ml.git@main#egg=hypercube-ml`

### Reproduce paper results

To reproduce the results in the original paper, refer to `experiments/reproduce_results.md`.

*The code and data for experiments on VTT and App Market is not yet available but will soon be released. 
Please expect this to be made available before 30/04/2026.*

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
Please refer to the library repo for further information.

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


## 📧 Contact
For questions regarding the status of this research, please contact Dr Mario D'Onghia at m.donghia@ucl.ac.uk.