# USD/IDR Exchange Rate Forecasting with LSTM Optimization

A forecasting project comparing **Random Search** and **Particle Swarm Optimization (PSO)** for tuning an LSTM model on USD/IDR exchange-rate data.

## Objective

Assess whether PSO can identify better LSTM hyperparameters than Random Search when both methods are evaluated using a sliding-window time-series validation scheme.

## Workflow

1. Data preprocessing, exploratory analysis, and chronological train/validation/test splitting.
2. LSTM hyperparameter search using Random Search.
3. LSTM hyperparameter optimization using Particle Swarm Optimization.
4. Final training and evaluation using the best configuration from each search method.

The optimized parameters include sequence length, hidden size, number of layers, learning rate, dropout, batch size, and training epochs.

## Key Result

The accompanying report shows that the PSO-optimized LSTM achieved a lower RMSE (**0.013**) than the Random Search baseline (**0.017**) under the study's evaluation setup.

## Files

| File | Description |
|---|---|
| [`01-data-preprocessing-eda.ipynb`](01-data-preprocessing-eda.ipynb) | Data preparation, exploratory analysis, and time-series split. |
| [`02-random-search-sliding-window.ipynb`](02-random-search-sliding-window.ipynb) | Random Search with sliding-window cross-validation. |
| [`03-pso-sliding-window.ipynb`](03-pso-sliding-window.ipynb) | PSO-based LSTM hyperparameter optimization. |
| [`04-final-training-evaluation.ipynb`](04-final-training-evaluation.ipynb) | Final model training, comparison, and test evaluation. |
| [`random-search-sliding-window-results.json`](random-search-sliding-window-results.json) | Best Random Search hyperparameters. |
| [`pso-sliding-window-results.json`](pso-sliding-window-results.json) | Best PSO hyperparameters. |
| [`usdidr-jisdor-exchange-rate.csv`](usdidr-jisdor-exchange-rate.csv) | Historical USD/IDR exchange-rate data. |
| [`pso-lstm-usdidr-forecasting.pdf`](pso-lstm-usdidr-forecasting.pdf) | Full project report. |

## Reproducibility Note

The notebooks preserve the original Kaggle workflow and contain Kaggle-specific input/output paths. When running locally, update those path variables or execute the notebooks in sequence using equivalent local paths.
