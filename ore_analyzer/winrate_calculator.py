"""
Winrate Calculator for ORE Supply Game
ORE Supply游戏胜率计算器
"""

import numpy as np
from typing import Dict, List, Optional
from .bayesian_engine import BayesianEngine


class WinrateCalculator:
    """
    Calculate and analyze winrates for ORE Supply game sessions.
    计算和分析ORE Supply游戏会话的胜率。
    """
    
    def __init__(self):
        """Initialize the winrate calculator."""
        self.engine = BayesianEngine()
        self.sessions = []
    
    def add_session(self, wins: int, losses: int, session_name: str = None) -> None:
        """
        Add a game session with its results.
        添加带有结果的游戏会话。
        
        Args:
            wins: Number of wins in this session
            losses: Number of losses in this session
            session_name: Optional name for the session
        """
        self.sessions.append({
            'name': session_name or f"Session {len(self.sessions) + 1}",
            'wins': wins,
            'losses': losses,
            'winrate': wins / (wins + losses) if (wins + losses) > 0 else 0
        })
        self.engine.update(wins, losses)
    
    def get_overall_stats(self) -> Dict:
        """
        Get overall statistics across all sessions.
        获取所有会话的总体统计。
        
        Returns:
            Dictionary with overall statistics
        """
        total_wins = sum(s['wins'] for s in self.sessions)
        total_losses = sum(s['losses'] for s in self.sessions)
        total_games = total_wins + total_losses
        
        stats = {
            'total_sessions': len(self.sessions),
            'total_games': total_games,
            'total_wins': total_wins,
            'total_losses': total_losses,
            'simple_winrate': total_wins / total_games if total_games > 0 else 0,
            'bayesian_winrate': self.engine.get_win_probability(),
            'credible_interval': self.engine.get_credible_interval(0.95)
        }
        
        return stats
    
    def get_session_stats(self) -> List[Dict]:
        """
        Get statistics for each session.
        获取每个会话的统计信息。
        
        Returns:
            List of session statistics
        """
        return self.sessions.copy()
    
    def calculate_streak_probability(self, n_consecutive_wins: int) -> float:
        """
        Calculate the probability of achieving n consecutive wins.
        计算达成n连胜的概率。
        
        Args:
            n_consecutive_wins: Number of consecutive wins
            
        Returns:
            Probability of the streak
        """
        win_prob = self.engine.get_win_probability()
        return win_prob ** n_consecutive_wins
    
    def calculate_break_even_rate(self, win_reward: float, loss_penalty: float) -> Dict:
        """
        Calculate break-even winrate for given reward/penalty structure.
        计算给定奖励/惩罚结构的盈亏平衡胜率。
        
        Args:
            win_reward: Reward for winning
            loss_penalty: Penalty for losing (positive value)
            
        Returns:
            Dictionary with break-even analysis
        """
        break_even_rate = loss_penalty / (win_reward + loss_penalty)
        current_rate = self.engine.get_win_probability()
        
        return {
            'break_even_winrate': break_even_rate,
            'current_winrate': current_rate,
            'above_break_even': current_rate > break_even_rate,
            'expected_value': current_rate * win_reward - (1 - current_rate) * loss_penalty
        }
    
    def predict_future_performance(self, n_games: int) -> Dict:
        """
        Predict performance for next n games.
        预测接下来n场比赛的表现。
        
        Args:
            n_games: Number of future games
            
        Returns:
            Prediction statistics
        """
        return self.engine.predict_next_n_games(n_games)
    
    def get_confidence_level(self, target_winrate: float) -> float:
        """
        Calculate confidence that true winrate exceeds target.
        计算真实胜率超过目标的置信度。
        
        Args:
            target_winrate: Target winrate to compare against
            
        Returns:
            Probability that true winrate > target
        """
        from scipy import stats
        # P(p > target) = 1 - CDF(target)
        prob = 1 - stats.beta.cdf(
            target_winrate,
            self.engine.posterior_alpha,
            self.engine.posterior_beta
        )
        return prob
    
    def reset(self) -> None:
        """
        Reset all session data.
        重置所有会话数据。
        """
        self.sessions = []
        self.engine.reset()
