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
    
    def _call_gpt4v(self,image_url:str, prompt:str) -> str:
        """Call OPENAI GPT-4v API"""
        response = self.client.chat.completions.create(
            model = "gpt-4o",
            messages =[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content

    def _parse_response(self, response:str, symbol:str) -> ChartAnalysisResponse:
        """Parse GPT-4V response into structured format"""
        try:
            # Parse JSON from GPT-4V response
            data = json.loads(response)
            
            # Extract patterns and convert to PatternDetection objects
            patterns = [
                PatternDetection(pattern_name = p["pattern_name"], confidence = p["confidence"],description = p["description"])
                for p in data.get("patterns",[])
            ]
            
            
            
            return ChartAnalysisResponse(
                symbol=symbol,
                analysis=data.get("overall_analysis",""),  # Get from data
                patterns=patterns,
                sentiment=data.get("sentiment","neutral"),  # Get from data
                confidence_score=data.get("confidence_score",.5),  # Get from data
                timestamp=datetime.now()
            )
            
        except json.JSONDecodeError:
            return ChartAnalysisResponse(
                symbol=symbol,
                analysis=response,  # Use raw response as fallback
                patterns=[],  # Empty list
                sentiment="neutral",
                confidence_score=0.0,
                timestamp=datetime.now()
            )