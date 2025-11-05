# ORE Supply Winrate Analyzer

**基于贝叶斯推理的 ORE Supply 游戏智能分析器 - 提供精准概率预测和投资建议的数据科学工具**

A sophisticated Bayesian inference-based analyzer for ORE Supply game that provides accurate probability predictions and investment advice using advanced data science techniques.

## 🌟 Features / 功能特性

- **Bayesian Inference Engine / 贝叶斯推理引擎**: Uses Beta-Binomial conjugate priors for robust probability estimation
- **Winrate Calculator / 胜率计算器**: Comprehensive winrate analysis with credible intervals
- **Investment Advisor / 投资顾问**: Kelly Criterion-based bet sizing and risk management
- **Data Visualization / 数据可视化**: Beautiful charts and graphs for analysis
- **CLI Interface / 命令行界面**: Easy-to-use command line tools and interactive mode
- **Bilingual Support / 双语支持**: Full Chinese and English documentation

## 📊 Core Capabilities / 核心能力

### 1. Bayesian Probability Analysis
- Posterior distribution calculation
- Credible interval estimation (95% default)
- Posterior predictive distribution for future games
- Historical tracking of game performance

### 2. Winrate Analysis
- Session-based performance tracking
- Overall statistics aggregation
- Streak probability calculations
- Break-even rate analysis

### 3. Investment Optimization
- Kelly Criterion for optimal bet sizing
- Risk of ruin assessment
- Expected value analysis
- Comprehensive investment reports

### 4. Visualizations
- Posterior probability distributions
- Session performance charts
- Future prediction distributions
- Kelly criterion optimization curves

## 🚀 Installation / 安装

```bash
# Clone the repository
git clone https://github.com/JLBcode-code/ore-winrate-analyzer.git
cd ore-winrate-analyzer

# Install dependencies
pip install -r requirements.txt
```

## 💻 Usage / 使用方法

### Command Line Interface

#### 1. Analyze Winrate / 分析胜率

```bash
# Single session
python cli.py analyze --wins 30 --losses 20

# Multiple sessions
python cli.py analyze --wins 15,20,18 --losses 10,15,12

# With predictions for next 10 games
python cli.py analyze --wins 30 --losses 20 --predict 10

# With visualizations
python cli.py analyze --wins 30 --losses 20 --predict 10 --visualize
```

#### 2. Investment Advice / 投资建议

```bash
# Basic Kelly Criterion analysis
python cli.py invest --wins 30 --losses 20 --odds 2.5

# Full investment report
python cli.py invest --wins 30 --losses 20 --odds 2.5 --bankroll 1000

# With visualizations
python cli.py invest --wins 30 --losses 20 --odds 2.5 --bankroll 1000 --visualize
```

#### 3. Interactive Mode / 交互模式

```bash
python cli.py interactive
```

### Python API

```python
from ore_analyzer import BayesianEngine, WinrateCalculator, InvestmentAdvisor
from ore_analyzer.visualizer import Visualizer

# Create calculator and add sessions
calculator = WinrateCalculator()
calculator.add_session(wins=30, losses=20, session_name="Session 1")
calculator.add_session(wins=25, losses=25, session_name="Session 2")

# Get statistics
stats = calculator.get_overall_stats()
print(f"Bayesian Winrate: {stats['bayesian_winrate']:.2%}")
print(f"95% CI: {stats['credible_interval']}")

# Predict future performance
prediction = calculator.predict_future_performance(n_games=10)
print(f"Expected wins in next 10 games: {prediction['expected_wins']:.1f}")

# Investment advice
advisor = InvestmentAdvisor(calculator.engine)
kelly = advisor.kelly_criterion(win_odds=2.5)
print(f"Recommended bet: {kelly['recommended_bet_percentage']:.2f}%")

# Generate comprehensive report
report = advisor.generate_investment_report(bankroll=1000, win_odds=2.5)
print(report['overall_recommendation'])

# Create visualizations
Visualizer.plot_posterior_distribution(calculator.engine, "posterior.png")
Visualizer.plot_session_performance(calculator, "sessions.png")
```

