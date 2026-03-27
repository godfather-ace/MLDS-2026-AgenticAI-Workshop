# Python Tutorial for Implementing MCP Server & Inspector

---

## 📦 Step 1 — Install `uv`

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 🗂️ Step 2 — Set Up Python Project

```bash
uv init simple-mcp-server
cd simple-mcp-server
```

---

## 🐍 Step 3 — Create a Virtual Environment

```bash
uv venv .venv
source .venv/bin/activate
```

---

## 📥 Step 4 — Install Dependencies

Using `uv`:

```bash
uv add "mcp[cli]" yfinance
```

Alternatively, using `pip`:

```bash
pip install mcp yfinance
```

---

## 🧠 Step 5 — Add Code to `main.py`

```python
from mcp.server.fastmcp import FastMCP
import yfinance as yf

# Create an MCP server with a custom name
mcp = FastMCP("Stock Price Server")


@mcp.tool()
def get_stock_price(symbol: str) -> float:
    """
    Retrieve the current stock price for the given ticker symbol.
    Returns the latest closing price as a float.
    """
    try:
        ticker = yf.Ticker(symbol)
        # Get today's historical data; may return empty if market is closed or symbol is invalid.
        data = ticker.history(period="1d")
        if not data.empty:
            # Use the last closing price from today's data
            price = data['Close'].iloc[-1]
            return float(price)
        else:
            # As a fallback, try using the regular market price from the ticker info
            info = ticker.info
            price = info.get("regularMarketPrice", None)
            if price is not None:
                return float(price)
            else:
                return -1.0  # Indicate failure
    except Exception:
        # Return -1.0 to indicate an error occurred when fetching the stock price
        return -1.0


@mcp.resource("stock://{symbol}")
def stock_resource(symbol: str) -> str:
    """
    Expose stock price data as a resource.
    Returns a formatted string with the current stock price for the given symbol.
    """
    price = get_stock_price(symbol)
    if price < 0:
        return f"Error: Could not retrieve price for symbol '{symbol}'."
    return f"The current price of '{symbol}' is ${price:.2f}."


@mcp.tool()
def get_stock_history(symbol: str, period: str = "1mo") -> str:
    """
    Retrieve historical data for a stock given a ticker symbol and a period.
    Returns the historical data as a CSV formatted string.

    Parameters:
        symbol: The stock ticker symbol.
        period: The period over which to retrieve historical data (e.g., '1mo', '3mo', '1y').
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        if data.empty:
            return f"No historical data found for symbol '{symbol}' with period '{period}'."
        # Convert the DataFrame to a CSV formatted string
        csv_data = data.to_csv()
        return csv_data
    except Exception as e:
        return f"Error fetching historical data: {str(e)}"


@mcp.tool()
def compare_stocks(symbol1: str, symbol2: str) -> str:
    """
    Compare the current stock prices of two ticker symbols.
    Returns a formatted message comparing the two stock prices.

    Parameters:
        symbol1: The first stock ticker symbol.
        symbol2: The second stock ticker symbol.
    """
    price1 = get_stock_price(symbol1)
    price2 = get_stock_price(symbol2)

    if price1 < 0 or price2 < 0:
        return f"Error: Could not retrieve data for comparison of '{symbol1}' and '{symbol2}'."

    if price1 > price2:
        result = f"{symbol1} (${price1:.2f}) is higher than {symbol2} (${price2:.2f})."
    elif price1 < price2:
        result = f"{symbol1} (${price1:.2f}) is lower than {symbol2} (${price2:.2f})."
    else:
        result = f"Both {symbol1} and {symbol2} have the same price (${price1:.2f})."

    return result


if __name__ == "__main__":
    mcp.run()
```

---

## 🔍 Step 6 — Run the MCP Inspector

```bash
mcp dev main.py
```

---

## 🖥️ Step 7 — Add to Claude Desktop

After inspection, install the MCP server into Claude Desktop:

```bash
mcp install main.py --name "My MCP Server"
```

---

## 🛠️ Tools & Resources Summary

| Name | Type | Description |
|---|---|---|
| `get_stock_price` | Tool | Returns the latest closing price for a ticker symbol |
| `get_stock_history` | Tool | Returns historical OHLCV data as a CSV string |
| `compare_stocks` | Tool | Compares current prices of two ticker symbols |
| `stock://{symbol}` | Resource | Exposes stock price data as an MCP resource |