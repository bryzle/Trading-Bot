# Code Style

- Follow existing patterns in `tradingbot.py` for strategy extensions
- Use Pydantic models for data validation in TradingEdge AI
- Type hints are used in TradingEdge AI but not in traditional bot
- Docstrings use triple-quoted strings with Args/Returns sections in TradingEdge AI
- Avoid unnecessary nested conditionals — flatten using chained methods (e.g. `removeprefix`, `removesuffix`) or early returns where possible
