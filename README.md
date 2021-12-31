# Optimal-portfolio-with-FTX-data

## Usage
Run `python portfolio.py`.

## Explanation
The script does the following
* GET historical prices for BTC-PERP, ETH-PERP, ADA-PERP, with hourly resolution, for the month of October
* Calculate expected hourly returns for each contract
* Calculate covariance of returns for the contracts
* Calculate portfolio volatility and expected return for randomly generated portfolios
* Find the portfolio with the best Sharpe ratio
* Plot these results on a scatter graph