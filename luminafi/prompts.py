"""
Collection of prompts used for LLM interactions in LuminaFi.
"""

SYSTEM_FINANCIAL_ANALYST = """You are a professional financial analyst with expertise in stock market analysis, \
investment strategies, and risk assessment. You can analyze both numerical data and financial charts. \
Provide detailed, actionable financial insights based on both the data and the visual chart patterns you observe."""

SYSTEM_SYMBOL_EXTRACTOR = """You are a financial data assistant to extract symbols from user query."""

SYMBOL_EXTRACTION_PROMPT = """Extract all stock ticker symbols (US stocks, ETFs, or crypto tickers) for yfinance \
from the following user query. Return ONLY a JSON array of strings, e.g. ["AAPL", "MSFT", "TSLA"].

User query: {query}"""

def generate_analysis_prompt(data: dict, user_query: str) -> str:
    """Generate prompt for financial analysis based on data and user query."""
    prompt = f'''
    Analyze the following financial data for the user query: "{user_query}"
    
    Financial Data Summary:
    '''
    
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

def generate_vision_prompt(prompt: str) -> str:
    """Add vision-specific instructions to the analysis prompt."""
    return prompt + "\n\nAdditionally, I'm providing you with a financial chart visualization of this data. \
Please analyze the visual patterns, trends, and technical indicators you can observe in the chart along with the numerical data." 