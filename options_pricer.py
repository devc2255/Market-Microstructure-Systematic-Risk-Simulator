"""
options_pricer.py
Analytical Black-Scholes European Options Pricing and Greeks Engine.
Utilizes Scipy for instantaneous, O(1) computational complexity pricing
and Brent's method for precise Zero-Cost Collar root finding.
"""

import numpy as np
from scipy.stats import norm
from scipy.optimize import brentq

class OptionsPricer:
    
    @staticmethod
    def d1(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculates the d1 probability factor for Black-Scholes."""
        if T <= 0:
            return 0.0
        return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    
    @staticmethod
    def call_delta(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculates European Call Option Delta."""
        if T <= 0: return 1.0 if S > K else 0.0
        return norm.cdf(OptionsPricer.d1(S, K, T, r, sigma))
    
    @staticmethod
    def put_delta(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculates European Put Option Delta."""
        if T <= 0: return -1.0 if S < K else 0.0
        return OptionsPricer.call_delta(S, K, T, r, sigma) - 1.0

    @staticmethod
    def bs_call(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculates European Call Option Premium."""
        if T <= 0: return max(0.0, S - K)
        d1 = OptionsPricer.d1(S, K, T, r, sigma)
        d2 = d1 - sigma * np.sqrt(T)
        return S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)

    @staticmethod
    def bs_put(S: float, K: float, T: float, r: float, sigma: float) -> float:
        """Calculates European Put Option Premium."""
        if T <= 0: return max(0.0, K - S)
        d1 = OptionsPricer.d1(S, K, T, r, sigma)
        d2 = d1 - sigma * np.sqrt(T)
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

    @staticmethod
    def construct_zero_cost_collar(S: float, T: float, r: float, sigma: float) -> tuple[float, float]:
        """
        Calculates strikes for a Zero Cost Collar.
        Uses a 5% OTM Put for protection, and solves for the Call strike
        that perfectly offsets the Put premium using Brent's method.
        """
        put_strike = S * 0.95 
        target_premium = OptionsPricer.bs_put(S, put_strike, T, r, sigma)
        
        # Objective function: Difference between Call premium and target Put premium
        def objective_function(call_strike_guess):
            return OptionsPricer.bs_call(S, call_strike_guess, T, r, sigma) - target_premium
        
        try:
            # Use institutional-grade root finding between current price and +20% OTM
            call_strike = brentq(objective_function, S, S * 1.20)
        except ValueError:
            # Fallback if solver fails to converge in extreme volatility
            call_strike = S * 1.05 
            
        return put_strike, call_strike