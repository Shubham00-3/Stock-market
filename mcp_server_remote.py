# """
# FastMCP Server - Financial Data Tool Provider
# Provides 5 asynchronous tools for stock market data using yfinance and NewsAPI.
# """
# import os
# import asyncio
# import logging
# from typing import Optional
# from datetime import datetime

# import yfinance as yf
# import aiohttp
# from mcp.server.fastmcp import FastMCP
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Configure logging
# logging.basicConfig(
#     level=os.getenv("LOG_LEVEL", "INFO"),
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# )
# logger = logging.getLogger(__name__)

# # Initialize FastMCP server - bind using HOST/PORT env vars for Railway networking
# port = int(os.getenv("PORT", "8000"))
# host = os.getenv("HOST", "127.0.0.1")
# mcp = FastMCP("Market Intelligence Tools", host=host, port=port)

# # Valid periods for historical data
# VALID_PERIODS = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "ytd", "max"]


# @mcp.tool()
# async def get_stock_price(symbol: str) -> dict:
#     """
#     Get current stock price and key metrics for a given symbol.
    
#     Args:
#         symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
    
#     Returns:
#         Dictionary with current price, changes, volume, market cap, and trading ranges
#     """
#     try:
#         logger.info(f"Fetching stock price for {symbol}")
#         ticker = yf.Ticker(symbol)
#         info = ticker.info
        
#         # Validate that we got valid data
#         if not info or 'symbol' not in info:
#             return {
#                 "error": f"Invalid symbol or no data available for {symbol}",
#                 "symbol": symbol
#             }
        
#         current_price = info.get('currentPrice') or info.get('regularMarketPrice')
#         previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
        
#         # Calculate change if we have both values
#         change = None
#         change_percent = None
#         if current_price and previous_close:
#             change = current_price - previous_close
#             change_percent = (change / previous_close) * 100
        
#         result = {
#             "symbol": symbol.upper(),
#             "company_name": info.get('longName', info.get('shortName', 'N/A')),
#             "current_price": current_price,
#             "previous_close": previous_close,
#             "change": round(change, 2) if change else None,
#             "change_percent": round(change_percent, 2) if change_percent else None,
#             "volume": info.get('volume'),
#             "market_cap": info.get('marketCap'),
#             "day_high": info.get('dayHigh'),
#             "day_low": info.get('dayLow'),
#             "52_week_high": info.get('fiftyTwoWeekHigh'),
#             "52_week_low": info.get('fiftyTwoWeekLow')
#         }
        
#         logger.info(f"Successfully fetched data for {symbol}")
#         return result
        
#     except Exception as e:
#         logger.error(f"Error fetching stock price for {symbol}: {str(e)}")
#         return {
#             "error": f"Failed to fetch data for {symbol}: {str(e)}",
#             "symbol": symbol
#         }


# @mcp.tool()
# async def get_market_news(query: str = "stock market", num_articles: int = 5) -> list:
#     """
#     Get recent market news articles using NewsAPI.
    
#     Args:
#         query: Search query for news articles (default: "stock market")
#         num_articles: Number of articles to return (default: 5, max: 20)
    
#     Returns:
#         List of article dictionaries with title, description, url, published date, and source
#     """
#     try:
#         news_api_key = os.getenv("NEWS_API_KEY")
#         if not news_api_key:
#             return [{
#                 "error": "NEWS_API_KEY not configured",
#                 "message": "Please set NEWS_API_KEY environment variable"
#             }]
        
#         # Limit articles to reasonable amount
#         num_articles = min(num_articles, 20)
        
#         logger.info(f"Fetching {num_articles} news articles for query: {query}")
        
#         url = "https://newsapi.org/v2/everything"
#         params = {
#             "q": query,
#             "apiKey": news_api_key,
#             "pageSize": num_articles,
#             "sortBy": "publishedAt",
#             "language": "en"
#         }
        
#         async with aiohttp.ClientSession() as session:
#             async with session.get(url, params=params) as response:
#                 if response.status != 200:
#                     error_text = await response.text()
#                     logger.error(f"NewsAPI error: {error_text}")
#                     return [{
#                         "error": f"NewsAPI request failed with status {response.status}",
#                         "details": error_text
#                     }]
                
#                 data = await response.json()
                
