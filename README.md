# SimplifinInterview-DS-Assignment

This project contains the code to the assignment for DS interview at Simplifin

> **Note : Checkout the [reports/](https://github.com/AvAkanksh/SimplifinInterview-DS-Assginment/tree/main/reports) folder for the Final Analysis of the Reconciliation.**

## My Project Folder Organization

``` shell

├── data
│   ├── external
│   ├── interim
│   ├── processed
│   │   ├── oms_data.csv
│   │   └── paytm_data.csv
│   └── raw
│       └── Data Assignment File.xlsx
├── docs
│   ├── docs
│   │   ├── getting-started.md
│   │   └── index.md
│   ├── mkdocs.yml
│   └── README.md
├── Makefile
├── models
├── notebooks
│   ├── dataAnalysis.ipynb
│   └── dataExploration.ipynb
├── pyproject.toml
├── README.md
├── reconciliation
│   ├── __init__.py
│   └── reconciliation.py
├── references
├── reports
│   ├── figures
│   │   └── difference_in_timestamps_oms_vs_paytm.png
│   ├── final_processed_oms_data.csv
│   ├── final_processed_paytm_data.csv
│   ├── README.md
│   └── reconciliation_report.csv
├── requirements.txt
└── setup.cfg

```

## General Reference of Project Organization

```
├── LICENSE            <- Open-source license if one is chosen
├── Makefile           <- Makefile with convenience commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
│
├── docs               <- A default mkdocs project; see mkdocs.org for details
│
├── models             <- Trained and serialized models, model predictions, or model summaries
│
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── pyproject.toml     <- Project configuration file with package metadata for reconciliation
│                         and configuration for tools like black
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `pip freeze > requirements.txt`
│
├── setup.cfg          <- Configuration file for flake8
│
└── reconciliation                <- Source code for use in this project.
    │
    ├── __init__.py    <- Makes reconciliation a Python module
    │
    ├── data           <- Scripts to download or generate data
    │   └── make_dataset.py
    │
    ├── features       <- Scripts to turn raw data into features for modeling
    │   └── build_features.py
    │
    ├── models         <- Scripts to train models and then use trained models to make
    │   │                 predictions
    │   ├── predict_model.py
    │   └── train_model.py
    │
    └── visualization  <- Scripts to create exploratory and results oriented visualizations
        └── visualize.py
```

## How to run the code/project


- **Step 1** : Download the project and navigate into the project directory
- **Step 2** : Install the required dependencies

``` shell
pip install -r requirements.txt
```

- **Step 3** : Run the below command to run the reconciliation script

``` shell
python reconcilation/reconciliation.py
```

> **Note : Checkout the [reports/](https://github.com/AvAkanksh/SimplifinInterview-DS-Assginment/tree/main/reports) folder for the Final Analysis of the Reconciliation.**
