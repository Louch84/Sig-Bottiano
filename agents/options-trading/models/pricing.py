"""
Quantitative Models
Options pricing, volatility modeling, and analytics
"""

import numpy as np
from scipy import stats
from scipy.optimize import minimize_scalar
from typing import Dict, Tuple, Optional, List
from dataclasses import dataclass
from enum import Enum

class OptionType(Enum):
    CALL = "call"
    PUT = "put"

@dataclass
class Greeks:
    delta: float
    gamma: float
    theta: float
    vega: float
    rho: float

class BlackScholesModel:
    """
    Black-Scholes-Merton option pricing model.
    
    Known limitations (documented for transparency):
    - Constant volatility assumption (violated by clustering/regime shifts)
    - Log-normal returns (misses fat tails/skewness)
    - No transaction costs
    - European exercise only (no early exercise for American options)
    """
    
    @staticmethod
    def price(
        S: float,  # Spot price
        K: float,  # Strike price
        T: float,  # Time to expiration (years)
        r: float,  # Risk-free rate
        q: float,  # Dividend yield
        sigma: float,  # Volatility
        option_type: OptionType
    ) -> float:
        """Calculate option price using BSM formula"""
        
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        if option_type == OptionType.CALL:
            price = S * np.exp(-q * T) * stats.norm.cdf(d1) - K * np.exp(-r * T) * stats.norm.cdf(d2)
        else:
            price = K * np.exp(-r * T) * stats.norm.cdf(-d2) - S * np.exp(-q * T) * stats.norm.cdf(-d1)
        
        return price
    
    @staticmethod
    def greeks(
        S: float,
        K: float,
        T: float,
        r: float,
        q: float,
        sigma: float,
        option_type: OptionType
    ) -> Greeks:
        """Calculate option Greeks"""
        
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        # Delta
        if option_type == OptionType.CALL:
            delta = np.exp(-q * T) * stats.norm.cdf(d1)
        else:
            delta = -np.exp(-q * T) * stats.norm.cdf(-d1)
        
        # Gamma (same for calls and puts)
        gamma = np.exp(-q * T) * stats.norm.pdf(d1) / (S * sigma * np.sqrt(T))
        
        # Theta
        if option_type == OptionType.CALL:
            theta = (-S * np.exp(-q * T) * stats.norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                     - r * K * np.exp(-r * T) * stats.norm.cdf(d2)
                     + q * S * np.exp(-q * T) * stats.norm.cdf(d1))
        else:
            theta = (-S * np.exp(-q * T) * stats.norm.pdf(d1) * sigma / (2 * np.sqrt(T))
                     + r * K * np.exp(-r * T) * stats.norm.cdf(-d2)
                     - q * S * np.exp(-q * T) * stats.norm.cdf(-d1))
        
        # Vega (same for calls and puts)
        vega = S * np.exp(-q * T) * stats.norm.pdf(d1) * np.sqrt(T) / 100  # Per 1% vol change
        
        # Rho
        if option_type == OptionType.CALL:
            rho = K * T * np.exp(-r * T) * stats.norm.cdf(d2) / 100  # Per 1% rate change
        else:
            rho = -K * T * np.exp(-r * T) * stats.norm.cdf(-d2) / 100
        
        return Greeks(delta, gamma, theta, vega, rho)
    
    @staticmethod
    def implied_volatility(
        market_price: float,
        S: float,
        K: float,
        T: float,
        r: float,
        q: float,
        option_type: OptionType
    ) -> float:
        """Calculate implied volatility from market price"""
        
        def objective(sigma):
            return (BlackScholesModel.price(S, K, T, r, q, sigma, option_type) - market_price)**2
        
        result = minimize_scalar(objective, bounds=(0.001, 5.0), method='bounded')
        return result.x if result.success else np.nan

