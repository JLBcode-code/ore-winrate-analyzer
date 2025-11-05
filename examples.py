"""
Example usage of ORE Supply Winrate Analyzer
ORE Supply胜率分析器使用示例
"""

from ore_analyzer import BayesianEngine, WinrateCalculator, InvestmentAdvisor
from ore_analyzer.visualizer import Visualizer


def example_basic_analysis():
    """Basic winrate analysis example."""
    print("=" * 60)
    print("EXAMPLE 1: Basic Winrate Analysis")
    print("示例1：基础胜率分析")
    print("=" * 60)
    
    # Create calculator
    calculator = WinrateCalculator()
    
    # Add game sessions
    calculator.add_session(wins=30, losses=20, session_name="Morning Session")
    calculator.add_session(wins=25, losses=25, session_name="Afternoon Session")
    calculator.add_session(wins=20, losses=15, session_name="Evening Session")
    
    # Get overall statistics
    stats = calculator.get_overall_stats()
    
    print(f"\nTotal games played: {stats['total_games']}")
    print(f"Total wins: {stats['total_wins']}")
    print(f"Total losses: {stats['total_losses']}")
    print(f"\nSimple winrate: {stats['simple_winrate']:.2%}")
    print(f"Bayesian winrate: {stats['bayesian_winrate']:.2%}")
    
    lower, upper = stats['credible_interval']
    print(f"95% Credible Interval: [{lower:.2%}, {upper:.2%}]")
    
    # Session breakdown
    print("\nSession breakdown:")
    for session in calculator.get_session_stats():
        print(f"  {session['name']}: {session['winrate']:.2%} "
              f"({session['wins']}W - {session['losses']}L)")
    
    print("\n")


def example_predictions():
    """Example of future game predictions."""
    print("=" * 60)
    print("EXAMPLE 2: Future Game Predictions")
    print("示例2：未来游戏预测")
    print("=" * 60)
    
    # Create engine with data
    engine = BayesianEngine()
    engine.update(wins=60, losses=40)
    
    # Predict next 10 games
    prediction = engine.predict_next_n_games(n_games=10)
    
    print(f"\nPredictions for next 10 games:")
    print(f"  Expected wins: {prediction['expected_wins']:.1f}")
    print(f"  Median wins: {prediction['median_wins']:.0f}")
    print(f"  Standard deviation: {prediction['std_wins']:.1f}")
    print(f"  Range: {prediction['min_wins']:.0f} - {prediction['max_wins']:.0f}")
    print(f"  Win probability per game: {prediction['win_probability']:.2%}")
    
    print("\n")


def example_kelly_criterion():
    """Example of Kelly Criterion bet sizing."""
    print("=" * 60)
    print("EXAMPLE 3: Kelly Criterion Bet Sizing")
    print("示例3：凯利公式投注规模")
    print("=" * 60)
    
    # Create engine with data
    engine = BayesianEngine()
    engine.update(wins=55, losses=45)
    
    advisor = InvestmentAdvisor(engine)
    
    # Analyze different odds
    odds_list = [1.8, 2.0, 2.5, 3.0]
    
    print(f"\nWin probability: {engine.get_win_probability():.2%}\n")
    print("Kelly Criterion for different odds:")
    print(f"{'Odds':<8} {'Full Kelly':<12} {'Half Kelly':<12} {'Advice'}")
    print("-" * 70)
    
    for odds in odds_list:
        result = advisor.kelly_criterion(odds)
        print(f"{odds:<8.1f} {result['recommended_bet_percentage']:<12.2f}% "
              f"{result['conservative_bet_percentage']:<12.2f}% "
              f"{result['advice'][:30]}...")
    
    print("\n")


def example_risk_assessment():
    """Example of risk assessment."""
    print("=" * 60)
    print("EXAMPLE 4: Risk Assessment")
    print("示例4：风险评估")
    print("=" * 60)
    
    # Create engine with data
    engine = BayesianEngine()
    engine.update(wins=52, losses=48)
    
    advisor = InvestmentAdvisor(engine)
    
    # Assess different bet sizes
    bankroll = 1000
    bet_sizes = [50, 100, 150, 200]
    
    print(f"\nBankroll: ${bankroll}")
    print(f"Win probability: {engine.get_win_probability():.2%}\n")
    print("Risk assessment for different bet sizes:")
    print(f"{'Bet Size':<12} {'% of BR':<10} {'Risk Level':<15} {'Risk of Ruin'}")
    print("-" * 70)
    
    for bet_size in bet_sizes:
        result = advisor.risk_assessment(bankroll, bet_size, n_games=100)
        pct = (bet_size / bankroll) * 100
        print(f"${bet_size:<11} {pct:<10.1f}% {result['risk_level']:<15} "
              f"{result['risk_of_ruin']:.2%}")
    
    print("\n")


