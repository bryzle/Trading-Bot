"""
API v1 route handlers
"""
from fastapi import APIRouter, HTTPException
from tradingbot_edge.models.chart_analysis import ChartAnalysisRequest, ChartAnalysisResponse
from tradingbot_edge.services.gpt4v_service import GPT4VChartAnalyzer

router = APIRouter()

# Module-level singleton — created once when the module loads, reused for every request
analyzer = GPT4VChartAnalyzer()


@router.post("/analyze-chart", response_model=ChartAnalysisResponse)

def analyze_chart(request: ChartAnalysisRequest) -> ChartAnalysisResponse:
    """
    Analyze a stock chart image using GPT-4V.

    Args:
        request: ChartAnalysisRequest containing image_url, symbol, and optional timeframe

    Returns:
        ChartAnalysisResponse with detected patterns, sentiment, and confidence score
    """
    try:
        return analyzer.analyze_chart(
            image_url=request.image_url,
            symbol=request.symbol,
            timeframe=request.timeframe or "1D"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
