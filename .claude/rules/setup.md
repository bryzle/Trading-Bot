# Development Setup

## Commands

### Running the Traditional Trading Bot

```bash
# Local execution
python tradingbot.py

# Test sentiment analysis standalone
python finbert_utils.py
```

### Docker Development

```bash
# Build the container
docker compose build

# Run the bot in container
docker compose run app

# Interactive bash session
docker compose run app /bin/bash
```

### Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt
```

**Note**: The project uses Python 3.7 in Docker but works with Python 3.7+. GPU acceleration is used for FinBERT if CUDA is available.

## Environment Configuration

Required environment variables in `.env`:

```
API_KEY=<Alpaca API Key>
API_SECRET=<Alpaca API Secret>
API_URL=https://paper-api.alpaca.markets/v2
OPENAI_API_KEY=<OpenAI API Key>
```

**Important**: The `.env` file currently exists but should be gitignored. Never commit credentials.