class VolatilityModels:
    """
    Volatility forecasting models for under-$50 stocks.
    Characteristics: higher baseline vol, stronger shock reaction, less persistence
    """
    
    @staticmethod
    def garch_11(
        returns: np.ndarray,
        omega: float = 0.00001,
        alpha: float = 0.1,
        beta: float = 0.85
    ) -> Dict:
        """
        GARCH(1,1) volatility forecasting.
        
        Equation: σ²ₜ = ω + αr²ₜ₋₁ + βσ²ₜ₋₁
        
        For under-$50 stocks:
        - Larger ω (higher baseline volatility)
        - Larger α (stronger reaction to shocks)
        - Smaller β (less persistence)
        """
        
        n = len(returns)
        variance = np.zeros(n)
        variance[0] = np.var(returns)
        
        for t in range(1, n):
            variance[t] = omega + alpha * returns[t-1]**2 + beta * variance[t-1]
        
        # Forecast next 5 periods
        forecasts = []
        last_var = variance[-1]
        
        for h in range(1, 6):
            if h == 1:
                forecast = omega + alpha * returns[-1]**2 + beta * last_var
            else:
                forecast = omega + (alpha + beta) * forecasts[-1]
            forecasts.append(forecast)
        
        return {
            "model": "GARCH(1,1)",
            "parameters": {"omega": omega, "alpha": alpha, "beta": beta, "persistence": alpha + beta},
            "current_variance": variance[-1],
            "current_volatility": np.sqrt(variance[-1]),
            "forecasts": forecasts,
            "half_life": np.log(0.5) / np.log(alpha + beta) if (alpha + beta) < 1 else np.inf
        }
    
    @staticmethod
    def egarch(
        returns: np.ndarray,
        omega: float = -0.1,
        alpha: float = 0.1,
        gamma: float = -0.05,
        beta: float = 0.95
    ) -> Dict:
        """
        EGARCH model with asymmetric term for leverage effects.
        
        Particularly relevant for under-$50 stocks due to stronger leverage effects.
        
        Equation: ln(σ²ₜ) = ω + α(|zₜ₋₁| - E|z|) + γzₜ₋₁ + βln(σ²ₜ₋₁)
        """
        
        n = len(returns)
        log_variance = np.zeros(n)
        log_variance[0] = np.log(np.var(returns))
        
        standardized = returns / np.sqrt(np.exp(log_variance[0]))
        e_abs_z = np.sqrt(2 / np.pi)  # E|z| for standard normal
        
        for t in range(1, n):
            z_t_1 = standardized[t-1]
            log_variance[t] = (omega + 
                              alpha * (abs(z_t_1) - e_abs_z) + 
                              gamma * z_t_1 + 
                              beta * log_variance[t-1])
        
        return {
            "model": "EGARCH",
            "parameters": {"omega": omega, "alpha": alpha, "gamma": gamma, "beta": beta},
            "asymmetric_effect": gamma,  # Negative = leverage effect
            "current_volatility": np.sqrt(np.exp(log_variance[-1])),
            "leverage_relevance": "High for under-$50 stocks"
        }
    
    @staticmethod
    def heston_model(
        S: float,
        K: float,
        T: float,
        r: float,
        v0: float = 0.04,
        kappa: float = 2.0,
        theta: float = 0.04,
        xi: float = 0.3,
        rho: float = -0.7
    ) -> Dict:
        """
        Heston stochastic volatility model.
        
        Parameters:
        - kappa: Mean reversion speed
        - theta: Long-term variance
        - xi: Vol of vol
        - rho: Correlation between price and variance
        - v0: Initial variance
        
        Best for: Smile fitting and exotic option pricing
        """
        
        # Simplified Heston characteristic function
        # Full implementation requires numerical integration
        
        return {
            "model": "Heston SV",
            "parameters": {
                "v0": v0,
                "kappa": kappa,
                "theta": theta,
                "xi": xi,
                "rho": rho
            },
            "long_term_vol": np.sqrt(theta),
            "mean_reversion_speed": kappa,
            "vol_of_vol": xi,
            "price_vol_correlation": rho,
            "note": "Full pricing requires FFT or numerical integration"
        }

