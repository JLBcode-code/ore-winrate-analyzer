"""
Bayesian Inference Engine for ORE Supply Game Analysis
贝叶斯推理引擎用于ORE供应游戏分析
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional


class BayesianEngine:
    """
    Implementation of Bayesian inference for game outcome prediction.
    实现用于游戏结果预测的贝叶斯推理。
    """
    
    def __init__(self, prior_alpha: float = 1.0, prior_beta: float = 1.0):
        """
        Initialize the Bayesian engine with Beta distribution priors.
        
        Args:
            prior_alpha: Alpha parameter for Beta prior (default: 1.0 for uniform prior)
            prior_beta: Beta parameter for Beta prior (default: 1.0 for uniform prior)
        """
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self.posterior_alpha = prior_alpha
        self.posterior_beta = prior_beta
        self.history = []
    
    def update(self, wins: int, losses: int) -> None:
        """
        Update the posterior distribution with new game results.
        使用新的游戏结果更新后验分布。
        
        Args:
            wins: Number of wins observed
            losses: Number of losses observed
        """
        self.posterior_alpha += wins
        self.posterior_beta += losses
        self.history.append({
            'wins': wins,
            'losses': losses,
            'alpha': self.posterior_alpha,
            'beta': self.posterior_beta
        })
    
    def get_win_probability(self) -> float:
        """
        Calculate the expected win probability based on current posterior.
        基于当前后验计算预期获胜概率。
        
        Returns:
            Expected win probability (posterior mean)
        """
        return self.posterior_alpha / (self.posterior_alpha + self.posterior_beta)
    
    def get_credible_interval(self, confidence: float = 0.95) -> Tuple[float, float]:
        """
        Calculate the credible interval for win probability.
        计算获胜概率的可信区间。
        
        Args:
            confidence: Confidence level (default: 0.95 for 95% credible interval)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        alpha_level = (1 - confidence) / 2
        lower = stats.beta.ppf(alpha_level, self.posterior_alpha, self.posterior_beta)
        upper = stats.beta.ppf(1 - alpha_level, self.posterior_alpha, self.posterior_beta)
        return (lower, upper)
    
    def get_probability_distribution(self, n_points: int = 1000) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the full posterior probability distribution.
        获取完整的后验概率分布。
        
        Args:
            n_points: Number of points for the distribution curve
            
        Returns:
            Tuple of (x_values, probability_densities)
        """
        x = np.linspace(0, 1, n_points)
        y = stats.beta.pdf(x, self.posterior_alpha, self.posterior_beta)
        return (x, y)
    
    def predict_next_n_games(self, n_games: int, n_simulations: int = 10000) -> Dict[str, float]:
        """
        Predict outcomes for the next n games using posterior predictive distribution.
        使用后验预测分布预测接下来n场比赛的结果。
        
        Args:
            n_games: Number of future games to predict
            n_simulations: Number of Monte Carlo simulations
            
        Returns:
            Dictionary with prediction statistics
        """
        # Sample win probabilities from posterior
        p_samples = np.random.beta(self.posterior_alpha, self.posterior_beta, n_simulations)
        
        # For each sampled probability, simulate n games
        wins_distribution = np.random.binomial(n_games, p_samples)
        
        return {
            'expected_wins': np.mean(wins_distribution),
            'median_wins': np.median(wins_distribution),
            'std_wins': np.std(wins_distribution),
            'min_wins': np.min(wins_distribution),
            'max_wins': np.max(wins_distribution),
            'win_probability': self.get_win_probability()
        }
    
    def reset(self) -> None:
        """
        Reset the engine to prior distribution.
        重置引擎到先验分布。
        """
        self.posterior_alpha = self.prior_alpha
        self.posterior_beta = self.prior_beta
        self.history = []
    
    def get_summary(self) -> Dict:
        """
        Get a summary of the current state.
        获取当前状态摘要。
        
        Returns:
            Dictionary with current statistics
        """
        prob = self.get_win_probability()
        lower, upper = self.get_credible_interval(0.95)
        
        total_games = (self.posterior_alpha - self.prior_alpha) + (self.posterior_beta - self.prior_beta)
        wins = self.posterior_alpha - self.prior_alpha
        
        return {
            'total_games': int(total_games),
            'wins': int(wins),
            'losses': int(total_games - wins),
            'win_probability': prob,
            'credible_interval_95': (lower, upper),
            'posterior_alpha': self.posterior_alpha,
            'posterior_beta': self.posterior_beta
        }
