"""
Investment Advisor for ORE Supply Game
ORE Supply游戏投资顾问
"""

import numpy as np
from typing import Dict, List, Optional
from .bayesian_engine import BayesianEngine


class InvestmentAdvisor:
    """
    Provide investment advice based on Bayesian analysis of game performance.
    基于贝叶斯分析提供投资建议。
    """
    
    def __init__(self, engine: BayesianEngine):
        """
        Initialize the investment advisor.
        
        Args:
            engine: Bayesian engine with game data
        """
        self.engine = engine
    
    def kelly_criterion(self, win_odds: float, loss_odds: float = 1.0) -> Dict:
        """
        Calculate optimal bet size using Kelly Criterion.
        使用凯利公式计算最优投注规模。
        
        Args:
            win_odds: Odds for winning (e.g., 2.0 means you get 2x your bet)
            loss_odds: Odds for losing (typically 1.0, you lose your bet)
            
        Returns:
            Dictionary with Kelly criterion results
        """
        p = self.engine.get_win_probability()
        q = 1 - p
        
        # Kelly formula: f = (bp - q) / b
        # where b is the net odds (win_odds - 1)
        b = win_odds - 1
        
        kelly_fraction = (b * p - q) / b if b > 0 else 0
        
        # Ensure non-negative (don't bet if expectation is negative)
        kelly_fraction = max(0, kelly_fraction)
        
        # Calculate expected growth
        if kelly_fraction > 0:
            expected_growth = p * np.log(1 + b * kelly_fraction) + q * np.log(1 - kelly_fraction)
        else:
            expected_growth = 0
        
        return {
            'kelly_fraction': kelly_fraction,
            'recommended_bet_percentage': kelly_fraction * 100,
            'conservative_bet_percentage': kelly_fraction * 0.5 * 100,  # Half Kelly for safety
            'expected_growth_rate': expected_growth,
            'advice': self._get_kelly_advice(kelly_fraction, p, win_odds)
        }
    
    def _get_kelly_advice(self, kelly_fraction: float, win_prob: float, win_odds: float) -> str:
        """
        Generate human-readable advice based on Kelly criterion.
        
        Args:
            kelly_fraction: Calculated Kelly fraction
            win_prob: Win probability
            win_odds: Win odds
            
        Returns:
            Advice string
        """
        if kelly_fraction <= 0:
            return "不建议投注 - 预期收益为负 (Do not bet - negative expected value)"
        elif kelly_fraction < 0.05:
            return "非常小的投注 - 优势很小 (Very small bet - minimal edge)"
        elif kelly_fraction < 0.15:
            return "适度投注 - 有一定优势 (Moderate bet - decent edge)"
        elif kelly_fraction < 0.30:
            return "较大投注 - 显著优势 (Larger bet - significant edge)"
        else:
            return "大额投注 - 强大优势 (Large bet - strong edge), 但建议谨慎 (but be cautious)"
    
    def risk_assessment(self, bankroll: float, bet_size: float, n_games: int = 100) -> Dict:
        """
        Assess risk of ruin for given bankroll and bet size.
        评估给定资金和投注规模的破产风险。
        
        Args:
            bankroll: Total bankroll
            bet_size: Size of each bet
            n_games: Number of games to simulate
            
        Returns:
            Risk assessment results
        """
        if bet_size >= bankroll:
            return {
                'risk_level': 'EXTREME',
                'risk_of_ruin': 1.0,
                'advice': '投注规模过大 - 立即减少 (Bet size too large - reduce immediately)'
            }
        
        p = self.engine.get_win_probability()
        
        # Monte Carlo simulation
        n_simulations = 10000
        ruins = 0
        
        for _ in range(n_simulations):
            current_bankroll = bankroll
            for _ in range(n_games):
                if np.random.random() < p:
                    current_bankroll += bet_size
                else:
                    current_bankroll -= bet_size
                
                if current_bankroll <= 0:
                    ruins += 1
                    break
        
        risk_of_ruin = ruins / n_simulations
        
        # Categorize risk
        if risk_of_ruin < 0.01:
            risk_level = 'LOW'
            advice = '风险可接受 (Acceptable risk)'
        elif risk_of_ruin < 0.05:
            risk_level = 'MODERATE'
            advice = '中等风险 - 谨慎监控 (Moderate risk - monitor carefully)'
        elif risk_of_ruin < 0.20:
            risk_level = 'HIGH'
            advice = '高风险 - 考虑减少投注 (High risk - consider reducing bet)'
        else:
            risk_level = 'EXTREME'
            advice = '极高风险 - 强烈建议减少投注 (Extreme risk - strongly reduce bet)'
        
        return {
            'risk_level': risk_level,
            'risk_of_ruin': risk_of_ruin,
            'bet_to_bankroll_ratio': bet_size / bankroll,
            'advice': advice
        }
    
    def expected_value_analysis(self, bet_amount: float, win_return: float, 
                                loss_amount: float = None) -> Dict:
        """
        Calculate expected value for a bet.
        计算投注的期望值。
        
        Args:
            bet_amount: Amount to bet
            win_return: Total return if win (including original bet)
            loss_amount: Amount lost if lose (default: bet_amount)
            
        Returns:
            Expected value analysis
        """
        if loss_amount is None:
            loss_amount = bet_amount
        
        p = self.engine.get_win_probability()
        lower, upper = self.engine.get_credible_interval(0.95)
        
        # Expected value
        ev = p * (win_return - bet_amount) - (1 - p) * loss_amount
        
        # EV with credible interval bounds
        ev_lower = lower * (win_return - bet_amount) - (1 - lower) * loss_amount
        ev_upper = upper * (win_return - bet_amount) - (1 - upper) * loss_amount
        
        return {
            'expected_value': ev,
            'ev_percentage': (ev / bet_amount) * 100,
            'ev_credible_interval': (ev_lower, ev_upper),
            'win_probability': p,
            'positive_ev': ev > 0,
            'recommendation': self._get_ev_recommendation(ev, bet_amount)
        }
    
    def _get_ev_recommendation(self, ev: float, bet_amount: float) -> str:
        """
        Generate recommendation based on expected value.
        
        Args:
            ev: Expected value
            bet_amount: Bet amount
            
        Returns:
            Recommendation string
        """
        ev_pct = (ev / bet_amount) * 100 if bet_amount > 0 else 0
        
        if ev_pct <= -10:
            return "强烈不推荐 - 期望损失很大 (Strongly not recommended - large expected loss)"
        elif ev_pct < 0:
            return "不推荐 - 负期望值 (Not recommended - negative EV)"
        elif ev_pct < 5:
            return "边缘投注 - 期望值很小 (Marginal bet - small positive EV)"
        elif ev_pct < 15:
            return "推荐 - 良好的期望值 (Recommended - good EV)"
        else:
            return "强烈推荐 - 优秀的期望值 (Highly recommended - excellent EV)"
    
    def generate_investment_report(self, bankroll: float, win_odds: float) -> Dict:
        """
        Generate comprehensive investment report.
        生成综合投资报告。
        
        Args:
            bankroll: Current bankroll
            win_odds: Odds for winning
            
        Returns:
            Complete investment report
        """
        kelly = self.kelly_criterion(win_odds)
        
        # Calculate recommended bet sizes
        full_kelly_bet = bankroll * kelly['kelly_fraction']
        half_kelly_bet = bankroll * kelly['kelly_fraction'] * 0.5
        
        # Risk assessment
        risk_full = self.risk_assessment(bankroll, full_kelly_bet, n_games=100)
        risk_half = self.risk_assessment(bankroll, half_kelly_bet, n_games=100)
        
        # Expected value
        ev_full = self.expected_value_analysis(full_kelly_bet, full_kelly_bet * win_odds)
        ev_half = self.expected_value_analysis(half_kelly_bet, half_kelly_bet * win_odds)
        
        return {
            'bankroll': bankroll,
            'win_odds': win_odds,
            'win_probability': self.engine.get_win_probability(),
            'credible_interval': self.engine.get_credible_interval(0.95),
            'kelly_analysis': kelly,
            'full_kelly': {
                'bet_size': full_kelly_bet,
                'risk': risk_full,
                'expected_value': ev_full
            },
            'half_kelly': {
                'bet_size': half_kelly_bet,
                'risk': risk_half,
                'expected_value': ev_half
            },
            'overall_recommendation': self._generate_overall_recommendation(
                kelly, risk_half, ev_half
            )
        }
    
    def _generate_overall_recommendation(self, kelly: Dict, risk: Dict, ev: Dict) -> str:
        """
        Generate overall investment recommendation.
        
        Args:
            kelly: Kelly criterion results
            risk: Risk assessment results
            ev: Expected value analysis
            
        Returns:
            Overall recommendation
        """
        recommendations = []
        
        if kelly['kelly_fraction'] <= 0:
            return "总体建议：不要投注。当前数据显示负期望值。\nOverall: Do not bet. Current data shows negative expected value."
        
        recommendations.append(f"建议使用 {kelly['conservative_bet_percentage']:.1f}% 的资金（保守凯利）")
        recommendations.append(f"Recommend using {kelly['conservative_bet_percentage']:.1f}% of bankroll (conservative Kelly)")
        
        if risk['risk_level'] in ['LOW', 'MODERATE']:
            recommendations.append(f"风险水平：{risk['risk_level']} - 可以接受")
            recommendations.append(f"Risk level: {risk['risk_level']} - Acceptable")
        else:
            recommendations.append(f"警告：风险水平 {risk['risk_level']}")
            recommendations.append(f"Warning: Risk level {risk['risk_level']}")
        
        if ev['positive_ev']:
            recommendations.append(f"期望收益：+{ev['ev_percentage']:.2f}%")
            recommendations.append(f"Expected return: +{ev['ev_percentage']:.2f}%")
        
        return "\n".join(recommendations)
