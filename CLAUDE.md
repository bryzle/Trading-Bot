# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## Project Overview

Trading-Bot is an AI-powered algorithmic trading platform integrating sentiment analysis and technical chart analysis for automated trading on Alpaca. The project consists of two components:

1. **Traditional Trading Bot** - Production-ready Lumibot-based strategy using FinBERT sentiment analysis
2. **TradingEdge AI** - In-development FastAPI microservice for GPT-4V chart pattern analysis

## Architecture Overview

- Traditional bot is **monolithic**: Single file with strategy, backtesting, and execution (`tradingbot.py`)
- TradingEdge AI uses **layered architecture**: API → Services → Models (`tradingbot_edge/`)
- Configuration management via Pydantic Settings with `.env` file
- Both systems use same Alpaca credentials from environment variables
- Future integration point: Combine GPT-4V chart analysis with FinBERT sentiment in unified trading decision
