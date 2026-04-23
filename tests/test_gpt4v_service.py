from tradingbot_edge.services.gpt4v_service import GPT4VChartAnalyzer
from unittest.mock import patch

@patch('tradingbot_edge.services.gpt4v_service.anthropic.Anthropic')
def test_parse_response_valid_json(mock_anthropic):
    # mock_openai now replaces the OpenAI constructor — __init__ won't crash
    analyzer = GPT4VChartAnalyzer()

    valid_json = '''{
        "overall_analysis": "Strong uptrend",
        "patterns": [
            {"pattern_name": "Bull Flag", "confidence": 0.9, "description": "Clean breakout"}
        ],
        "sentiment": "bullish",
        "confidence_score": 0.85
    }'''

    result = analyzer._parse_response(valid_json, "AAPL")

    assert result.symbol == "AAPL"
    assert result.sentiment == "bullish"
    assert len(result.patterns) == 1
    assert result.patterns[0].pattern_name == "Bull Flag"