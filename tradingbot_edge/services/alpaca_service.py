"""Alpaca Trading Service"""
import alpaca_trade_api as tradeapi
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from math import floor
from ..config import get_settings
from ..models.chart_analysis import ChartAnalysisResponse, TradeDecision, TradeAction, PortfolioScanResponse

# Minimum confidence required to place a real order — below this we hold
CONFIDENCE_THRESHOLD = 0.8

# Maximum percentage of portfolio to allocate to a single trade
RISK_PER_TRADE = 0.05  # 5%

# Tickers from the user's Webull portfolio — scanned in parallel by scan()
PORTFOLIO_TICKERS = [
    "GEV", "CRWV", "MU", "CRCL", "SNDK", "TQQQ", "TSM", "AAPL", "SOXX", "MSFT",
    "EEM", "GOOGL", "AMZN", "VONG", "RRX", "SYF", "SOFI", "TSLA", "LI", "NVDA",
    "VOO", "CAVA", "JPM", "ABT", "C", "COF", "GEHC", "GE",
]


class AlpacaTrader:
    """Service for executing trades on Alpaca paper trading"""

    def __init__(self):
        """Initialize the Alpaca client"""
        settings = get_settings()
        self.api = tradeapi.REST(
            key_id=settings.alpaca_api_key,
            secret_key=settings.alpaca_api_secret,
            base_url=settings.alpaca_base_url
        )

    def execute(self, analysis: ChartAnalysisResponse) -> TradeDecision:
        """
        Evaluate a chart analysis and place a trade if confidence is high enough.

        Args:
            analysis: ChartAnalysisResponse from the chart analyzer

        Returns:
            TradeDecision describing what action was taken and why
        """
        action, reason = self._decide(analysis)

        if action == TradeAction.HOLD:
            return TradeDecision(
                symbol=analysis.symbol,
                action=action,
                quantity=0,
                reason=reason,
                order_id=None,
                confidence_score=analysis.confidence_score,
                timestamp=datetime.now()
            )

        quantity = self._calculate_quantity(analysis.symbol)

        if quantity == 0:
            return TradeDecision(
                symbol=analysis.symbol,
                action=TradeAction.HOLD,
                quantity=0,
                reason="Insufficient buying power to purchase at least 1 share",
                order_id=None,
                confidence_score=analysis.confidence_score,
                timestamp=datetime.now()
            )

        order_id = self._place_order(analysis.symbol, action, quantity)

        return TradeDecision(
            symbol=analysis.symbol,
            action=action,
            quantity=quantity,
            reason=reason,
            order_id=order_id,
            confidence_score=analysis.confidence_score,
            timestamp=datetime.now()
        )

    def _decide(self, analysis: ChartAnalysisResponse) -> tuple[TradeAction, str]:
        """
        Apply decision rules to the analysis.

        Returns a (action, reason) tuple.
        """
        if analysis.confidence_score < CONFIDENCE_THRESHOLD:
            return (
                TradeAction.HOLD,
                f"Confidence {analysis.confidence_score:.0%} is below threshold {CONFIDENCE_THRESHOLD:.0%} — no trade placed"
            )

        if analysis.sentiment == "bullish":
            return (
                TradeAction.BUY,
                f"Bullish sentiment with {analysis.confidence_score:.0%} confidence"
            )

        if analysis.sentiment == "bearish":
            return (
                TradeAction.SELL,
                f"Bearish sentiment with {analysis.confidence_score:.0%} confidence"
            )

        return (
            TradeAction.HOLD,
            "Neutral sentiment — no trade placed"
        )

    def _get_portfolio_value(self) -> float:
        """Fetch current total portfolio value from Alpaca"""
        account = self.api.get_account()
        return float(account.portfolio_value)

    def _get_current_price(self, symbol: str) -> float:
        """Fetch the latest trade price for a symbol from Alpaca"""
        latest_trade = self.api.get_latest_trade(symbol)
        return float(latest_trade.price)

    def _calculate_quantity(self, symbol: str) -> int:
        """
        Calculate how many shares to buy based on portfolio value and risk percentage.

        Formula: floor((portfolio_value * RISK_PER_TRADE) / current_price)
        """
        portfolio_value = self._get_portfolio_value()
        current_price = self._get_current_price(symbol)
        return floor((portfolio_value * RISK_PER_TRADE) / current_price)

    def _place_order(self, symbol: str, action: TradeAction, quantity: int) -> str:
        """
        Submit a market order to Alpaca.

        Returns the Alpaca order ID.
        """
        order = self.api.submit_order(
            symbol=symbol,
            qty=quantity,
            side=action.value,
            type="market",
            time_in_force="day"
        )
        return order.id

    def scan(self, analyzer, timeframe: str = "1D") -> PortfolioScanResponse:
        """
        Analyze all portfolio tickers concurrently and execute trades for those meeting
        the confidence threshold. Results are sorted by confidence score descending.

        Args:
            analyzer: GPT4VChartAnalyzer instance for chart generation and Claude calls
            timeframe: Chart timeframe applied to every ticker — "1D", "1W", or "1M"

        Returns:
            PortfolioScanResponse with all trade decisions sorted by confidence score
        """
        def analyze_one(symbol: str) -> TradeDecision:
            analysis = analyzer.analyze_chart(symbol=symbol, timeframe=timeframe)
            return self.execute(analysis)

        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(analyze_one, ticker): ticker for ticker in PORTFOLIO_TICKERS}
            for future in as_completed(futures):
                ticker = futures[future]
                try:
                    results.append(future.result())
                except Exception as e:
                    results.append(TradeDecision(
                        symbol=ticker,
                        action=TradeAction.HOLD,
                        quantity=0,
                        reason=f"Scan error: {e}",
                        order_id=None,
                        confidence_score=0.0,
                        timestamp=datetime.now()
                    ))

        results.sort(key=lambda d: d.confidence_score or 0.0, reverse=True)

        return PortfolioScanResponse(
            timeframe=timeframe,
            total_scanned=len(results),
            results=results,
            timestamp=datetime.now()
        )
