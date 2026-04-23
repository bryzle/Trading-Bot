"""
API v1 route handlers
"""
from fastapi import APIRouter, HTTPException
from tradingbot_edge.models.chart_analysis import ChartAnalysisRequest, ChartAnalysisResponse, TradeDecision, PortfolioScanRequest, PortfolioScanResponse
from tradingbot_edge.services.gpt4v_service import GPT4VChartAnalyzer
from tradingbot_edge.services.alpaca_service import AlpacaTrader

router = APIRouter()

# Singletons — created once when the module loads, reused for every request
analyzer = GPT4VChartAnalyzer()
trader = AlpacaTrader()


@router.post("/analyze-chart", response_model=ChartAnalysisResponse)
def analyze_chart(request: ChartAnalysisRequest) -> ChartAnalysisResponse:
    """
    Analyze a stock chart using Claude vision.

    Args:
        request: ChartAnalysisRequest containing symbol and optional timeframe

    Returns:
        ChartAnalysisResponse with detected patterns, sentiment, and confidence score
    """
    try:
        return analyzer.analyze_chart(
            symbol=request.symbol,
            timeframe=request.timeframe or "1D"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute-trade", response_model=TradeDecision)
def execute_trade(request: ChartAnalysisRequest) -> TradeDecision:
    """
    Analyze a stock chart and execute a trade on Alpaca paper trading.

    Args:
        request: ChartAnalysisRequest containing symbol and optional timeframe

    Returns:
        TradeDecision with the action taken and Alpaca order ID if an order was placed
    """
    try:
        analysis = analyzer.analyze_chart(
            symbol=request.symbol,
            timeframe=request.timeframe or "1D"
        )
        return trader.execute(analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scan-portfolio", response_model=PortfolioScanResponse)
def scan_portfolio(request: PortfolioScanRequest) -> PortfolioScanResponse:
    """
    Analyze all 28 portfolio tickers concurrently and execute trades for those
    meeting the confidence threshold. Results are sorted by confidence score descending.

    Args:
        request: PortfolioScanRequest with optional timeframe (defaults to "1D")

    Returns:
        PortfolioScanResponse with trade decisions for every ticker, sorted by confidence
    """
    try:
        return trader.scan(
            analyzer=analyzer,
            timeframe=request.timeframe or "1D"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
