# TradingEdge AI Module

**Status**: Under active development - scaffolding complete, API endpoints not yet implemented

## Structure

```
tradingbot_edge/
├── config.py              # Pydantic settings (OpenAI, Alpaca credentials)
├── api/v1/                # FastAPI routes (empty - needs implementation)
├── models/
│   └── chart_analysis.py  # Pydantic schemas for chart analysis
├── services/
│   └── gpt4v_service.py   # GPT-4V integration (partial - has TODOs)
└── utils/                 # Utilities (empty)
```

## GPT4VChartAnalyzer Service

Located in `services/gpt4v_service.py`:
- `analyze_chart()` - Main entry point for chart analysis
- `_create_analysis_prompt()` - Complete (generates structured JSON prompt)
- `_call_gpt4v()` - **TODO**: Not implemented, needs OpenAI vision API call
- `_parse_response()` - **TODO**: Not implemented, needs JSON parsing to `ChartAnalysisResponse`

## Planned Features

- RAG system for earnings/SEC filing analysis
- Multi-agent reasoning with LangGraph
- Integration with existing FinBERT sentiment

## Development Notes

### Completing GPT-4V Service

1. Implement `_call_gpt4v()`: Use OpenAI client with vision model (gpt-4o from config)
2. Implement `_parse_response()`: Parse JSON response into `ChartAnalysisResponse` model
3. Pattern detection should return `List[PatternDetection]` with confidence scores

### Adding FastAPI Routes

- Create route handlers in `api/v1/`
- Import `GPT4VChartAnalyzer` from services
- Use Pydantic models from `models/chart_analysis.py` for request/response validation
- Configuration is available via `get_settings()` from config module

### Testing

- No test infrastructure currently exists (empty `tests/` directory)
- When adding tests, use pytest (already in requirements.txt)
