"""Chart Analysis Service using Claude"""
import anthropic
import base64
import io
import yfinance as yf
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — required when running in a web server thread
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import json
from ..config import get_settings
from ..models.chart_analysis import (
    ChartAnalysisResponse,
    PatternDetection
)


# Maps our timeframe strings to yfinance period and interval arguments
TIMEFRAME_MAP = {
    "1D": {"period": "1mo",  "interval": "1d"},
    "1W": {"period": "6mo",  "interval": "1wk"},
    "1M": {"period": "2y",   "interval": "1mo"},
}


class GPT4VChartAnalyzer:
    """Service for analyzing stock charts using Claude"""

    def __init__(self):
        """Initialize the Anthropic client"""
        settings = get_settings()
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.anthropic_model

    def analyze_chart(
        self,
        symbol: str,
        timeframe: str = "1D"
    ) -> ChartAnalysisResponse:
        """
        Fetch price data, generate a chart, and analyze it with Claude.

        Args:
            symbol: Stock ticker symbol (e.g., "AAPL")
            timeframe: Chart timeframe — "1D", "1W", or "1M"

        Returns:
            ChartAnalysisResponse with analysis results
        """
        image_data = self._generate_chart(symbol, timeframe)
        prompt = self._create_analysis_prompt(symbol, timeframe)
        response = self._call_claude(image_data, prompt)
        return self._parse_response(response, symbol)

    def _generate_chart(self, symbol: str, timeframe: str) -> str:
        """
        Fetch OHLCV data from yfinance and render a price chart.
        Returns the chart as a base64-encoded PNG string.
        """
        params = TIMEFRAME_MAP.get(timeframe, TIMEFRAME_MAP["1D"])
        df = yf.download(symbol, period=params["period"], interval=params["interval"], progress=False)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), gridspec_kw={"height_ratios": [3, 1]})
        fig.patch.set_facecolor("#1a1a2e")

        # .squeeze() converts a single-column DataFrame to a 1D Series
        # needed because newer yfinance versions return MultiIndex columns
        close = df["Close"].squeeze()
        volume = df["Volume"].squeeze()

        # Price line
        ax1.plot(df.index, close, color="#00d4ff", linewidth=1.5, label="Close")
        ax1.fill_between(df.index, close, close.min(), alpha=0.1, color="#00d4ff")
        ax1.set_facecolor("#16213e")
        ax1.set_title(f"{symbol} — {timeframe}", color="white", fontsize=14, pad=10)
        ax1.tick_params(colors="white")
        ax1.yaxis.label.set_color("white")
        ax1.set_ylabel("Price (USD)", color="white")
        for spine in ax1.spines.values():
            spine.set_edgecolor("#333366")
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax1.xaxis.set_major_locator(mdates.AutoDateLocator())
        plt.setp(ax1.get_xticklabels(), rotation=30, ha="right", color="white")

        # Volume bars
        ax2.bar(df.index, volume, color="#4a4a8a", width=0.8)
        ax2.set_facecolor("#16213e")
        ax2.set_ylabel("Volume", color="white")
        ax2.tick_params(colors="white")
        for spine in ax2.spines.values():
            spine.set_edgecolor("#333366")
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        plt.setp(ax2.get_xticklabels(), rotation=30, ha="right", color="white")

        plt.tight_layout()

        # Save to memory as PNG — no file written to disk
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", dpi=72, bbox_inches="tight")
        plt.close(fig)
        buffer.seek(0)

        return base64.standard_b64encode(buffer.read()).decode("utf-8")

    def _create_analysis_prompt(self, symbol: str, timeframe: str) -> str:
        """Create the prompt for Claude analysis"""
        return f"""You are an expert technical analyst. Analyze this {symbol} stock chart for the {timeframe} timeframe.

Provide your analysis in JSON format with the following structure:
{{
    "overall_analysis": "Brief summary of what you see in the chart",
    "patterns": [
        {{
            "pattern_name": "Name of pattern (e.g., Head and Shoulders, Bull Flag)",
            "confidence": 0.85,
            "description": "Detailed explanation of the pattern"
        }}
    ],
    "sentiment": "bullish, bearish, or neutral",
    "confidence_score": 0.8
}}

Focus on:
- Key support and resistance levels
- Trend direction and strength
- Chart patterns (triangles, flags, head & shoulders, etc.)
- Volume analysis if visible
- Overall bullish/bearish sentiment

Return ONLY valid JSON with no markdown, no code fences, and no additional text."""

    def _call_claude(self, image_data: str, prompt: str) -> str:
        """Send the base64 chart image and prompt to Claude"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_data
                            }
                        },
                        {"type": "text", "text": prompt}
                    ]
                }
            ]
        )

        return next(block.text for block in response.content if block.type == "text")

    def _parse_response(self, response: str, symbol: str) -> ChartAnalysisResponse:
        """Parse Claude's response into structured format"""
        try:
            # Strip markdown code fences if Claude wrapped the JSON in ```json ... ```
            cleaned = response.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            data = json.loads(cleaned)

            patterns = [
                PatternDetection(
                    pattern_name=p["pattern_name"],
                    confidence=p["confidence"],
                    description=p["description"]
                )
                for p in data.get("patterns", [])
            ]

            return ChartAnalysisResponse(
                symbol=symbol,
                analysis=data.get("overall_analysis", ""),
                patterns=patterns,
                sentiment=data.get("sentiment", "neutral"),
                confidence_score=data.get("confidence_score", 0.5),
                timestamp=datetime.now()
            )

        except json.JSONDecodeError:
            return ChartAnalysisResponse(
                symbol=symbol,
                analysis=response,
                patterns=[],
                sentiment="neutral",
                confidence_score=0.0,
                timestamp=datetime.now()
            )