#                 if data.get('status') != 'ok':
#                     return [{
#                         "error": "NewsAPI returned error",
#                         "details": data.get('message', 'Unknown error')
#                     }]
                
#                 articles = data.get('articles', [])
                
#                 result = []
#                 for article in articles:
#                     result.append({
#                         "title": article.get('title', 'N/A'),
#                         "description": article.get('description', 'N/A'),
#                         "url": article.get('url', 'N/A'),
#                         "published_at": article.get('publishedAt', 'N/A'),
#                         "source": article.get('source', {}).get('name', 'N/A')
#                     })
                
#                 logger.info(f"Successfully fetched {len(result)} news articles")
#                 return result
                
#     except Exception as e:
#         logger.error(f"Error fetching market news: {str(e)}")
#         return [{
#             "error": f"Failed to fetch news: {str(e)}"
#         }]


# @mcp.tool()
# async def get_stock_history(symbol: str, period: str = "1mo") -> dict:
#     """
#     Get historical stock data for a given period.
    
#     Args:
#         symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
#         period: Time period - valid values: 1d, 5d, 1mo, 3mo, 6mo, 1y, ytd, max (default: 1mo)
    
#     Returns:
#         Dictionary with historical data including period stats and latest close
#     """
#     try:
#         # Validate period
#         if period not in VALID_PERIODS:
#             return {
#                 "error": f"Invalid period '{period}'. Valid periods: {', '.join(VALID_PERIODS)}",
#                 "symbol": symbol
#             }
        
#         logger.info(f"Fetching {period} history for {symbol}")
        
#         ticker = yf.Ticker(symbol)
#         hist = ticker.history(period=period)
        
#         if hist.empty:
#             return {
#                 "error": f"No historical data available for {symbol}",
#                 "symbol": symbol,
#                 "period": period
#             }
        
#         result = {
#             "symbol": symbol.upper(),
#             "period": period,
#             "start_date": hist.index[0].strftime("%Y-%m-%d"),
#             "end_date": hist.index[-1].strftime("%Y-%m-%d"),
#             "latest_close": round(hist['Close'].iloc[-1], 2),
#             "period_high": round(hist['High'].max(), 2),
#             "period_low": round(hist['Low'].min(), 2),
#             "average_volume": int(hist['Volume'].mean())
#         }
        
#         logger.info(f"Successfully fetched history for {symbol}")
#         return result
        
#     except Exception as e:
#         logger.error(f"Error fetching stock history for {symbol}: {str(e)}")
#         return {
#             "error": f"Failed to fetch history for {symbol}: {str(e)}",
#             "symbol": symbol,
#             "period": period
#         }


# @mcp.tool()
# async def compare_stocks(symbols: list[str]) -> dict:
#     """
#     Compare key metrics across multiple stocks.
    
#     Args:
#         symbols: List of stock ticker symbols (max 5)
    
#     Returns:
#         Dictionary with comparison data for each symbol
#     """
#     try:
#         # Limit to 5 symbols
#         if len(symbols) > 5:
#             symbols = symbols[:5]
#             logger.warning(f"Limited comparison to first 5 symbols")
        
#         logger.info(f"Comparing stocks: {', '.join(symbols)}")
        
#         result = {}
        
#         for symbol in symbols:
#             try:
#                 ticker = yf.Ticker(symbol)
#                 info = ticker.info
                
#                 if not info or 'symbol' not in info:
#                     result[symbol.upper()] = {
#                         "error": "Invalid symbol or no data available"
#                     }
#                     continue
                
#                 result[symbol.upper()] = {
#                     "company_name": info.get('longName', info.get('shortName', 'N/A')),
#                     "current_price": info.get('currentPrice') or info.get('regularMarketPrice'),
#                     "market_cap": info.get('marketCap'),
#                     "pe_ratio": info.get('trailingPE') or info.get('forwardPE'),
#                     "dividend_yield": info.get('dividendYield')
#                 }
                
#             except Exception as e:
#                 logger.error(f"Error fetching data for {symbol}: {str(e)}")
#                 result[symbol.upper()] = {
#                     "error": str(e)
#                 }
        
#         logger.info(f"Successfully compared {len(result)} stocks")
#         return result
        
#     except Exception as e:
#         logger.error(f"Error comparing stocks: {str(e)}")
#         return {
#             "error": f"Failed to compare stocks: {str(e)}"
#         }


