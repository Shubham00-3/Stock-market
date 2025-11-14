"""
FastMCP Server - Financial Data Tool Provider
Provides 5 asynchronous tools for stock market data using yfinance and NewsAPI.
"""
import os
import asyncio
import logging
from typing import Optional
from datetime import datetime

import yfinance as yf
import aiohttp
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server - bind to 0.0.0.0 for Railway networking
mcp = FastMCP("Market Intelligence Tools", host="0.0.0.0", port=8000)

# Valid periods for historical data
VALID_PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "ytd", "max"]


@mcp.tool()
async def get_stock_price(symbol: str) -> dict:
    """
    Get current stock price and key metrics for a given symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
    
    Returns:
        Dictionary with current price, changes, volume, market cap, and trading ranges
    """
    try:
        logger.info(f"Fetching stock price for {symbol}")
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Validate that we got valid data
        if not info or 'symbol' not in info:
            return {
                "error": f"Invalid symbol or no data available for {symbol}",
                "symbol": symbol
            }
        
        current_price = info.get('currentPrice') or info.get('regularMarketPrice')
        previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
        
        # Calculate change if we have both values
        change = None
        change_percent = None
        if current_price and previous_close:
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
        
        result = {
            "symbol": symbol.upper(),
            "company_name": info.get('longName', info.get('shortName', 'N/A')),
            "current_price": current_price,
            "previous_close": previous_close,
            "change": round(change, 2) if change else None,
            "change_percent": round(change_percent, 2) if change_percent else None,
            "volume": info.get('volume'),
            "market_cap": info.get('marketCap'),
            "day_high": info.get('dayHigh'),
            "day_low": info.get('dayLow'),
            "52_week_high": info.get('fiftyTwoWeekHigh'),
            "52_week_low": info.get('fiftyTwoWeekLow')
        }
        
        logger.info(f"Successfully fetched data for {symbol}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching stock price for {symbol}: {str(e)}")
        return {
            "error": f"Failed to fetch data for {symbol}: {str(e)}",
            "symbol": symbol
        }


@mcp.tool()
async def get_market_news(query: str = "stock market", num_articles: int = 5) -> list:
    """
    Get recent market news articles using NewsAPI.
    
    Args:
        query: Search query for news articles (default: "stock market")
        num_articles: Number of articles to return (default: 5, max: 20)
    
    Returns:
        List of article dictionaries with title, description, url, published date, and source
    """
    try:
        news_api_key = os.getenv("NEWS_API_KEY")
        if not news_api_key:
            return [{
                "error": "NEWS_API_KEY not configured",
                "message": "Please set NEWS_API_KEY environment variable"
            }]
        
        # Limit articles to reasonable amount
        num_articles = min(num_articles, 20)
        
        logger.info(f"Fetching {num_articles} news articles for query: {query}")
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": news_api_key,
            "pageSize": num_articles,
            "sortBy": "publishedAt",
            "language": "en"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"NewsAPI error: {error_text}")
                    return [{
                        "error": f"NewsAPI request failed with status {response.status}",
                        "details": error_text
                    }]
                
                data = await response.json()
                
                if data.get('status') != 'ok':
                    return [{
                        "error": "NewsAPI returned error",
                        "details": data.get('message', 'Unknown error')
                    }]
                
                articles = data.get('articles', [])
                
                result = []
                for article in articles:
                    result.append({
                        "title": article.get('title', 'N/A'),
                        "description": article.get('description', 'N/A'),
                        "url": article.get('url', 'N/A'),
                        "published_at": article.get('publishedAt', 'N/A'),
                        "source": article.get('source', {}).get('name', 'N/A')
                    })
                
                logger.info(f"Successfully fetched {len(result)} news articles")
                return result
                
    except Exception as e:
        logger.error(f"Error fetching market news: {str(e)}")
        return [{
            "error": f"Failed to fetch news: {str(e)}"
        }]


