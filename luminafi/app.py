import streamlit as st
import threading
from luminafi.finance_workflow import FinanceWorkflow
from luminafi.utils import sanitize_markdown
import pandas as pd

st.set_page_config(
    page_title="AI Finance Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for animations and styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .news-ticker {
        overflow: hidden;
        white-space: nowrap;
        background: linear-gradient(90deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 300% 100%;
        animation: gradientShift 8s ease infinite;
        color: white;
        padding: 12px;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 2px solid rgba(255,255,255,0.2);
    }
    .news-ticker-content {
        display: inline-block;
        animation: ticker 25s linear infinite;
        font-weight: 600;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    @keyframes ticker {
        0% { transform: translate3d(100%, 0, 0); }
        100% { transform: translate3d(-100%, 0, 0); }
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
</style>
""", unsafe_allow_html=True)

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'workflow_data' not in st.session_state:
    st.session_state.workflow_data = {}

def main():
    st.markdown("""
    <div class="main-header">
        <h1>🤖 AI-Powered Finance Analysis Workflow</h1>
        <p>Comprehensive financial analysis with real-time data, AI insights, and news updates</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ About LuminaFi", expanded=False):
        st.markdown(
            """
            **About LuminaFi**
            
            LuminaFi is an AI-powered financial analysis app. Enter your stock or ETF comparison queries (e.g., 'Compare AAPL vs MSFT'), and LuminaFi will:
            
            - Extract and validate ticker symbols using AI
            - Fetch historical price and key financial data from Yahoo Finance
            - Generate interactive charts for visual comparison
            - Use advanced AI models to provide detailed, actionable financial analysis
            - Fetch and display the latest real news and research headlines for your selected symbols
            
            **Analysis Parameters:**
            
            Use the **Analysis Parameters** section in the sidebar to adjust the time period and chart type for your analysis. This lets you customize the data range and visualization style to fit your needs.
            
            This app is designed for investors, analysts, and anyone interested in deep, AI-driven insights into stocks and markets. It does not provide live streaming prices, but focuses on robust, explainable, and up-to-date analysis.
            """
        )

    user_query = None
    workflow_running = False
    if 'user_input' in st.session_state:
        user_query = st.session_state['user_input']
        workflow_running = True
    elif st.session_state.messages:
        last_user_message = next((m['content'] for m in reversed(st.session_state.messages) if m['role'] == 'user'), None)
        if last_user_message:
            user_query = last_user_message
    if workflow_running and user_query:
        st.markdown(f"""
        <div style='background: #ff9800; border-left: 6px solid #ff9800; color: white; padding: 1.2rem 1rem; border-radius: 10px; margin-bottom: 1.5rem; font-size: 1.3rem; font-weight: 600;'>
            🔎 Searching for: {user_query}
        </div>
        """, unsafe_allow_html=True)
    elif user_query:
        st.markdown(f"""
        <div style='background: #f0f2f6; border-left: 6px solid #2196f3; padding: 1.2rem 1rem; border-radius: 10px; margin-bottom: 1.5rem; font-size: 1.3rem; font-weight: 600;'>
            <span style='color:#2196f3;'>Current Query:</span> {user_query}
        </div>
        """, unsafe_allow_html=True)

    workflow = FinanceWorkflow()

    with st.sidebar:
        st.header("⚙️ Configuration")
        if st.button("💻 Get Code", help="View the LuminaFi source code on GitHub"):
            st.markdown("""
            <div style='padding: 1rem; background: #f0f2f6; border-radius: 8px; margin-bottom: 1rem;'>
                <strong>GitHub Repository:</strong><br>
                <input type='text' value='https://github.com/Areej17-01/LuminaFi' id='github-url' readonly style='width: 90%; padding: 0.3rem; border-radius: 4px; border: 1px solid #ccc; margin-top: 0.5rem;'>
                <button onclick="navigator.clipboard.writeText('https://github.com/Areej17-01/LuminaFi')" style='margin-left: 0.5rem; padding: 0.3rem 0.7rem; border-radius: 4px; border: none; background: #2196f3; color: white; font-weight: 600; cursor: pointer;'>Copy</button>
                <a href='https://github.com/Areej17-01/LuminaFi' target='_blank' style='display: inline-block; margin-top: 0.7rem; padding: 0.3rem 0.7rem; border-radius: 4px; background: #43a047; color: white; text-decoration: none; font-weight: 600;'>Go to GitHub</a>
            </div>
            """, unsafe_allow_html=True)
        st.subheader("Analysis Parameters")
        time_period = st.selectbox(
            "Time Period",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3
        )
        chart_type = st.selectbox(
            "Chart Type",
            ["line", "candlestick"],
            index=0
        )
        st.subheader("Workflow Status")
        if st.session_state.workflow_data:
            st.success("✅ Data loaded")
            if 'analysis' in st.session_state.workflow_data:
                st.success("✅ Analysis complete")
            if 'news' in st.session_state.workflow_data:
                st.success("✅ News fetched")

    st.subheader("💬 Financial Analysis Chat")
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>AI Assistant:</strong> {message["content"]}
                </div>
                """, unsafe_allow_html=True)
    user_input = st.chat_input("Enter your financial comparison query (e.g., 'Compare AAPL vs GOOGL vs MSFT')")
    if user_input:
        user_input_to_keep = user_input
        st.session_state.clear()
        st.session_state['user_input'] = user_input_to_keep
        st.rerun()
    if 'user_input' in st.session_state:
        user_input = st.session_state.pop('user_input')
        st.session_state.messages = []
        st.session_state.workflow_data = {}
        symbols = workflow.extract_symbols_llm(user_input)
        if symbols is None:
            st.error("LLM symbol extraction failed. Please try again or use a different query.")
            st.stop()
        if not symbols:
            import re
            symbols = re.findall(r'\b[A-Z0-9]{1,5}\b', re.sub(r'[^A-Z0-9\s]', '', user_input.upper()))
            common_words = {'THE', 'AND', 'OR', 'FOR', 'WITH', 'VS', 'VERSUS', 'COMPARE', 'ANALYZE', 'STOCK', 'STOCKS'}
            symbols = [symbol for symbol in symbols if symbol not in common_words and len(symbol) >= 1]
        if not symbols:
            st.error("Please include valid stock symbols in your query (e.g., 'Compare AAPL vs GOOGL vs MSFT' or 'Analyze TSLA and NVDA')")
            st.stop()
        if len(symbols) > 10:
            st.warning(f"Too many symbols ({len(symbols)}). Limiting to first 10 symbols.")
            symbols = symbols[:10]
        st.session_state.workflow_data['news'] = []
        if symbols:
            with st.spinner("Fetching news for first symbol..."):
                first_symbol_news = workflow.fetch_financial_news(symbols[0])
                st.session_state.workflow_data['news'] = first_symbol_news
        st.subheader("📰 Latest Financial News")
        news_list = st.session_state.workflow_data.get('news', [])
        ticker_headlines = news_list[:5]
        news_text = " | ".join([f"{article['title']}" for article in ticker_headlines])
        ticker_content = f"📈 <strong>BREAKING NEWS:</strong> {news_text}"
        st.markdown(f"""
        <div class="news-ticker">
            <div class="news-ticker-content" style='animation: ticker 25s linear infinite;'>
                {ticker_content}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if not news_list:
            st.info("No news available.")
        st.markdown("<h4 style='margin-top:2rem; color:#333;'>Learn more about the latest articles:</h4>", unsafe_allow_html=True)
        from datetime import datetime as dt
        for idx, article in enumerate(news_list[:5], 1):
            pub_date = article.get('publishedAt', '')
            try:
                pub_date_fmt = dt.fromtimestamp(int(pub_date)).strftime('%Y-%m-%d %H:%M')
            except Exception:
                try:
                    pub_date_fmt = dt.fromisoformat(pub_date).strftime('%Y-%m-%d %H:%M')
                except Exception:
                    pub_date_fmt = str(pub_date)
            expander_label = f'📰 {idx}. {article["title"]}'
            with st.expander(expander_label, expanded=False):
                if article.get('description'):
                    st.markdown(f"<span style='color:#555;'>{article['description']}</span>", unsafe_allow_html=True)
                if article.get('url'):
                    st.markdown(f'<a href="{article["url"]}" target="_blank" style="color:#2196f3; font-weight:600; text-decoration:none;">🔗 Read Full Article</a>', unsafe_allow_html=True)
                st.markdown(f'<span style="color:#888; font-size:0.95rem;">📅 Published: {pub_date_fmt}</span>', unsafe_allow_html=True)
        def fetch_remaining_news(symbols, initial_news):
            all_news = list(initial_news)
            for symbol in symbols[1:]:
                try:
                    news = workflow.fetch_financial_news(symbol)
                    all_news.extend(news)
                    st.session_state.workflow_data['news'] = all_news
                    st.rerun()
                except Exception as e:
                    print(f"Error fetching news for {symbol}: {e}")
            st.session_state.workflow_data['news'] = all_news
        if len(symbols) > 1:
            threading.Thread(target=fetch_remaining_news, args=(symbols, first_symbol_news), daemon=True).start()
        col1, col2 = st.columns([2, 1])
        with col2:
            st.subheader("🔄 Workflow Progress")
            progress_bar = st.progress(0)
            status_container = st.empty()
        with col1:
            with status_container:
                st.markdown("""
                <div class="workflow-step">
                    <strong>Step 1:</strong> Fetching financial data from yfinance...
                </div>
                """, unsafe_allow_html=True)
            progress_bar.progress(20)
            financial_data = workflow.fetch_financial_data(symbols, time_period)
            st.session_state.workflow_data['financial_data'] = financial_data
            with status_container:
                st.markdown("""
                <div class="workflow-step">
                    <strong>Step 2:</strong> Creating comparison visualization...
                </div>
                """, unsafe_allow_html=True)
            progress_bar.progress(40)
            chart = None
            chart_base64 = None
            if any(data for data in financial_data.values() if data):
                chart = workflow.create_comparison_chart(financial_data, chart_type)
                st.plotly_chart(chart, use_container_width=True)
                st.session_state.workflow_data['chart'] = chart
                chart_base64 = workflow.chart_to_base64(chart)
                if chart_base64:
                    st.success("✅ Chart converted for AI vision analysis")
            with status_container:
                st.markdown("""
                <div class="workflow-step">
                    <strong>Step 3:</strong> Generating AI analysis with chart vision...
                </div>
                """, unsafe_allow_html=True)
            progress_bar.progress(60)
            if 'analysis' not in st.session_state.workflow_data:
                # Use vision LLM with chart image if available, otherwise fallback to text-only analysis
                if chart_base64:
                    response_stream = workflow.call_together_ai_with_vision(financial_data, user_input, chart_base64)
                    output_placeholder = st.empty()
                    streamed_text = ""
                    if response_stream:
                        for chunk in response_stream:
                            if hasattr(chunk, 'choices') and chunk.choices and hasattr(chunk.choices[0], 'delta'):
                                delta = getattr(chunk.choices[0].delta, "content", None)
                                if delta:
                                    streamed_text += delta
                                    output_placeholder.markdown(streamed_text)
                    analysis = sanitize_markdown(streamed_text)
                else:
                    analysis = workflow.call_together_ai_text_only(financial_data, user_input)
                    analysis = sanitize_markdown(analysis)
                st.session_state.workflow_data['analysis'] = analysis
            else:
                analysis = st.session_state.workflow_data['analysis']
            progress_bar.progress(100)
            st.subheader("📊 AI Analysis")
            st.markdown(analysis)
            with status_container:
                st.success("✅ Workflow completed successfully!")
    if st.session_state.workflow_data and 'financial_data' in st.session_state.workflow_data:
        st.subheader("📋 Data Summary")
        summary_data = []
        for symbol, data in st.session_state.workflow_data['financial_data'].items():
            if data and data['current_price'] is not None:
                market_cap = data['info'].get('marketCap', 'N/A')
                if isinstance(market_cap, (int, float)):
                    if market_cap >= 1e12:
                        market_cap_str = f"${market_cap/1e12:.2f}T"
                    elif market_cap >= 1e9:
                        market_cap_str = f"${market_cap/1e9:.2f}B"
                    elif market_cap >= 1e6:
                        market_cap_str = f"${market_cap/1e6:.2f}M"
                    else:
                        market_cap_str = f"${market_cap:,.0f}"
                else:
                    market_cap_str = str(market_cap)
                summary_data.append({
                    'Symbol': symbol,
                    'Current Price': f"${data['current_price']:.2f}",
                    'Change': f"${data['price_change']:.2f}",
                    'Change %': f"{data['price_change_pct']:.2f}%",
                    'Market Cap': market_cap_str
                })
            elif data:
                summary_data.append({
                    'Symbol': symbol,
                    'Current Price': 'N/A',
                    'Change': 'N/A',
                    'Change %': 'N/A',
                    'Market Cap': 'N/A'
                })
            else:
                summary_data.append({
                    'Symbol': symbol,
                    'Current Price': 'No Data',
                    'Change': 'No Data',
                    'Change %': 'No Data',
                    'Market Cap': 'No Data'
                })
        if summary_data:
            df = pd.DataFrame(summary_data)
            st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main() 