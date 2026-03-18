# Hypercube-ML

This repository contains the code for the 
**Statistically representative, TESSERACT-guided Application Sampling strategy (STAS)** and 
the **Average Area Under Time (A-AUT)** driven evaluations of malware classifiers as introduced in:

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
 

## How-to

### Setup

We recommend installing this repo as a pip package. Either run `pip install .` from within the directory or add the 
following line to your `requirements` file:

`git+ssh://git@github.com/s2labres/hypercube-ml.git@main#egg=hypercube-ml`

### Reproduce paper results

To reproduce the results in the original paper, refer to `experiments/reproduce_results.md`.

### Use the library

Both the library and the experiments are built on top of the `Android Malware Detectors` library developed by S2Lab 
(https://github.com/s2labres/android_malware_detectors). 
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

To compute the **A-AUT** for your newly defined malware detector, you can use the APIs:

1. `temporal_luck.trainer.train_model` for training your model across all time splits.
2. `temporal_luck.trainer.test_model` for evaluating your model across all time splits

```python
import os

from temporal_luck.trainer import train_classifier
from temporal_luck.temporal_windows import training_slice_iterator

for start_date, end_date in training_slice_iterator():
    save_dir = f"save_dir-{start_date}-{end_date}/"
    os.makedirs(save_dir, exist_ok=True)
    my_model = MyNewMalwareDetector(save_dir)

    dataset = []
    labels = []

```



## 🔬 Project Overview
The reliability of machine learning critically depends on dataset quality. While machine learning applied to computer 
vision and natural language processing benefit from high-quality benchmark datasets, cyber security often falls behind,
as quality ties to the ability of accessing hard-to-obtain realistic datasets that may evolve over time.
Android is, however, positioned uniquely in this ecosystem thanks to AndroZoo and other sources, which provide
large-scale, continuously updated, and timestamped repositories of benign and malicious apps. 

Since their release, such data sources provided access to populations of Android apps that researchers can sample 
from to evaluate learning-based methods in realistic settings, i.e., over temporal frames to account for apps evolution 
(natural distribution shift) and test datasets that reflect in-the-wild class ratios. Surprisingly, 
we observe that despite this abundance of data, performance discrepancies of learning-based Android malware classifiers
still persist even after satisfying such realistic requirements, which challenges our ability to understand what
the state-of-the-art in this field is. In this work, we identify five novel factors that influence such discrepancies:
we show how such factors have been largely overlooked and the impact they have on providing sound evaluations.
Our findings and recommendations help define a methodology for creating trustworthy datasets towards sound evaluations
of Android malware classifiers.

## 📧 Contact
For questions regarding the status of this research, please contact Dr Mario D'Onghia at m.donghia@ucl.ac.uk.