from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChartAnalysisRequest(BaseModel):
    """Request Model for Chart Analysis"""
    image_url: str = Field(..., description="URL of the Chart Image")
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
    timestamp: datetime = Field(...,description = "Transaction Time")