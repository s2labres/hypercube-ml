# Hypercube-ML

![Status](https://img.shields.io/badge/status-under--construction-orange)

This repository contains the code and analysis for the manuscript:
> **"Beyond the TESSERACT: Trustworthy Dataset Curation for Sound Evaluations of Android Malware Classifiers"**

> *Authors: T. Chow, M. D'Onghia, L. Linhardt, Z. Kan, D. Arp, L. Cavallaro, F. Pierazzi*

---

## 🚧 Current Status
This repository is a work-in-progress. We are currently cleaning the source code and documenting 
the environment requirements to ensure reproducibility. 

**Estimated Completion:** March 2026.

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