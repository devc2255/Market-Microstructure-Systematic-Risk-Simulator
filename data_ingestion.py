"""
data_ingestion.py
Handles lightweight REST calls to Polygon.io's Market Data API.
Used exclusively to "seed" the Synthetic Matching Engine with real-world initial states.
"""

import requests
from typing import Tuple, Optional

class PolygonMarketData:
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"

    def search_ticker_by_name(self, company_name: str) -> list:
        """
        Queries Polygon's reference directory to find tickers matching a search string.
        Returns a list of tuples: [("AAPL", "Apple Inc."), ...]
        """
        url = f"{self.base_url}/v3/reference/tickers"
        params = {
            "search": company_name,
            "active": "true",
            "market": "stocks",
            "limit": 5,
            "apiKey": self.api_key
        }
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return [(item['ticker'], item['name']) for item in data.get('results', [])]
        except Exception as e:
            print(f"Directory Lookup Error: {e}")
        return []

    def fetch_initial_state(self, ticker: str) -> Optional[Tuple[float, float]]:
        """
        Fetches the previous day's close and high/low spread for a ticker.
        Returns (latest_spot_price, estimated_volatility).
        """
        # Endpoint for the previous day's aggregated market data
        endpoint = f"{self.base_url}/v2/aggs/ticker/{ticker.upper()}/prev?adjusted=true&apiKey={self.api_key}"
        
        try:
            response = requests.get(endpoint, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get('resultsCount', 0) > 0:
                result = data['results'][0]
                
                # Extract Close price for initial S0
                latest_price = result['c']
                
                # Estimate basic volatility (sigma) using high/low spread
                high = result['h']
                low = result['l']
                estimated_sigma = max(0.10, min(0.40, ((high - low) / latest_price) * 5))
                
                return latest_price, estimated_sigma
            else:
                print("No data found for this ticker.")
                return None
                
        except Exception as e:
            print(f"Polygon API Error: {e}")
            return None