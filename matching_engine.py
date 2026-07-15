"""
matching_engine.py
Synthetic Spot Market Engine utilizing the Merton Jump-Diffusion Stochastic Differential Equation (SDE).
Models endogenous price formation, volatility expansion, and Order Book Imbalance (OBI).
"""

import numpy as np
from typing import List

class MatchingEngine:
    def __init__(self, initial_price: float = 100.0, mu: float = 0.05, sigma: float = 0.15, dt: float = 1/252):
        # Microstructure Parameters
        self.spot_price: float = initial_price
        self.mu: float = mu
        self.sigma: float = sigma
        self.dt: float = dt
        
        # State Tracking
        self.time_step: int = 0
        self.shock_active: bool = False
        self.order_book_imbalance: float = 0.0 # Bounded: -1.0 (All Ask) to 1.0 (All Bid)
        
        # Telemetry History
        self.price_history: List[float] = [self.spot_price]
        self.obi_history: List[float] = [self.order_book_imbalance]

    def trigger_exogenous_shock(self) -> None:
        """Triggers the liquidity vacuum (dJ_t component)."""
        self.shock_active = True

    def step(self, market_maker_sell_volume: int = 0) -> float:
        """
        Advances the market by one tick using the Merton Jump-Diffusion SDE.
        Incorporates endogenous impact from Market Maker delta hedging.
        """
        # 1. Standard Brownian Motion (Market-making noise)
        dW = np.random.normal(0, np.sqrt(self.dt))
        
        # 2. Jump Component (Systemic Shock)
        dJ = 0.0
        if self.shock_active:
            dJ = np.random.uniform(-0.08, -0.05) # Severe -5% to -8% drop
            self.shock_active = False 
            self.sigma *= 2.5 # Instantaneous volatility surface expansion

        # 3. Endogenous Procyclicality (Delta-Hedge Impact)
        # MM selling absorbs liquidity, pushing drift downward
        hedging_impact = -0.00015 * market_maker_sell_volume

        # SDE Calculation
        dp = self.spot_price * (self.mu * self.dt + self.sigma * dW + dJ + hedging_impact)
        self.spot_price += dp
        
        # 4. Order Book Imbalance (OBI) Dynamics
        if dJ < 0 or market_maker_sell_volume > 0:
            # Massive sell pressure heavily skews OBI to the Ask side (-1.0)
            self.order_book_imbalance = np.clip(self.order_book_imbalance - 0.25, -1.0, 1.0)
        else:
            # Mean reversion with random noise during normal conditions
            reversion = (0.0 - self.order_book_imbalance) * 0.1
            noise = np.random.normal(0, 0.05)
            self.order_book_imbalance = np.clip(self.order_book_imbalance + reversion + noise, -1.0, 1.0)
            
        # Record Telemetry
        self.price_history.append(self.spot_price)
        self.obi_history.append(self.order_book_imbalance)
        self.time_step += 1
        
        return self.spot_price