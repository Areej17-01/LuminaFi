import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json
import time
import streamlit as st

import base64
from typing import Dict, List, Any, Optional, Union, Iterator
import io
import matplotlib.pyplot as plt
import seaborn as sns
from together import Together
import os
from dotenv import load_dotenv
from . import prompts

# Load environment variables from .env file
load_dotenv()

class FinanceWorkflow:
    def __init__(self):
        # Load Together API key from environment
        together_api_key = os.getenv("TOGETHER_API_KEY")
        if not together_api_key:
            raise ValueError("TOGETHER_API_KEY not found in environment. Please set it in your .env file.")
        # Initialize Together AI client
        self.together_client = Together(api_key=together_api_key)
        
    def fetch_financial_data(self, symbols: List[str], period: str = "1y") -> Dict:
        """Fetch financial data using yfinance"""
        data = {}
        
        with st.spinner("🔍 Fetching financial data..."):
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period=period)
                    info = ticker.info
                    
                    current_price = hist['Close'].iloc[-1] if not hist.empty else None
                    price_change = 0
                    price_change_pct = 0
                    
                    if len(hist) > 1 and current_price is not None:
                        first_price = hist['Close'].iloc[0]
                        if first_price and first_price != 0:
                            price_change = current_price - first_price
                            price_change_pct = (price_change / first_price) * 100
                    
                    data[symbol] = {
                        'history': hist,
                        'info': info,
                        'current_price': current_price,
                        'price_change': price_change,
                        'price_change_pct': price_change_pct
                    }
                except Exception as e:
                    print(f"Error fetching data for {symbol}: {str(e)}")
                    data[symbol] = None
                    
        return data
    
    def create_comparison_chart(self, data: Dict, chart_type: str = "line") -> go.Figure:
        """Create comparison chart using Plotly"""
        fig = go.Figure()
        
        colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
        
        for i, (symbol, symbol_data) in enumerate(data.items()):
            if symbol_data and not symbol_data['history'].empty:
                if chart_type == "line":
                    fig.add_trace(go.Scatter(
                        x=symbol_data['history'].index,
                        y=symbol_data['history']['Close'],
                        mode='lines',
                        name=symbol,
                        line=dict(color=colors[i % len(colors)], width=2),
                        hovertemplate=f'<b>{symbol}</b><br>Date: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>'
                    ))
                elif chart_type == "candlestick":
                    fig.add_trace(go.Candlestick(
                        x=symbol_data['history'].index,
                        open=symbol_data['history']['Open'],
                        high=symbol_data['history']['High'],
                        low=symbol_data['history']['Low'],
                        close=symbol_data['history']['Close'],
                        name=symbol
                    ))
        
        fig.update_layout(
            title="Financial Data Comparison",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            template="plotly_white",
            hovermode='x unified',
            height=500
        )
        
        return fig
    
    def chart_to_base64(self, fig) -> str:
        """Convert Plotly chart to base64 image for vision LLM"""
        try:
            # Convert plotly figure to image bytes
            img_bytes = fig.to_image(format="png", width=1200, height=600)
            # Convert to base64
            img_base64 = base64.b64encode(img_bytes).decode()
            return img_base64
        except Exception as e:
            print(f"Error converting chart to image: {str(e)}")
            return ""
    
    def generate_analysis_prompt(self, data: Dict, user_query: str) -> str:
        """Generate prompt for LLM analysis"""
        prompt = f"""
        Analyze the following financial data for the user query: "{user_query}"
        
        Financial Data Summary:
        """
        
        for symbol, symbol_data in data.items():
            if symbol_data and symbol_data['current_price'] is not None:
                current_price = symbol_data['current_price']
                price_change = symbol_data['price_change']
                price_change_pct = symbol_data['price_change_pct']
                market_cap = symbol_data['info'].get('marketCap', 'N/A')
                pe_ratio = symbol_data['info'].get('trailingPE', 'N/A')
                week_52_high = symbol_data['info'].get('fiftyTwoWeekHigh', 'N/A')
                week_52_low = symbol_data['info'].get('fiftyTwoWeekLow', 'N/A')
                
                prompt += f"""
                {symbol}:
                - Current Price: ${current_price:.2f}
                - Price Change: ${price_change:.2f} ({price_change_pct:.2f}%)
                - Market Cap: {market_cap if market_cap != 'N/A' else 'N/A'}
                - P/E Ratio: {pe_ratio if pe_ratio != 'N/A' else 'N/A'}
                - 52 Week High: ${week_52_high if isinstance(week_52_high, (int, float)) else 'N/A'}
                - 52 Week Low: ${week_52_low if isinstance(week_52_low, (int, float)) else 'N/A'}
                """
            elif symbol_data:
                prompt += f"""
                {symbol}:
                - Status: Data available but current price unavailable
                - Historical data points: {len(symbol_data['history']) if not symbol_data['history'].empty else 0}
                """
            else:
                prompt += f"""
                {symbol}:
                - Status: Unable to fetch data for this symbol
                """
        
        prompt += """
        Please provide a detailed financial analysis including:
        1. Performance comparison between the securities
        2. Key financial metrics analysis
        3. Investment recommendations
        4. Risk assessment
        5. Market outlook and trends
        
        Make the analysis comprehensive and actionable for investors.
        """
        
        return prompt
    
    def extract_symbols_llm(self, user_query: str):
        """Use Together LLM to extract stock symbols from user query. Returns a list of symbols."""
        try:
            response = self.together_client.chat.completions.create(
                model="meta-llama/Llama-Vision-Free",
                messages=[
                    {"role": "system", "content": prompts.SYSTEM_SYMBOL_EXTRACTOR},
                    {"role": "user", "content": prompts.SYMBOL_EXTRACTION_PROMPT.format(query=user_query)}
                ],
                max_tokens=100,
                temperature=0.0,
                stream=False
            )
            
            if not isinstance(response, str):
                print("Unexpected response type from Together API")
                return []
                
            # Try to extract JSON from the response
            text = response.strip()
            # Find the first [ and last ] to extract the JSON array
            start = text.find('[')
            end = text.rfind(']')
            if start != -1 and end != -1:
                try:
                    symbols = json.loads(text[start:end+1])
                    # Filter to only valid symbol-like strings
                    symbols = [s for s in symbols if isinstance(s, str) and 1 <= len(s) <= 6 and s.isalnum()]
                    return symbols
                except json.JSONDecodeError:
                    print("Failed to parse symbols JSON response")
                    return []
            return []
        except Exception as e:
            print(f"LLM symbol extraction failed, falling back to regex. Error: {e}")
            return []

    def call_together_ai_with_vision(self, data: Dict, user_query: str, chart_base64: str):
        """Call Together AI Vision API with both text data and chart image, streaming response to UI."""
        try:
            # Generate the analysis prompt
            analysis_prompt = prompts.generate_analysis_prompt(data, user_query)
            vision_prompt = prompts.generate_vision_prompt(analysis_prompt)
            
            # Prepare messages for vision model
            messages = [
                {
                    "role": "system",
                    "content": prompts.SYSTEM_FINANCIAL_ANALYST
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": vision_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{chart_base64}"
                            }
                        }
                    ]
                }
            ]
            
            # Stream response
            response_stream = self.together_client.chat.completions.create(
                model="meta-llama/Llama-Vision-Free",
                messages=messages,
                max_tokens=3000,
                temperature=0.3,
                stream=True
            )
            
            return response_stream
            
        except Exception as e:
            print(f"Error in vision analysis: {str(e)}")
            return None

    def call_together_ai_text_only(self, data: Dict, user_query: str):
        """Fallback method for text-only analysis"""
        try:
            # Generate the analysis prompt
            analysis_prompt = prompts.generate_analysis_prompt(data, user_query)
            
            response = self.together_client.chat.completions.create(
                model="meta-llama/Llama-3.2-3B-Instruct-Turbo",
                messages=[
                    {
                        "role": "system",
                        "content": prompts.SYSTEM_FINANCIAL_ANALYST
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                max_tokens=2000,
                temperature=0.3,
                stream=False
            )
            
            if not isinstance(response, str):
                return self._get_fallback_analysis()
                
            return response or self._get_fallback_analysis()
            
        except Exception as e:
            print(f"Error in fallback analysis: {str(e)}")
            return self._get_fallback_analysis()

    def _get_fallback_analysis(self) -> str:
        """Return a fallback analysis when API calls fail."""
        return """
        ## Financial Analysis Report
        
        *Analysis temporarily unavailable due to API limitations. Please try again.*
        
        Based on the provided financial data, here's a basic analysis framework:
        
        ### Performance Overview
        Review the price movements and percentage changes for each security.
        
        ### Key Metrics to Consider
        - Price-to-Earnings ratios
        - Market capitalization
        - 52-week highs and lows
        - Trading volume patterns
        
        ### General Investment Principles
        1. Diversification across sectors and asset classes
        2. Regular portfolio rebalancing
        3. Long-term perspective for equity investments
        4. Risk management through position sizing
        
        *Note: This is general information only and not personalized financial advice.*
        """
    
    def fetch_financial_news(self, query: str) -> List[Dict]:
        """Fetch recent financial news and research using yfinance Search API for each symbol in the query."""
        from datetime import datetime
        news_results = []
        import re
        symbols = re.findall(r'\b[A-Z0-9]{1,6}\b', query.upper())
        seen_urls = set()
        for symbol in symbols:
            try:
                # Fetch news
                s = yf.Search(symbol, news_count=10)
                news_items = getattr(s, 'news', [])
                for item in news_items:
                    url = item.get('link') or item.get('url')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        news_results.append({
                            'title': item.get('title', f"{symbol} News"),
                            'description': item.get('publisher', '') + (': ' + item.get('summary', '') if item.get('summary') else ''),
                            'url': url,
                            'publishedAt': item.get('providerPublishTime') or item.get('published_at') or datetime.now().isoformat()
                        })
                # Fetch research (if available)
                s_research = yf.Search(symbol, include_research=True)
                research_items = getattr(s_research, 'research', [])
                for item in research_items:
                    url = item.get('link') or item.get('url')
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        news_results.append({
                            'title': item.get('title', f"{symbol} Research"),
                            'description': item.get('publisher', '') + (': ' + item.get('summary', '') if item.get('summary') else ''),
                            'url': url,
                            'publishedAt': item.get('providerPublishTime') or item.get('published_at') or datetime.now().isoformat()
                        })
            except Exception as e:
                print(f"Error fetching news/research for {symbol}: {e}")
                continue
        if not news_results:
            news_results.append({
                'title': f"No news found for {query}",
                'description': '',
                'url': '',
                'publishedAt': datetime.now().isoformat()
            })
        return news_results