# @mcp.tool()
# async def get_market_summary() -> dict:
#     """
#     Get current snapshot of major market indices.
    
#     Returns:
#         Dictionary with data for S&P 500, Dow Jones, NASDAQ, and Russell 2000
#     """
#     try:
#         logger.info("Fetching market summary")
        
#         indices = {
#             "S&P 500": "^GSPC",
#             "Dow Jones": "^DJI",
#             "NASDAQ": "^IXIC",
#             "Russell 2000": "^RUT"
#         }
        
#         result = {}
        
#         for name, symbol in indices.items():
#             try:
#                 ticker = yf.Ticker(symbol)
#                 info = ticker.info
                
#                 current_price = info.get('currentPrice') or info.get('regularMarketPrice')
#                 previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
                
#                 change = None
#                 change_percent = None
#                 if current_price and previous_close:
#                     change = current_price - previous_close
#                     change_percent = (change / previous_close) * 100
                
#                 result[name] = {
#                     "value": current_price,
#                     "change": round(change, 2) if change else None,
#                     "change_percent": round(change_percent, 2) if change_percent else None
#                 }
                
#             except Exception as e:
#                 logger.error(f"Error fetching {name} data: {str(e)}")
#                 result[name] = {
#                     "error": str(e)
#                 }
        
#         logger.info("Successfully fetched market summary")
#         return result
        
#     except Exception as e:
#         logger.error(f"Error fetching market summary: {str(e)}")
#         return {
#             "error": f"Failed to fetch market summary: {str(e)}"
#         }


# if __name__ == "__main__":
#     logger.info("Starting Market Intelligence MCP Server")
#     logger.info(f"Transport: streamable-http on port {port} (binding to {host})")
    
#     # Run the FastMCP server
#     mcp.run(transport="streamable-http")



"""
Market Intelligence MCP Server - Remote HTTP Version
Provides tools for stock prices, market news, historical data, and stock comparison.
Uses Streamable HTTP transport for remote deployment.
"""

import asyncio
import os
import logging
from datetime import datetime
from typing import Optional

import yfinance as yf
import aiohttp
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from starlette.responses import JSONResponse

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    name="Market Intelligence Tools",
    host="0.0.0.0",
    port=8000
)


