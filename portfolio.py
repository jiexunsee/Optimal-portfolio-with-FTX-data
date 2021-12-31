import time
import hmac
from requests import Request, Session
import json
import numpy as np
import matplotlib.pyplot as plt

from api_keys import API_KEY, API_SECRET


s = Session()
ftx_api = 'https://ftx.com/api'

def get_request(endpoint):
    ts = int(time.time() * 1000)
    endpoint = ftx_api + endpoint
    request = Request('GET', endpoint)
    prepared = request.prepare()
    signature_payload = f'{ts}{prepared.method}{prepared.path_url}'
    if prepared.body:
        signature_payload += prepared.body
    signature_payload = signature_payload.encode()
    signature = hmac.new(API_SECRET.encode(), signature_payload, 'sha256').hexdigest()

    request.headers['FTX-KEY'] = API_KEY
    request.headers['FTX-SIGN'] = signature
    request.headers['FTX-TS'] = str(ts)

    resp = s.send(prepared)
    return resp

def get_perps(market_name, resolution, start_time, end_time):
    resp = get_request('/markets/{}/candles?resolution={}&start_time={}&end_time={}'.format(market_name, resolution, start_time, end_time))
    if resp.status_code != 200:
        raise Exception('Status code: {}'.format(resp.status_code))
    result = json.loads(resp.text)
    perps = result['result']
    return perps

def get_optimal_portfolio(expected_returns, cov_matrix, risk_free_rate, num_samples = 1000, plot_filename = ''):
    portfolio_returns = []
    portfolio_volatilities = []
    portfolio_weights = []
    for portfolio in range(num_samples):
        weights = np.random.random(len(market_names))
        weights = weights / np.sum(weights)
        ret = np.dot(weights, expected_returns)
        portfolio_variance = np.multiply(np.multiply(cov_matrix, weights), weights[:, np.newaxis]).sum()
        portfolio_volatility = np.sqrt(portfolio_variance)

        portfolio_weights.append(weights)
        portfolio_returns.append(ret)
        portfolio_volatilities.append(portfolio_volatility)

    sharpe_ratios = [(portfolio_returns[i] - risk_free_rate) / portfolio_volatilities[i] for i in range(num_samples)]
    max_sharpe_ratio_idx = np.argmax(sharpe_ratios)
    best_portfolio = portfolio_weights[max_sharpe_ratio_idx]

    if plot_filename:
        fig = plt.figure()
        min_x = min(portfolio_volatilities)
        max_x = max(portfolio_volatilities)
        min_y = min(portfolio_returns)
        max_y = max(portfolio_returns)
        xlim = (min_x - (max_x - min_x) * 0.1, max_x + (max_x - min_x) * 0.1)
        ylim = (min_y - (max_y - min_y) * 0.1, max_y + (max_y - min_y) * 0.1)
        plt.xlim(xlim)
        plt.ylim(ylim)
        plt.xlabel('Volatility')
        plt.ylabel('Expected Return')
        plt.title('Efficient Frontier')
        plt.scatter(portfolio_volatilities, portfolio_returns, s = 2, c ="cornflowerblue")
        plt.scatter(portfolio_volatilities[max_sharpe_ratio_idx], portfolio_returns[max_sharpe_ratio_idx], color='orangered', marker='*', s=100)
        fig.savefig(plot_filename)

    return best_portfolio

if __name__ == '__main__':
    resolution = 3600 # one hour
    start_time = 1633046400 # 2021-10-01 T00:00:00 +00:00
    end_time = 1635721200 # 2021-10-31 T23:00:00 +00:00
    market_names = ['BTC-PERP', 'ETH-PERP', 'ADA-PERP']

    expected_returns = []
    all_returns = []
    for market_name in market_names:
        perps = get_perps(market_name, resolution, start_time, end_time)
        returns = [(p['close'] - p['open']) / p['open'] for p in perps]
        all_returns.append(returns)
        expected_return = np.array(returns).mean()
        expected_returns.append(expected_return)

    all_returns = np.stack(all_returns, axis = 0)
    cov_matrix = np.cov(all_returns)

    risk_free_rate = (1.05 ** (1/(365 * 24))) - 1 # Risk free rate per hour, assuming risk free rate per year = 5%
    num_samples = 5000
    plot_filename = 'efficient_frontier.png'
    optimal_portfolio = get_optimal_portfolio(expected_returns, cov_matrix, risk_free_rate, num_samples, plot_filename)
    output = {market_names[i] : optimal_portfolio[i] for i in range(len(market_names))}
    print(output)