class VolatilityAnalytics:
    """Realized and implied volatility analytics"""
    
    @staticmethod
    def realized_volatility(returns: np.ndarray, window: int = 20) -> float:
        """Calculate realized volatility (annualized)"""
        return np.std(returns[-window:]) * np.sqrt(252)
    
    @staticmethod
    def volatility_risk_premium(iv30: float, rv20: float) -> float:
        """
        Volatility Risk Premium: IV - RV
        
        Positive = short vol opportunity
        Negative = stress/risk-off
        """
        return iv30 - rv20
    
    @staticmethod
    def term_structure(iv30: float, iv90: float) -> float:
        """
        Volatility term structure: IV90 - IV30
        
        Steep = expected volatility increase
        Inverted = event risk priced
        """
        return iv90 - iv30
    
    @staticmethod
    def skew(iv25_put: float, iv25_call: float) -> float:
        """
        Volatility skew: IV(25 delta put) - IV(25 delta call)
        
        Steepening = crash hedging demand
        Flattening = speculation/compliance
        """
        return iv25_put - iv25_call
    
    @staticmethod
    def expected_move(stock_price: float, atm_straddle: float, days: int) -> float:
        """
        Calculate expected move from straddle price.
        
        Formula: (ATM Straddle Price / Stock Price) × √(Days/365)
        """
        return (atm_straddle / stock_price) * np.sqrt(days / 365)

class VIXReplication:
    """VIX methodology replication for custom volatility indices"""
    
    @staticmethod
    def calculate_variance_swap_rate(
        option_prices: List[Dict],
        risk_free_rate: float,
        time_to_expiry: float
    ) -> float:
        """
        Replicate variance swap payoff using weighted option portfolio.
        
        Formula: σ² = (2/T) × Σ(ΔKᵢ/Kᵢ²) × e^(rT) × Q(Kᵢ) - (1/T) × [F/K₀ - 1]²
        """
        
        variance_contribution = 0
        
        for opt in option_prices:
            K = opt["strike"]
            delta_K = opt["strike_width"]
            Q = opt["mid_price"]
            
            variance_contribution += (delta_K / K**2) * np.exp(risk_free_rate * time_to_expiry) * Q
        
        T = time_to_expiry
        variance_rate = (2 / T) * variance_contribution
        
        # Adjustment for F/K0 term
        F = option_prices[0]["forward_price"]
        K0 = option_prices[0]["atm_strike"]
        adjustment = (1 / T) * ((F / K0) - 1)**2
        
        return variance_rate - adjustment
    
    @staticmethod
    def interpolate_30day_var(v1: float, t1: float, v2: float, t2: float) -> float:
        """Interpolate to 30-day constant maturity"""
        t30 = 30 / 365
        
        w1 = (t2 - t30) / (t2 - t1)
        w2 = (t30 - t1) / (t2 - t1)
        
        return w1 * v1 + w2 * v2

class Under50StockAdjustments:
    """
    Special adjustments for under-$50 stock characteristics:
    - Higher baseline volatility
    - Stronger reaction to shocks
    - Less persistence
    - Stronger leverage effects (EGARCH more relevant)
    """
    
    @staticmethod
    def adjust_garch_params(base_params: Dict) -> Dict:
        """Adjust GARCH parameters for under-$50 stocks"""
        return {
            "omega": base_params.get("omega", 0.00001) * 2.5,  # Higher baseline
            "alpha": base_params.get("alpha", 0.1) * 1.3,      # Stronger shock reaction
            "beta": base_params.get("beta", 0.85) * 0.9        # Less persistence
        }
    
    @staticmethod
    def estimate_expected_move(price: float, days: int, vol_percentile: float = 50) -> Dict:
        """Estimate expected move with under-$50 adjustments"""
        
        # Higher vol assumption for cheaper stocks
        base_vol = 0.30 if price < 20 else 0.25
        
        daily_vol = base_vol / np.sqrt(252)
        move = price * daily_vol * np.sqrt(days) * stats.norm.ppf(0.5 + vol_percentile/200)
        
        return {
            "expected_move_pct": move / price,
            "expected_move_dollars": move,
            "up_price": price + move,
            "down_price": price - move,
            "vol_assumption": base_vol,
            "note": "Adjusted for under-$50 higher volatility regime"
        }