@mcp.tool()
async def get_stock_price(symbol: str) -> dict:
    """
    Get current stock price and basic information for a given symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'MSFT')
    
    Returns:
        Dictionary containing current price, previous close, change, volume, 
        market cap, and company name
    """
    try:
        logger.info(f"Fetching stock price for {symbol}")
        ticker = yf.Ticker(symbol.upper())
        info = ticker.info
        
        current_price = info.get("currentPrice") or info.get("regularMarketPrice")
        previous_close = info.get("previousClose")
        
        if current_price is None:
            return {
                "error": f"Unable to fetch price for {symbol}. Symbol may be invalid.",
                "symbol": symbol.upper()
            }
        
        change = 0.0
        change_percent = 0.0
        
        if previous_close and previous_close != 0:
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
        
        result = {
            "symbol": symbol.upper(),
            "company_name": info.get("longName") or info.get("shortName") or symbol,
            "current_price": round(current_price, 2),
            "previous_close": round(previous_close, 2) if previous_close else "N/A",
            "change": round(change, 2),
            "change_percent": round(change_percent, 2),
            "volume": info.get("volume", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "day_high": info.get("dayHigh", "N/A"),
            "day_low": info.get("dayLow", "N/A"),
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
        }
        
        logger.info(f"Successfully fetched data for {symbol}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching stock price for {symbol}: {e}")
        return {
            "error": str(e), 
            "symbol": symbol.upper(),
            "message": "Failed to fetch stock data. Please check the symbol."
        }


@mcp.tool()
async def get_market_news(
    query: str = "stock market",
    num_articles: int = 5
) -> list:
    """
    Get latest market news articles from NewsAPI.
    
    Args:
        query: Search query for news articles (default: "stock market")
        num_articles: Number of articles to return (default: 5, max: 10)
    
    Returns:
        List of news articles with title, description, url, published date, 
        and source
    """
    try:
        logger.info(f"Fetching market news for query: {query}")
        
        api_key = os.getenv("NEWS_API_KEY")
        if not api_key:
            return [{
                "error": "NEWS_API_KEY not configured",
                "message": "Please set NEWS_API_KEY in your .env file"
            }]
        
        # Limit num_articles to reasonable range
        num_articles = max(1, min(num_articles, 10))
        
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "apiKey": api_key,
            "sortBy": "publishedAt",
            "pageSize": num_articles,
            "language": "en"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    return [{
                        "error": f"NewsAPI returned status {response.status}",
                        "message": "Failed to fetch news"
                    }]
                
                data = await response.json()
                
                if data.get("status") != "ok":
                    return [{
                        "error": data.get("message", "API error"),
                        "code": data.get("code", "unknown")
                    }]
                
                articles = []
                for article in data.get("articles", [])[:num_articles]:
                    articles.append({
                        "title": article.get("title"),
                        "description": article.get("description"),
                        "url": article.get("url"),
                        "published_at": article.get("publishedAt"),
                        "source": article.get("source", {}).get("name"),
                        "author": article.get("author")
                    })
                
                logger.info(f"Successfully fetched {len(articles)} news articles")
                return articles
                
    except aiohttp.ClientError as e:
        logger.error(f"HTTP error fetching news: {e}")
        return [{"error": str(e), "message": "Network error fetching news"}]
    except Exception as e:
        logger.error(f"Error fetching market news: {e}")
        return [{"error": str(e), "message": "Failed to fetch news"}]


@mcp.tool()
async def get_stock_history(
    symbol: str,
    period: str = "1mo"
) -> dict:
    """
    Get historical stock price data for technical analysis.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
        period: Time period for history. Valid values:
                1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
                (default: '1mo')
    
    Returns:
        Dictionary with historical data including period high, low, 
        latest close, and average volume
    """
    try:
        logger.info(f"Fetching stock history for {symbol} over {period}")
        
        # Validate period
        valid_periods = ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", 
                        "5y", "10y", "ytd", "max"]
        if period not in valid_periods:
            return {
                "error": f"Invalid period '{period}'",
                "valid_periods": valid_periods,
                "symbol": symbol.upper()
            }
        
        ticker = yf.Ticker(symbol.upper())
        hist = ticker.history(period=period)
        
        if hist.empty:
            return {
                "error": f"No historical data available for {symbol}",
                "symbol": symbol.upper(),
                "period": period
            }
        
        result = {
            "symbol": symbol.upper(),
            "period": period,
            "data_points": len(hist),
            "start_date": hist.index[0].strftime("%Y-%m-%d"),
            "end_date": hist.index[-1].strftime("%Y-%m-%d"),
            "latest_close": round(float(hist['Close'].iloc[-1]), 2),
            "period_high": round(float(hist['High'].max()), 2),
            "period_low": round(float(hist['Low'].min()), 2),
            "average_volume": int(hist['Volume'].mean()),
            "total_volume": int(hist['Volume'].sum()),
            "price_change": round(
                float(hist['Close'].iloc[-1] - hist['Close'].iloc[0]), 2
            ),
            "price_change_percent": round(
                ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / 
                 hist['Close'].iloc[0]) * 100, 2
            )
        }
        
        logger.info(f"Successfully fetched historical data for {symbol}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching stock history for {symbol}: {e}")
        return {
            "error": str(e),
            "symbol": symbol.upper(),
            "period": period,
            "message": "Failed to fetch historical data"
        }