@mcp.tool()
async def get_stock_history(symbol: str, period: str = "1mo") -> dict:
    """
    Get historical stock data for a given period.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
        period: Time period - valid values: 1d, 5d, 1mo, 3mo, 6mo, 1y, ytd, max (default: 1mo)
    
    Returns:
        Dictionary with historical data including period stats and latest close
    """
    try:
        # Validate period
        if period not in VALID_PERIODS:
            return {
                "error": f"Invalid period '{period}'. Valid periods: {', '.join(VALID_PERIODS)}",
                "symbol": symbol
            }
        
        logger.info(f"Fetching {period} history for {symbol}")
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return {
                "error": f"No historical data available for {symbol}",
                "symbol": symbol,
                "period": period
            }
        
        result = {
            "symbol": symbol.upper(),
            "period": period,
            "start_date": hist.index[0].strftime("%Y-%m-%d"),
            "end_date": hist.index[-1].strftime("%Y-%m-%d"),
            "latest_close": round(hist['Close'].iloc[-1], 2),
            "period_high": round(hist['High'].max(), 2),
            "period_low": round(hist['Low'].min(), 2),
            "average_volume": int(hist['Volume'].mean())
        }
        
        logger.info(f"Successfully fetched history for {symbol}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching stock history for {symbol}: {str(e)}")
        return {
            "error": f"Failed to fetch history for {symbol}: {str(e)}",
            "symbol": symbol,
            "period": period
        }


@mcp.tool()
async def compare_stocks(symbols: list[str]) -> dict:
    """
    Compare key metrics across multiple stocks.
    
    Args:
        symbols: List of stock ticker symbols (max 5)
    
    Returns:
        Dictionary with comparison data for each symbol
    """
    try:
        # Limit to 5 symbols
        if len(symbols) > 5:
            symbols = symbols[:5]
            logger.warning(f"Limited comparison to first 5 symbols")
        
        logger.info(f"Comparing stocks: {', '.join(symbols)}")
        
        result = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                if not info or 'symbol' not in info:
                    result[symbol.upper()] = {
                        "error": "Invalid symbol or no data available"
                    }
                    continue
                
                result[symbol.upper()] = {
                    "company_name": info.get('longName', info.get('shortName', 'N/A')),
                    "current_price": info.get('currentPrice') or info.get('regularMarketPrice'),
                    "market_cap": info.get('marketCap'),
                    "pe_ratio": info.get('trailingPE') or info.get('forwardPE'),
                    "dividend_yield": info.get('dividendYield')
                }
                
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {str(e)}")
                result[symbol.upper()] = {
                    "error": str(e)
                }
        
        logger.info(f"Successfully compared {len(result)} stocks")
        return result
        
    except Exception as e:
        logger.error(f"Error comparing stocks: {str(e)}")
        return {
            "error": f"Failed to compare stocks: {str(e)}"
        }


@mcp.tool()
async def get_market_summary() -> dict:
    """
    Get current snapshot of major market indices.
    
    Returns:
        Dictionary with data for S&P 500, Dow Jones, NASDAQ, and Russell 2000
    """
    try:
        logger.info("Fetching market summary")
        
        indices = {
            "S&P 500": "^GSPC",
            "Dow Jones": "^DJI",
            "NASDAQ": "^IXIC",
            "Russell 2000": "^RUT"
        }
        
        result = {}
        
        for name, symbol in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                current_price = info.get('currentPrice') or info.get('regularMarketPrice')
                previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
                
                change = None
                change_percent = None
                if current_price and previous_close:
                    change = current_price - previous_close
                    change_percent = (change / previous_close) * 100
                
                result[name] = {
                    "value": current_price,
                    "change": round(change, 2) if change else None,
                    "change_percent": round(change_percent, 2) if change_percent else None
                }
                
            except Exception as e:
                logger.error(f"Error fetching {name} data: {str(e)}")
                result[name] = {
                    "error": str(e)
                }
        
        logger.info("Successfully fetched market summary")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching market summary: {str(e)}")
        return {
            "error": f"Failed to fetch market summary: {str(e)}"
        }


if __name__ == "__main__":
    logger.info("Starting Market Intelligence MCP Server")
    logger.info(f"Transport: streamable-http on port 8000 (binding to 0.0.0.0)")
    
    # Run the FastMCP server
    mcp.run(transport="streamable-http")

