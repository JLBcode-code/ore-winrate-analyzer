"""
Visualization tools for ORE Supply Analyzer
ORE Supply分析器的可视化工具
"""

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Optional
from .bayesian_engine import BayesianEngine
from .winrate_calculator import WinrateCalculator


# Set style
sns.set_style("whitegrid")
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial Unicode MS', 'SimHei']
plt.rcParams['axes.unicode_minus'] = False


class Visualizer:
    """
    Create visualizations for game analysis.
    创建游戏分析的可视化图表。
    """
    
    @staticmethod
    def plot_posterior_distribution(engine: BayesianEngine, 
                                    save_path: Optional[str] = None) -> None:
        """
        Plot the posterior probability distribution.
        绘制后验概率分布。
        
        Args:
            engine: BayesianEngine instance
            save_path: Optional path to save the figure
        """
        x, y = engine.get_probability_distribution()
        mean_prob = engine.get_win_probability()
        lower, upper = engine.get_credible_interval(0.95)
        
        plt.figure(figsize=(10, 6))
        plt.plot(x, y, 'b-', linewidth=2, label='Posterior Distribution')
        plt.axvline(mean_prob, color='r', linestyle='--', linewidth=2, 
                   label=f'Mean: {mean_prob:.3f}')
        plt.axvline(lower, color='g', linestyle=':', linewidth=1.5,
                   label=f'95% CI: [{lower:.3f}, {upper:.3f}]')
        plt.axvline(upper, color='g', linestyle=':', linewidth=1.5)
        plt.fill_between(x, 0, y, where=(x >= lower) & (x <= upper), 
                        alpha=0.3, color='green')
        
        plt.xlabel('Win Probability / 获胜概率', fontsize=12)
        plt.ylabel('Probability Density / 概率密度', fontsize=12)
        plt.title('Posterior Distribution of Win Probability\n获胜概率的后验分布', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.tight_layout()
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_session_performance(calculator: WinrateCalculator,
                                save_path: Optional[str] = None) -> None:
        """
        Plot performance across sessions.
        绘制各会话的表现。
        
        Args:
            calculator: WinrateCalculator instance
            save_path: Optional path to save the figure
        """
        sessions = calculator.get_session_stats()
        
        if not sessions:
            print("No session data to plot / 没有会话数据可绘制")
            return
        
        names = [s['name'] for s in sessions]
        winrates = [s['winrate'] * 100 for s in sessions]
        
        plt.figure(figsize=(12, 6))
        bars = plt.bar(range(len(names)), winrates, color='skyblue', edgecolor='navy')
        
        # Color bars based on winrate
        for i, bar in enumerate(bars):
            if winrates[i] >= 60:
                bar.set_color('green')
            elif winrates[i] >= 50:
                bar.set_color('yellow')
            else:
                bar.set_color('red')
        
        plt.axhline(50, color='black', linestyle='--', linewidth=1, 
                   label='50% Baseline')
        
        plt.xlabel('Session / 会话', fontsize=12)
        plt.ylabel('Winrate (%) / 胜率 (%)', fontsize=12)
        plt.title('Session Performance / 会话表现', fontsize=14, fontweight='bold')
        plt.xticks(range(len(names)), names, rotation=45, ha='right')
        plt.legend()
        plt.grid(True, alpha=0.3, axis='y')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.tight_layout()
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_prediction_distribution(engine: BayesianEngine, n_games: int = 10,
                                     save_path: Optional[str] = None) -> None:
        """
        Plot prediction distribution for future games.
        绘制未来游戏的预测分布。
        
        Args:
            engine: BayesianEngine instance
            n_games: Number of future games to predict
            save_path: Optional path to save the figure
        """
        # Run many simulations
        n_simulations = 10000
        p_samples = np.random.beta(engine.posterior_alpha, engine.posterior_beta, 
                                   n_simulations)
        wins_distribution = np.random.binomial(n_games, p_samples)
        
        plt.figure(figsize=(10, 6))
        
        # Create histogram
        counts, bins, patches = plt.hist(wins_distribution, bins=range(n_games + 2),
                                        density=True, alpha=0.7, color='blue',
                                        edgecolor='black')
        
        # Color bars
        for i, patch in enumerate(patches):
            if i / n_games > 0.6:
                patch.set_facecolor('green')
            elif i / n_games > 0.4:
                patch.set_facecolor('yellow')
            else:
                patch.set_facecolor('red')
        
        expected_wins = engine.get_win_probability() * n_games
        plt.axvline(expected_wins, color='red', linestyle='--', linewidth=2,
                   label=f'Expected: {expected_wins:.1f} wins')
        
        plt.xlabel(f'Number of Wins in {n_games} Games / {n_games}场比赛的获胜数', 
                  fontsize=12)
        plt.ylabel('Probability Density / 概率密度', fontsize=12)
        plt.title(f'Prediction Distribution for Next {n_games} Games\n'
                 f'接下来{n_games}场比赛的预测分布', 
                 fontsize=14, fontweight='bold')
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3, axis='y')
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.tight_layout()
            plt.show()
        
        plt.close()
    
    @staticmethod
    def plot_kelly_criterion(engine: BayesianEngine, win_odds_range: tuple = (1.5, 3.0),
                           save_path: Optional[str] = None) -> None:
        """
        Plot Kelly criterion recommendation across different odds.
        绘制不同赔率下的凯利公式推荐。
        
        Args:
            engine: BayesianEngine instance
            win_odds_range: Tuple of (min_odds, max_odds)
            save_path: Optional path to save the figure
        """
        from .investment_advisor import InvestmentAdvisor
        
        advisor = InvestmentAdvisor(engine)
        odds_values = np.linspace(win_odds_range[0], win_odds_range[1], 100)
        kelly_fractions = []
        
        for odds in odds_values:
            result = advisor.kelly_criterion(odds)
            kelly_fractions.append(result['kelly_fraction'] * 100)
        
        plt.figure(figsize=(10, 6))
        plt.plot(odds_values, kelly_fractions, 'b-', linewidth=2)
        plt.fill_between(odds_values, 0, kelly_fractions, alpha=0.3)
        
        plt.xlabel('Win Odds / 获胜赔率', fontsize=12)
        plt.ylabel('Kelly Bet Percentage (%) / 凯利投注百分比 (%)', fontsize=12)
        plt.title('Kelly Criterion Recommendation vs Odds\n凯利公式推荐 vs 赔率', 
                 fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            plt.tight_layout()
            plt.show()
        
        plt.close()