@mcp.tool()
async def compare_stocks(symbols: list[str]) -> dict:
    """
    Compare multiple stocks side by side with key metrics.
    
    Args:
        symbols: List of stock ticker symbols to compare 
                 (e.g., ['AAPL', 'GOOGL', 'MSFT'])
                 Maximum 5 stocks at a time
    
    Returns:
        Dictionary with comparison data for all provided symbols including
        price, market cap, P/E ratio, dividend yield, and 52-week range
    """
    try:
        logger.info(f"Comparing stocks: {symbols}")
        
        if not symbols or not isinstance(symbols, list):
            return {
                "error": "symbols must be a non-empty list",
                "example": ["AAPL", "GOOGL", "MSFT"]
            }
        
        # Limit to 5 stocks to avoid overwhelming responses
        if len(symbols) > 5:
            return {
                "error": "Maximum 5 stocks can be compared at once",
                "provided": len(symbols),
                "limit": 5
            }
        
        comparisons = {}
        
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol.upper())
                info = ticker.info
                
                current_price = info.get("currentPrice") or info.get(
                    "regularMarketPrice"
                )
                
                comparisons[symbol.upper()] = {
                    "company_name": info.get("longName") or info.get(
                        "shortName"
                    ) or symbol,
                    "current_price": round(current_price, 2) if current_price 
                                     else "N/A",
                    "market_cap": info.get("marketCap", "N/A"),
                    "pe_ratio": round(info.get("trailingPE", 0), 2) if info.get(
                        "trailingPE"
                    ) else "N/A",
                    "dividend_yield": round(
                        info.get("dividendYield", 0) * 100, 2
                    ) if info.get("dividendYield") else "N/A",
                    "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
                    "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
                    "beta": round(info.get("beta", 0), 2) if info.get(
                        "beta"
                    ) else "N/A",
                    "volume": info.get("volume", "N/A"),
                    "avg_volume": info.get("averageVolume", "N/A"),
                }
                
            except Exception as e:
                logger.warning(f"Error fetching data for {symbol}: {e}")
                comparisons[symbol.upper()] = {
                    "error": str(e),
                    "message": f"Failed to fetch data for {symbol}"
                }
        
        result = {
            "comparison": comparisons,
            "symbols_analyzed": len(symbols),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(f"Successfully compared {len(symbols)} stocks")
        return result
        
    except Exception as e:
        logger.error(f"Error comparing stocks: {e}")
        return {
            "error": str(e),
            "message": "Failed to compare stocks"
        }


@mcp.tool()
async def get_market_summary() -> dict:
    """
    Get a summary of major market indices and their current status.
    
    Returns:
        Dictionary with data for major indices: S&P 500, Dow Jones, NASDAQ,
        Russell 2000, including current values and daily changes
    """
    try:
        logger.info("Fetching market summary for major indices")
        
        indices = {
            "^GSPC": "S&P 500",
            "^DJI": "Dow Jones Industrial Average",
            "^IXIC": "NASDAQ Composite",
            "^RUT": "Russell 2000"
        }
        
        summary = {}
        
        for symbol, name in indices.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1d")
                
                if not hist.empty:
                    current = float(hist['Close'].iloc[-1])
                    open_price = float(hist['Open'].iloc[-1])
                    change = current - open_price
                    change_percent = (change / open_price) * 100
                    
                    summary[name] = {
                        "symbol": symbol,
                        "value": round(current, 2),
                        "change": round(change, 2),
                        "change_percent": round(change_percent, 2),
                        "high": round(float(hist['High'].iloc[-1]), 2),
                        "low": round(float(hist['Low'].iloc[-1]), 2),
                    }
                else:
                    summary[name] = {
                        "symbol": symbol,
                        "error": "No data available"
                    }
                    
            except Exception as e:
                logger.warning(f"Error fetching data for {name}: {e}")
                summary[name] = {
                    "symbol": symbol,
                    "error": str(e)
                }
        
        result = {
            "market_summary": summary,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "market_status": "Data fetched successfully"
        }
        
        logger.info("Successfully fetched market summary")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching market summary: {e}")
        return {
            "error": str(e),
            "message": "Failed to fetch market summary"
        }


# Health check endpoint (optional but recommended)
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for monitoring"""
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })


# Run the MCP server
if __name__ == "__main__":
    # Get port from environment (Railway, Render, etc. set PORT automatically)
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info("=" * 60)
    logger.info("Starting Market Intelligence MCP Server (Remote Mode)")
    logger.info("=" * 60)
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Endpoint: http://{host}:{port}/mcp")
    logger.info(f"Health Check: http://{host}:{port}/health")
    logger.info("")
    logger.info("Available tools:")
    logger.info("  - get_stock_price: Get current stock price and info")
    logger.info("  - get_market_news: Fetch latest market news")
    logger.info("  - get_stock_history: Get historical price data")
    logger.info("  - compare_stocks: Compare multiple stocks")
    logger.info("  - get_market_summary: Get major market indices summary")
    logger.info("=" * 60)
    
    # Run with HTTP transport (Streamable HTTP)
    # FastMCP automatically creates the /mcp endpoint
    asyncio.run(mcp.run(transport="streamable-http"))