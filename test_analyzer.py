"""
Unit tests for ORE Supply Winrate Analyzer
"""

import unittest
import numpy as np
from ore_analyzer import BayesianEngine, WinrateCalculator, InvestmentAdvisor


class TestBayesianEngine(unittest.TestCase):
    """Tests for BayesianEngine class."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = BayesianEngine()
        self.assertEqual(engine.prior_alpha, 1.0)
        self.assertEqual(engine.prior_beta, 1.0)
        self.assertEqual(engine.posterior_alpha, 1.0)
        self.assertEqual(engine.posterior_beta, 1.0)
        self.assertEqual(len(engine.history), 0)
    
    def test_update(self):
        """Test updating with wins and losses."""
        engine = BayesianEngine()
        engine.update(wins=30, losses=20)
        
        self.assertEqual(engine.posterior_alpha, 31.0)
        self.assertEqual(engine.posterior_beta, 21.0)
        self.assertEqual(len(engine.history), 1)
    
    def test_win_probability(self):
        """Test win probability calculation."""
        engine = BayesianEngine()
        engine.update(wins=60, losses=40)
        
        prob = engine.get_win_probability()
        # With Beta(1,1) prior, posterior is Beta(61, 41)
        # Expected value = alpha / (alpha + beta) = 61 / 102
        expected = 61 / 102
        self.assertAlmostEqual(prob, expected, places=5)
    
    def test_credible_interval(self):
        """Test credible interval calculation."""
        engine = BayesianEngine()
        engine.update(wins=50, losses=50)
        
        lower, upper = engine.get_credible_interval(0.95)
        
        # Should be symmetric around 0.5
        self.assertLess(lower, 0.5)
        self.assertGreater(upper, 0.5)
        self.assertGreater(upper - lower, 0)
    
    def test_predict_next_n_games(self):
        """Test game prediction."""
        engine = BayesianEngine()
        engine.update(wins=60, losses=40)
        
        prediction = engine.predict_next_n_games(n_games=10, n_simulations=1000)
        
        self.assertIn('expected_wins', prediction)
        self.assertIn('win_probability', prediction)
        self.assertGreater(prediction['expected_wins'], 0)
        self.assertLessEqual(prediction['expected_wins'], 10)
    
    def test_reset(self):
        """Test engine reset."""
        engine = BayesianEngine()
        engine.update(wins=30, losses=20)
        engine.reset()
        
        self.assertEqual(engine.posterior_alpha, 1.0)
        self.assertEqual(engine.posterior_beta, 1.0)
        self.assertEqual(len(engine.history), 0)


class TestWinrateCalculator(unittest.TestCase):
    """Tests for WinrateCalculator class."""
    
    def test_add_session(self):
        """Test adding sessions."""
        calc = WinrateCalculator()
        calc.add_session(wins=30, losses=20, session_name="Test Session")
        
        self.assertEqual(len(calc.sessions), 1)
        self.assertEqual(calc.sessions[0]['name'], "Test Session")
        self.assertEqual(calc.sessions[0]['wins'], 30)
        self.assertEqual(calc.sessions[0]['losses'], 20)
    
    def test_overall_stats(self):
        """Test overall statistics calculation."""
        calc = WinrateCalculator()
        calc.add_session(wins=30, losses=20)
        calc.add_session(wins=25, losses=25)
        
        stats = calc.get_overall_stats()
        
        self.assertEqual(stats['total_sessions'], 2)
        self.assertEqual(stats['total_games'], 100)
        self.assertEqual(stats['total_wins'], 55)
        self.assertEqual(stats['total_losses'], 45)
        self.assertAlmostEqual(stats['simple_winrate'], 0.55)
    
    def test_streak_probability(self):
        """Test streak probability calculation."""
        calc = WinrateCalculator()
        calc.add_session(wins=50, losses=50)
        
        # Probability of 2 consecutive wins
        prob = calc.calculate_streak_probability(n_consecutive_wins=2)
        
        self.assertGreater(prob, 0)
        self.assertLess(prob, 1)
    
    def test_break_even_rate(self):
        """Test break-even rate calculation."""
        calc = WinrateCalculator()
        calc.add_session(wins=60, losses=40)
        
        result = calc.calculate_break_even_rate(win_reward=1.0, loss_penalty=1.0)
        
        self.assertIn('break_even_winrate', result)
        self.assertIn('above_break_even', result)
        self.assertEqual(result['break_even_winrate'], 0.5)


class TestInvestmentAdvisor(unittest.TestCase):
    """Tests for InvestmentAdvisor class."""
    
    def setUp(self):
        """Set up test engine."""
        self.engine = BayesianEngine()
        self.engine.update(wins=60, losses=40)
        self.advisor = InvestmentAdvisor(self.engine)
    
    def test_kelly_criterion(self):
        """Test Kelly criterion calculation."""
        result = self.advisor.kelly_criterion(win_odds=2.5)
        
        self.assertIn('kelly_fraction', result)
        self.assertIn('recommended_bet_percentage', result)
        self.assertIn('advice', result)
        self.assertGreater(result['kelly_fraction'], 0)
    
    def test_kelly_negative_ev(self):
        """Test Kelly with negative expected value."""
        engine = BayesianEngine()
        engine.update(wins=30, losses=70)
        advisor = InvestmentAdvisor(engine)
        
        result = advisor.kelly_criterion(win_odds=1.5)
        
        # Should recommend not betting
        self.assertEqual(result['kelly_fraction'], 0)
    
    def test_risk_assessment(self):
        """Test risk assessment."""
        result = self.advisor.risk_assessment(bankroll=1000, bet_size=50, n_games=100)
        
        self.assertIn('risk_level', result)
        self.assertIn('risk_of_ruin', result)
        self.assertGreater(result['risk_of_ruin'], 0)
        self.assertLess(result['risk_of_ruin'], 1)
    
    def test_expected_value_analysis(self):
        """Test expected value calculation."""
        result = self.advisor.expected_value_analysis(
            bet_amount=100,
            win_return=250,
            loss_amount=100
        )
        
        self.assertIn('expected_value', result)
        self.assertIn('positive_ev', result)
        self.assertIn('recommendation', result)
    
    def test_comprehensive_report(self):
        """Test comprehensive investment report generation."""
        report = self.advisor.generate_investment_report(
            bankroll=1000,
            win_odds=2.5
        )
        
        self.assertIn('kelly_analysis', report)
        self.assertIn('full_kelly', report)
        self.assertIn('half_kelly', report)
        self.assertIn('overall_recommendation', report)


class TestEdgeCases(unittest.TestCase):
    """Tests for edge cases and error handling."""
    
    def test_zero_games(self):
        """Test with zero games."""
        calc = WinrateCalculator()
        stats = calc.get_overall_stats()
        
        self.assertEqual(stats['total_games'], 0)
        self.assertEqual(stats['simple_winrate'], 0)
    
    def test_all_wins(self):
        """Test with 100% winrate."""
        calc = WinrateCalculator()
        calc.add_session(wins=100, losses=0)
        
        stats = calc.get_overall_stats()
        self.assertEqual(stats['simple_winrate'], 1.0)
    
    def test_all_losses(self):
        """Test with 0% winrate."""
        calc = WinrateCalculator()
        calc.add_session(wins=0, losses=100)
        
        stats = calc.get_overall_stats()
        self.assertEqual(stats['simple_winrate'], 0.0)
    
    def test_extreme_bankroll_ratio(self):
        """Test with extreme bet to bankroll ratio."""
        engine = BayesianEngine()
        engine.update(wins=50, losses=50)
        advisor = InvestmentAdvisor(engine)
        
        # Bet size >= bankroll
        result = advisor.risk_assessment(bankroll=100, bet_size=100, n_games=10)
        
        self.assertEqual(result['risk_level'], 'EXTREME')
        self.assertEqual(result['risk_of_ruin'], 1.0)


if __name__ == '__main__':
    unittest.main()