def example_comprehensive_report():
    """Example of comprehensive investment report."""
    print("=" * 60)
    print("EXAMPLE 5: Comprehensive Investment Report")
    print("示例5：综合投资报告")
    print("=" * 60)
    
    # Create engine with data
    engine = BayesianEngine()
    engine.update(wins=65, losses=35)
    
    advisor = InvestmentAdvisor(engine)
    
    # Generate report
    bankroll = 1000
    win_odds = 2.5
    report = advisor.generate_investment_report(bankroll, win_odds)
    
    print(f"\nBankroll: ${report['bankroll']}")
    print(f"Win odds: {report['win_odds']}x")
    print(f"Win probability: {report['win_probability']:.2%}")
    
    lower, upper = report['credible_interval']
    print(f"95% Credible Interval: [{lower:.2%}, {upper:.2%}]")
    
    print("\n--- Full Kelly Strategy ---")
    fk = report['full_kelly']
    print(f"Bet size: ${fk['bet_size']:.2f}")
    print(f"Risk level: {fk['risk']['risk_level']}")
    print(f"Risk of ruin: {fk['risk']['risk_of_ruin']:.2%}")
    print(f"Expected value: ${fk['expected_value']['expected_value']:.2f}")
    
    print("\n--- Half Kelly Strategy (Recommended) ---")
    hk = report['half_kelly']
    print(f"Bet size: ${hk['bet_size']:.2f}")
    print(f"Risk level: {hk['risk']['risk_level']}")
    print(f"Risk of ruin: {hk['risk']['risk_of_ruin']:.2%}")
    print(f"Expected value: ${hk['expected_value']['expected_value']:.2f}")
    
    print(f"\n--- Overall Recommendation ---")
    print(report['overall_recommendation'])
    
    print("\n")


def example_visualizations():
    """Example of creating visualizations."""
    print("=" * 60)
    print("EXAMPLE 6: Creating Visualizations")
    print("示例6：创建可视化图表")
    print("=" * 60)
    
    # Create calculator with data
    calculator = WinrateCalculator()
    calculator.add_session(wins=30, losses=20, session_name="Week 1")
    calculator.add_session(wins=28, losses=22, session_name="Week 2")
    calculator.add_session(wins=35, losses=15, session_name="Week 3")
    calculator.add_session(wins=25, losses=25, session_name="Week 4")
    
    print("\nGenerating visualizations...")
    
    # Create visualizations
    Visualizer.plot_posterior_distribution(
        calculator.engine, 
        save_path="examples/posterior_distribution.png"
    )
    print("  ✓ Posterior distribution saved")
    
    Visualizer.plot_session_performance(
        calculator,
        save_path="examples/session_performance.png"
    )
    print("  ✓ Session performance saved")
    
    Visualizer.plot_prediction_distribution(
        calculator.engine,
        n_games=20,
        save_path="examples/prediction_distribution.png"
    )
    print("  ✓ Prediction distribution saved")
    
    Visualizer.plot_kelly_criterion(
        calculator.engine,
        win_odds_range=(1.5, 3.5),
        save_path="examples/kelly_criterion.png"
    )
    print("  ✓ Kelly criterion plot saved")
    
    print("\nAll visualizations saved to examples/ directory!")
    print("\n")


def main():
    """Run all examples."""
    import os
    
    # Create examples directory for visualizations
    os.makedirs("examples", exist_ok=True)
    
    print("\n" + "=" * 60)
    print("ORE SUPPLY WINRATE ANALYZER - EXAMPLES")
    print("ORE供应胜率分析器 - 示例")
    print("=" * 60 + "\n")
    
    # Run examples
    example_basic_analysis()
    example_predictions()
    example_kelly_criterion()
    example_risk_assessment()
    example_comprehensive_report()
    example_visualizations()
    
    print("=" * 60)
    print("All examples completed!")
    print("所有示例已完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
