#!/usr/bin/env python3
"""
Command Line Interface for ORE Supply Winrate Analyzer
ORE Supply胜率分析器命令行界面
"""

import argparse
import sys
import json
from typing import Optional
from ore_analyzer import BayesianEngine, WinrateCalculator, InvestmentAdvisor
from ore_analyzer.visualizer import Visualizer


def print_separator(char='=', length=60):
    """Print a separator line."""
    print(char * length)


def print_section_header(title):
    """Print a section header."""
    print_separator()
    print(f"  {title}")
    print_separator()


def analyze_winrate(args):
    """Analyze winrate from provided data."""
    calculator = WinrateCalculator()
    
    # Add sessions
    if args.wins and args.losses:
        wins_list = [int(w) for w in args.wins.split(',')]
        losses_list = [int(l) for l in args.losses.split(',')]
        
        if len(wins_list) != len(losses_list):
            print("Error: Number of wins and losses must match")
            return 1
        
        for i, (wins, losses) in enumerate(zip(wins_list, losses_list)):
            calculator.add_session(wins, losses, f"Session {i+1}")
    
    # Get statistics
    overall_stats = calculator.get_overall_stats()
    
    print_section_header("OVERALL STATISTICS / 总体统计")
    print(f"Total Sessions / 总会话数: {overall_stats['total_sessions']}")
    print(f"Total Games / 总游戏数: {overall_stats['total_games']}")
    print(f"Total Wins / 总获胜数: {overall_stats['total_wins']}")
    print(f"Total Losses / 总失败数: {overall_stats['total_losses']}")
    print(f"\nSimple Winrate / 简单胜率: {overall_stats['simple_winrate']:.2%}")
    print(f"Bayesian Winrate / 贝叶斯胜率: {overall_stats['bayesian_winrate']:.2%}")
    ci_lower, ci_upper = overall_stats['credible_interval']
    print(f"95% Credible Interval / 95%可信区间: [{ci_lower:.2%}, {ci_upper:.2%}]")
    
    # Predictions
    if args.predict:
        print_section_header("PREDICTIONS / 预测")
        predictions = calculator.predict_future_performance(args.predict)
        print(f"Next {args.predict} games prediction / 接下来{args.predict}场比赛预测:")
        print(f"  Expected wins / 预期获胜: {predictions['expected_wins']:.1f}")
        print(f"  Win probability / 获胜概率: {predictions['win_probability']:.2%}")
    
    # Visualization
    if args.visualize:
        print("\nGenerating visualizations / 生成可视化图表...")
        Visualizer.plot_posterior_distribution(calculator.engine, "posterior_distribution.png")
        Visualizer.plot_session_performance(calculator, "session_performance.png")
        if args.predict:
            Visualizer.plot_prediction_distribution(calculator.engine, args.predict, 
                                                    "prediction_distribution.png")
        print("Visualizations saved / 可视化图表已保存!")
    
    return 0


def analyze_investment(args):
    """Provide investment advice."""
    engine = BayesianEngine()
    
    # Add data
    if args.wins and args.losses:
        wins = int(args.wins)
        losses = int(args.losses)
        engine.update(wins, losses)
    else:
        print("Error: Must provide wins and losses data")
        return 1
    
    advisor = InvestmentAdvisor(engine)
    
    print_section_header("INVESTMENT ANALYSIS / 投资分析")
    
    # Kelly Criterion
    if args.odds:
        kelly = advisor.kelly_criterion(args.odds)
        print(f"\nKelly Criterion Analysis (Odds: {args.odds}) / 凯利公式分析:")
        print(f"  Optimal bet percentage / 最优投注百分比: {kelly['recommended_bet_percentage']:.2f}%")
        print(f"  Conservative bet (Half Kelly) / 保守投注: {kelly['conservative_bet_percentage']:.2f}%")
        print(f"  Advice / 建议: {kelly['advice']}")
    
    # Generate full report
    if args.bankroll and args.odds:
        report = advisor.generate_investment_report(args.bankroll, args.odds)
        
        print_section_header("COMPREHENSIVE INVESTMENT REPORT / 综合投资报告")
        print(f"\nBankroll / 资金: {report['bankroll']}")
        print(f"Win Probability / 获胜概率: {report['win_probability']:.2%}")
        ci_lower, ci_upper = report['credible_interval']
        print(f"95% Credible Interval / 95%可信区间: [{ci_lower:.2%}, {ci_upper:.2%}]")
        
        print("\n--- Half Kelly Strategy (Recommended) / 半凯利策略（推荐） ---")
        hk = report['half_kelly']
        print(f"Bet Size / 投注规模: {hk['bet_size']:.2f}")
        print(f"Risk Level / 风险水平: {hk['risk']['risk_level']}")
        print(f"Risk of Ruin / 破产风险: {hk['risk']['risk_of_ruin']:.2%}")
        print(f"Expected Value / 期望值: {hk['expected_value']['expected_value']:.2f}")
        
        print(f"\n{report['overall_recommendation']}")
    
    # Visualization
    if args.visualize and args.odds:
        print("\nGenerating Kelly criterion visualization / 生成凯利公式可视化...")
        Visualizer.plot_kelly_criterion(engine, save_path="kelly_criterion.png")
        print("Visualization saved / 可视化图表已保存!")
    
    return 0


