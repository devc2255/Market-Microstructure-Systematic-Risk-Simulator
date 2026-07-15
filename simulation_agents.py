"""
simulation_agents.py
Defines the autonomous agents operating within the microstructure.
Models institutional hedging behavior and automated delta-band hedging.
"""

from options_pricer import OptionsPricer
from typing import Tuple

class NLPSentimentAgent:
    """Represents an algorithm trading on news/sentiment streams."""
    def __init__(self):
        self.sentiment_score: float = 1.0

    def evaluate_market(self, engine_shock_active: bool) -> float:
        """Updates conviction. Plummets if a macro shock is detected."""
        if engine_shock_active:
            self.sentiment_score = -1.0 
        return self.sentiment_score

class QuantHedgingAgent:
    """Represents an institutional portfolio utilizing derivatives for risk management."""
    def __init__(self):
        self.inventory: int = 10000 
        self.has_collar: bool = False
        self.collar_strikes: Tuple[float, float] = (0.0, 0.0)

    def evaluate_risk(self, S: float, sigma: float) -> bool:
        """Executes a Zero Cost Collar if volatility breaches safety thresholds."""
        # Lowered threshold from 0.25 to 0.20 to guarantee cascade on low-vol assets like SPY
        if sigma > 0.20 and not self.has_collar:
            self.collar_strikes = OptionsPricer.construct_zero_cost_collar(
                S=S, T=0.25, r=0.02, sigma=sigma
            )
            self.has_collar = True
            return True 
        return False

class OptionsMarketMaker:
    """Represents a derivatives desk managing non-linear risk via Delta Hedging."""
    def __init__(self):
        self.spot_inventory: int = 0
        self.short_put_strike: float = 0.0
        self.long_call_strike: float = 0.0
        self.active_collar: bool = False
        
        self.inventory_history: list[int] = [0]
        self.delta_history: list[float] = [0.0]

    def assume_collar_risk(self, put_strike: float, call_strike: float) -> None:
        """Takes the counterparty risk of the Quant Agent's Collar."""
        self.short_put_strike = put_strike
        self.long_call_strike = call_strike
        self.active_collar = True

    def delta_hedge(self, S: float, sigma: float) -> int:
        """
        Calculates portfolio Delta and executes spot market trades if tolerance is breached.
        Returns the volume of spot asset sold into the market.
        """
        sell_volume = 0
        portfolio_delta = 0.0
        
        if self.active_collar:
            # MM is SHORT the put and LONG the call
            delta_short_put = -1.0 * OptionsPricer.put_delta(S, self.short_put_strike, 0.25, 0.02, sigma)
            delta_long_call = OptionsPricer.call_delta(S, self.long_call_strike, 0.25, 0.02, sigma)
            
            # Net delta includes spot inventory (1 share = 1 delta)
            portfolio_delta = delta_short_put + delta_long_call + self.spot_inventory
            
            # Dynamic Delta-Band Hedging: Tolerance shrinks as volatility rises
            tau = max(0.05, 0.5 - (sigma * 0.5)) 
            
            # If exposure breaches band, aggressively short to remain delta-neutral
            if portfolio_delta > tau:
                hedge_size = int(portfolio_delta * 100) 
                self.spot_inventory -= hedge_size
                sell_volume = hedge_size
                
        self.inventory_history.append(self.spot_inventory)
        self.delta_history.append(portfolio_delta)
        
        return sell_volume        