"""GPT-4V Service for Chart Pattern Analysis"""
import os
from openai import OpenAI
from typing import List,Dict,Any
from datetime import datetime
import json
from ..config import get_settings
from ..models.chart_analysis import(
    ChartAnalysisResponse,
    PatternDetection
)

class GPT4VChartAnalyzer:
    """Service for analyzing stock charts using GPT-4V"""
    
    def __init__(self):
        """Initialize the OpenAI client"""
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        
    
    def analyze_chart(
        self, 
        image_url: str, 
        symbol: str, 
        timeframe: str = "1D"
    ) -> ChartAnalysisResponse:
        """
        Analyze a stock chart image using GPT-4V
        
        Args:
            image_url: URL of the chart image
            symbol: Stock ticker symbol
            timeframe: Chart timeframe (e.g., "1D", "1W", "1M")
            
        Returns:
            ChartAnalysisResponse with analysis results
        """
        # TODO: Step 1 - Create the prompt for GPT-4V
        prompt = self._create_analysis_prompt(symbol, timeframe)
        
        # TODO: Step 2 - Call OpenAI API with image
        response = self._call_gpt4v(image_url, prompt)
        
        # TODO: Step 3 - Parse the response
        analysis_data = self._parse_response(response, symbol)
        
        return analysis_data
    
    def _create_analysis_prompt(self, symbol: str, timeframe: str) -> str:
        """Create the prompt for GPT-4V analysis"""
        prompt = f"""You are an expert technical analyst. Analyze this {symbol} stock chart for the {timeframe} timeframe.

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

        Return ONLY valid JSON, no additional text."""

        return prompt

    