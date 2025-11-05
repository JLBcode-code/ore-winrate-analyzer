# Quick Start Guide

## ORE Supply Winrate Analyzer / ORE供应胜率分析器

快速开始指南 - Get started in 5 minutes!

### 1. Installation / 安装

```bash
# Clone the repository
git clone https://github.com/JLBcode-code/ore-winrate-analyzer.git
cd ore-winrate-analyzer

# Install dependencies
pip install -r requirements.txt
```

### 2. Quick Examples / 快速示例

#### Analyze Your Winrate / 分析胜率

```bash
# Simple analysis
python cli.py analyze --wins 30 --losses 20

# Multiple sessions
python cli.py analyze --wins 15,20,18 --losses 10,15,12 --predict 10 --visualize
```

Output:
```
Total Games: 50
Bayesian Winrate: 59.62%
95% Credible Interval: [46.11%, 72.42%]
```

#### Get Investment Advice / 获取投资建议

```bash
# Kelly Criterion analysis
python cli.py invest --wins 60 --losses 40 --odds 2.5 --bankroll 1000
```

Output:
```
Recommended bet (Half Kelly): 16.5% of bankroll
Risk Level: HIGH
Expected return: +49.51%
```

#### Interactive Mode / 交互模式

```bash
python cli.py interactive
```

### 3. Python API Quick Start

```python
from ore_analyzer import WinrateCalculator, InvestmentAdvisor

# Create calculator
calc = WinrateCalculator()
calc.add_session(wins=60, losses=40)

# Get statistics
stats = calc.get_overall_stats()
print(f"Winrate: {stats['bayesian_winrate']:.2%}")

# Investment advice
advisor = InvestmentAdvisor(calc.engine)
kelly = advisor.kelly_criterion(win_odds=2.5)
print(f"Recommended bet: {kelly['recommended_bet_percentage']:.2f}%")
```

### 4. Run Examples / 运行示例

```bash
# Run all examples with visualizations
python examples.py
```

This will generate:
- Posterior distribution charts
- Session performance graphs
- Prediction distributions
- Kelly criterion optimization curves

### 5. Run Tests / 运行测试

```bash
# Run unit tests
python -m unittest test_analyzer -v
```

All 19 tests should pass ✓

### Key Features at a Glance

| Feature | Command | Output |
|---------|---------|--------|
| Basic Winrate | `cli.py analyze --wins 30 --losses 20` | Bayesian probability estimate |
| Future Prediction | `cli.py analyze --wins 30 --losses 20 --predict 10` | Expected wins in next N games |
| Kelly Criterion | `cli.py invest --wins 60 --losses 40 --odds 2.5` | Optimal bet size |
| Risk Assessment | `cli.py invest --wins 60 --losses 40 --odds 2.5 --bankroll 1000` | Risk of ruin analysis |
| Visualizations | Add `--visualize` to any command | Beautiful PNG charts |

### Understanding the Output

**Bayesian Winrate**: More accurate than simple winrate, accounts for uncertainty

**95% Credible Interval**: Range where the true winrate likely falls

**Kelly Criterion**: Optimal bet size to maximize long-term growth

**Risk of Ruin**: Probability of losing your entire bankroll

**Half Kelly**: Recommended conservative strategy (50% of optimal Kelly)

### Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Check out [examples.py](examples.py) for advanced usage
3. Explore the API in the `ore_analyzer/` directory
4. Visit [https://ore.supply/](https://ore.supply/) for the game

---

**Happy Analyzing! / 分析愉快！** 🎲📊
