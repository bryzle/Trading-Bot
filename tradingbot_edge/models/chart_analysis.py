from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TradeAction(str, Enum):
    BUY  = "buy"
    SELL = "sell"
    HOLD = "hold"

class ChartAnalysisRequest(BaseModel):
    """Request Model for Chart Analysis"""
    symbol: str = Field(..., description="Stock Symbol")
    timeframe: Optional[str] = Field(None, description="time frame chosen for stock")
    
    
class PatternDetection(BaseModel):
    """Detected chart Pattern"""
    pattern_name: str = Field(..., description="Name of the detected pattern")
    confidence: float = Field(..., description = "Confidence score from detected pattern")
    description: str = Field(..., description = "Explanation of the detected pattern")
    
class ChartAnalysisResponse(BaseModel):
    symbol: str = Field(..., description="Stock Symbol")
    analysis: str = Field(..., description="Stock Analysis Response")
    patterns: List[PatternDetection] = Field(..., description="List of detected patterns")
    sentiment: str = Field(..., description="Sentiment value")
    confidence_score: float = Field(..., description="Confidence Score")
    timestamp: datetime = Field(..., description="Transaction Time")


class TradeDecision(BaseModel):
    symbol: str = Field(..., description="Stock Symbol")
    action: TradeAction = Field(..., description="Trade action: buy, sell, or hold")
    quantity: int = Field(..., description="Number of shares")
    reason: str = Field(..., description="Why this action was taken")
    order_id: Optional[str] = Field(None, description="Alpaca order ID if an order was placed")
    confidence_score: Optional[float] = Field(None, description="Claude's confidence score for this decision")
    timestamp: datetime = Field(..., description="When the decision was made")


class PortfolioScanRequest(BaseModel):
    timeframe: Optional[str] = Field(None, description="Chart timeframe for all tickers")


class PortfolioScanResponse(BaseModel):
    timeframe: str = Field(..., description="Timeframe used for analysis")
    total_scanned: int = Field(..., description="Number of tickers analyzed")
    results: List[TradeDecision] = Field(..., description="Trade decisions sorted by confidence score")
    timestamp: datetime = Field(..., description="When the scan was run")