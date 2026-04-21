---
paths:
  - "tradingbot.py"
  - "finbert_utils.py"
---

# Traditional Trading Bot

**Core Strategy**: `RebalancingMLTrader` class extends Lumibot Strategy framework

**Trading Loop**:
1. Fetch news headlines from Alpaca API (last 3 days)
2. Run FinBERT sentiment analysis via `finbert_utils.py`
3. Rebalance portfolio to maintain target allocation (default 50% SPY)
4. Sleep 24 hours and repeat

**Key Methods**:
- `get_sentiment()` - Fetches news and returns FinBERT probability/sentiment
- `rebalance_portfolio()` - Calculates delta between current and target allocation, submits buy/sell orders
- `position_sizing()` - Determines trade quantity based on cash at risk
- `on_trading_iteration()` - Main loop called every 24 hours

**Backtesting**: Uses `YahooDataBacktesting` with historical data. Current backtest period: Dec 15-31, 2023 on SPY.

## Development Notes

- The bot runs on paper trading by default (`"PAPER": True` in `ALPACA_CREDS`)
- Backtest parameters: `symbol`, `cash_at_risk`, `target_allocation`
- FinBERT outputs: `(probability: float, sentiment: str)` where sentiment is "positive", "negative", or "neutral"
- Trading iterations sleep for 24H between runs

## Data Flow

```
Alpaca News API → FinBERT Sentiment → Rebalancing Logic → Alpaca Broker → Paper Trading
                       ↓
                  [probability, sentiment]
                       ↓
              Portfolio Rebalancing Decision
```

## Critical Imports

- **Lumibot**: `lumibot.brokers.Alpaca`, `lumibot.strategies.Strategy`, `lumibot.backtesting.YahooDataBacktesting`
- **Alpaca API**: `alpaca_trade_api.REST` for news and order submission
- **FinBERT**: `transformers.AutoTokenizer/AutoModelForSequenceClassification` (ProsusAI/finbert)
- **PyTorch**: Backend for FinBERT inference with GPU acceleration