## 📈 Example Output / 示例输出

### Winrate Analysis

```
============================================================
  OVERALL STATISTICS / 总体统计
============================================================
Total Sessions / 总会话数: 2
Total Games / 总游戏数: 100
Total Wins / 总获胜数: 55
Total Losses / 总失败数: 45

Simple Winrate / 简单胜率: 55.00%
Bayesian Winrate / 贝叶斯胜率: 54.90%
95% Credible Interval / 95%可信区间: [45.12%, 64.48%]
```

### Investment Report

```
============================================================
  COMPREHENSIVE INVESTMENT REPORT / 综合投资报告
============================================================

Bankroll / 资金: 1000
Win Probability / 获胜概率: 54.90%
95% Credible Interval / 95%可信区间: [45.12%, 64.48%]

--- Half Kelly Strategy (Recommended) / 半凯利策略（推荐） ---
Bet Size / 投注规模: 53.40
Risk Level / 风险水平: LOW
Risk of Ruin / 破产风险: 0.23%
Expected Value / 期望值: 2.93

建议使用 5.3% 的资金（保守凯利）
Recommend using 5.3% of bankroll (conservative Kelly)
风险水平：LOW - 可以接受
Risk level: LOW - Acceptable
期望收益：+5.49%
Expected return: +5.49%
```

## 🔬 Methodology / 方法论

### Bayesian Inference

The analyzer uses **Beta-Binomial conjugate priors** for Bayesian inference:

- **Prior**: Beta(α, β) distribution representing initial beliefs
- **Likelihood**: Binomial distribution for observed wins/losses
- **Posterior**: Beta(α + wins, β + losses) updated beliefs

This approach provides:
- Robust probability estimates even with limited data
- Natural quantification of uncertainty via credible intervals
- Ability to incorporate prior knowledge
- Posterior predictive distribution for future games

### Kelly Criterion

Optimal bet sizing using the Kelly Criterion:

```
f* = (bp - q) / b
```

Where:
- f* = fraction of bankroll to bet
- b = net odds received on the bet
- p = probability of winning
- q = probability of losing (1-p)

We recommend using **Half Kelly** (f*/2) for reduced volatility while maintaining most of the growth rate.

## 📚 Mathematical Background / 数学背景

### Beta Distribution

The posterior distribution follows:

```
p(θ|data) = Beta(α + wins, β + losses)
```

Expected value (mean):
```
E[θ] = α / (α + β)
```

### Credible Intervals

95% Credible Interval uses the Beta quantile function:
```
CI = [Beta_inv(0.025, α, β), Beta_inv(0.975, α, β)]
```

### Risk of Ruin

Calculated via Monte Carlo simulation:
- Simulate N game sequences
- Track bankroll evolution
- Estimate probability of bankroll reaching 0

## 🛠️ Requirements / 依赖要求

- Python 3.7+
- NumPy >= 1.21.0
- SciPy >= 1.7.0
- Pandas >= 1.3.0
- Matplotlib >= 3.4.0
- Seaborn >= 0.11.0

## 📝 License / 许可证

MIT License

## 👨‍💻 Author / 作者

JLBcode

## 🤝 Contributing / 贡献

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献！请随时提交 Pull Request。

## 📧 Contact / 联系方式

For questions or support, please open an issue on GitHub.

如有问题或需要支持，请在 GitHub 上开启 issue。

## 🌐 Related Links / 相关链接

- [ORE Supply](https://ore.supply/)
- [Bayesian Inference](https://en.wikipedia.org/wiki/Bayesian_inference)
- [Kelly Criterion](https://en.wikipedia.org/wiki/Kelly_criterion)

---

**Note**: This tool is for educational and analytical purposes. Always gamble responsibly.

**注意**: 此工具仅用于教育和分析目的。请理性游戏。