def interactive_mode():
    """Run in interactive mode."""
    print_section_header("ORE SUPPLY WINRATE ANALYZER - INTERACTIVE MODE")
    print("ORE供应胜率分析器 - 交互模式\n")
    
    calculator = WinrateCalculator()
    
    print("Enter your game sessions (enter 'done' when finished)")
    print("输入您的游戏会话（完成后输入'done'）\n")
    
    session_num = 1
    while True:
        print(f"\nSession {session_num}:")
        wins_input = input("  Wins / 获胜数: ")
        if wins_input.lower() == 'done':
            break
        
        losses_input = input("  Losses / 失败数: ")
        if losses_input.lower() == 'done':
            break
        
        try:
            wins = int(wins_input)
            losses = int(losses_input)
            calculator.add_session(wins, losses, f"Session {session_num}")
            print(f"  ✓ Added session {session_num}")
            session_num += 1
        except ValueError:
            print("  ✗ Invalid input, please enter numbers")
    
    if calculator.sessions:
        stats = calculator.get_overall_stats()
        print_section_header("RESULTS / 结果")
        print(f"Bayesian Winrate / 贝叶斯胜率: {stats['bayesian_winrate']:.2%}")
        ci_lower, ci_upper = stats['credible_interval']
        print(f"95% Credible Interval / 95%可信区间: [{ci_lower:.2%}, {ci_upper:.2%}]")
        
        # Ask for investment analysis
        print("\nWould you like investment advice? / 需要投资建议吗？ (y/n): ", end='')
        if input().lower() == 'y':
            odds = float(input("Enter win odds / 输入获胜赔率: "))
            bankroll = float(input("Enter bankroll / 输入资金: "))
            
            advisor = InvestmentAdvisor(calculator.engine)
            report = advisor.generate_investment_report(bankroll, odds)
            
            print(f"\nRecommended bet (Half Kelly) / 推荐投注（半凯利）: {report['half_kelly']['bet_size']:.2f}")
            print(f"Risk Level / 风险水平: {report['half_kelly']['risk']['risk_level']}")
    
    print("\nThank you for using ORE Winrate Analyzer!")
    print("感谢使用ORE胜率分析器！")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='ORE Supply Winrate Analyzer - 基于贝叶斯推理的游戏分析器',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples / 示例:
  # Analyze winrate / 分析胜率
  %(prog)s analyze --wins 15,20,18 --losses 10,15,12
  
  # With predictions / 带预测
  %(prog)s analyze --wins 30 --losses 20 --predict 10
  
  # Investment advice / 投资建议
  %(prog)s invest --wins 30 --losses 20 --odds 2.5 --bankroll 1000
  
  # Interactive mode / 交互模式
  %(prog)s interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze winrate')
    analyze_parser.add_argument('--wins', type=str, required=True,
                               help='Comma-separated wins per session')
    analyze_parser.add_argument('--losses', type=str, required=True,
                               help='Comma-separated losses per session')
    analyze_parser.add_argument('--predict', type=int,
                               help='Predict next N games')
    analyze_parser.add_argument('--visualize', action='store_true',
                               help='Generate visualizations')
    
    # Investment command
    invest_parser = subparsers.add_parser('invest', help='Investment advice')
    invest_parser.add_argument('--wins', type=str, required=True,
                              help='Total wins')
    invest_parser.add_argument('--losses', type=str, required=True,
                              help='Total losses')
    invest_parser.add_argument('--odds', type=float, required=True,
                              help='Win odds (e.g., 2.0 for 2x return)')
    invest_parser.add_argument('--bankroll', type=float,
                              help='Current bankroll')
    invest_parser.add_argument('--visualize', action='store_true',
                              help='Generate visualizations')
    
    # Interactive command
    subparsers.add_parser('interactive', help='Interactive mode')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    if args.command == 'analyze':
        return analyze_winrate(args)
    elif args.command == 'invest':
        return analyze_investment(args)
    elif args.command == 'interactive':
        interactive_mode()
        return 0
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
