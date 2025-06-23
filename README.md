# 🤖 LuminaFi - AI-Powered Finance Analysis Workflow

A comprehensive Streamlit application that provides real-time financial analysis with AI-powered insights, interactive charts, and live news updates.

## Access the App Online

If you want to use the LuminaFi app directly in your browser, visit the Hugging Face Space:

👉 [LuminaFi on Hugging Face Spaces](https://huggingface.co/spaces/AreejMehboob17/LuminaFi)

## ✨ Features

### 📊 Real-Time Financial Data
- **Multi-stock Comparison**: Compare multiple stocks simultaneously
- **Interactive Charts**: Line and candlestick chart visualizations
- **Comprehensive Metrics**: Price, change, market cap, P/E ratios, 52-week highs/lows
- **Flexible Time Periods**: 1mo, 3mo, 6mo, 1y, 2y, 5y analysis periods

### 🤖 AI-Powered Analysis
- **Vision-Enabled AI**: Uses Together AI's vision model to analyze both data and charts
- **Comprehensive Reports**: Performance comparison, investment recommendations, risk assessment
- **Natural Language Queries**: Chat interface for financial analysis requests
- **Fallback Support**: Text-only analysis when vision processing fails

### 📰 Live Financial News
- **DuckDuckGo Integration**: Real-time financial news search
- **Clickable Links**: Direct links to full news articles
- **Multiple Search Strategies**: Financial news, stock market news, investment news, earnings reports
- **Animated News Ticker**: Real-time news updates display

### 🎨 Modern UI/UX
- **Responsive Design**: Works on desktop and mobile devices
- **Progress Tracking**: Real-time workflow progress indicators
- **Interactive Elements**: Expandable news sections, clickable links
- **Professional Styling**: Modern gradient headers and smooth animations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd LuminaFi
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8501`

## 💬 Usage Examples

### Basic Stock Comparison
```
Compare AAPL vs GOOGL vs MSFT
```

### Market Analysis
```
Analyze TSLA and NVDA performance
```

### Investment Research
```
Compare AMZN, META, and NFLX for investment
```

## 🔧 Configuration

### API Keys
- **Together AI**: Add your Together AI API key in the `FinanceWorkflow` class
- **News API**: Currently uses DuckDuckGo (no API key required)

### Customization
- **Time Periods**: Modify the time period options in the sidebar
- **Chart Types**: Switch between line and candlestick charts
- **News Sources**: Extend the news fetching to include additional sources

## 📋 Dependencies

- **streamlit**: Web application framework
- **yfinance**: Yahoo Finance data fetching
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive chart creation
- **together**: Together AI API integration
- **requests**: HTTP requests for news fetching
- **matplotlib/seaborn**: Additional visualization support

## 🛠️ Technical Architecture

### Core Components
1. **FinanceWorkflow Class**: Main business logic handler
2. **Data Fetching**: yfinance integration for real-time stock data
3. **Chart Generation**: Plotly-based interactive visualizations
4. **AI Analysis**: Together AI vision and text models
5. **News Integration**: DuckDuckGo API for financial news
6. **UI Components**: Streamlit-based responsive interface

### Data Flow
1. User input → Symbol extraction → Data fetching
2. Financial data → Chart generation → AI analysis
3. News search → Display with clickable links
4. Results → Interactive dashboard

## 🔒 Error Handling

- **Invalid Symbols**: Graceful handling of non-existent stock symbols
- **API Failures**: Fallback mechanisms for data and news fetching
- **Network Issues**: Timeout handling and retry logic
- **Data Validation**: Null value handling and type conversion

## 🚧 Known Limitations

- **Rate Limiting**: yfinance and DuckDuckGo may have rate limits
- **Symbol Validation**: Limited validation of stock symbol format
- **News Timestamps**: DuckDuckGo doesn't provide exact publication times
- **API Dependencies**: Requires active internet connection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This application is for educational and informational purposes only. It does not constitute financial advice. Always consult with a qualified financial advisor before making investment decisions.



