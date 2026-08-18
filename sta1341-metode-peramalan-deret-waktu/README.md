# Tourist Arrivals Forecasting: SARIMAX vs LSTM

A time-series forecasting project comparing SARIMAX and Long Short-Term Memory (LSTM) models for monthly international tourist arrivals to Indonesia.

## Objective

Evaluate whether a deep-learning approach can better capture the seasonal and highly fluctuating behavior of international tourist arrivals than a conventional seasonal time-series model.

## Data

The dataset contains monthly international tourist arrivals from January 1998 through August 2025.

## Methods

- Time-series preprocessing and train/test preparation.
- SARIMAX modeling as the statistical baseline.
- LSTM sequence modeling with normalized inputs.
- Model comparison using RMSE and MAPE.
- Residual and diagnostic evaluation for the LSTM model.

## Key Result

In the accompanying report, LSTM achieved lower forecast error than SARIMAX: RMSE **106,089.12** and MAPE **7.46%**, compared with SARIMAX RMSE **123,288.40** and MAPE **8.53%**.

## Files

| File | Description |
|---|---|
| [`lstm-tourist-arrivals-forecasting.ipynb`](lstm-tourist-arrivals-forecasting.ipynb) | LSTM preprocessing, modeling, prediction, and diagnostics. |
| [`sarimax-vs-lstm-tourist-arrivals-forecasting.pdf`](sarimax-vs-lstm-tourist-arrivals-forecasting.pdf) | Full comparative report. |
| [`tourist-arrivals.csv`](tourist-arrivals.csv) | Monthly international tourist-arrival data. |

## Reproducibility Note

The notebook was developed in a notebook environment and includes environment-specific setup/upload cells. Adjust the data-loading section if running directly from a cloned repository.
