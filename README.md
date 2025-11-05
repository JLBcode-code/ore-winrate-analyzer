<<<<<<< HEAD
# ORE Supply Game Win Rate Analyzer

📞 **Contact the Author:**
- Telegram: [https://t.me/Block_devp](https://t.me/Block_devp)
- X (Twitter): [https://x.com/OSDCoin](https://x.com/OSDCoin)

---

## Overview

The ORE Supply Game Win Rate Analyzer is a sophisticated tool designed to analyze the Solana-based ORE Supply Game, providing data-driven insights and probability calculations to help players make informed betting decisions. This analyzer uses advanced algorithms including Bayesian inference, time-decay models, and historical pattern analysis to predict winning probabilities for each of the 25 game blocks.

![ORE Supply Game Analysis Interface](https://raw.githubusercontent.com/JLBcode-code/ore-winrate-analyzer/main/images/ore-analysis-interface.png)

## Features

### 🎯 Core Analytics
- **Real-time Game Monitoring**: Continuously monitors the ORE Supply Game state on Solana mainnet
- **Probability Analysis**: Calculates win probabilities for all 25 blocks using historical data
- **Smart Pick Recommendations**: Provides top 3 recommended blocks based on Bayesian analysis
- **Advanced Pattern Recognition**: Identifies trends and patterns in winning sequences

### 📊 Analysis Methods
1. **Bayesian Time-Decay Model**: Uses Dirichlet-multinomial posterior with exponential time decay
2. **Anti-Streak Analysis**: Applies penalties to recently winning blocks to diversify recommendations
3. **Pool Efficiency Calculator**: Analyzes risk-reward ratios for optimal betting strategies
4. **Historical Pattern Analysis**: Leverages 15-25 rounds of historical data for predictions

### 🔍 Key Metrics
- **Round Information**: Current round number and block details
- **Participant Data**: Number of participants and SOL amounts for each block
- **Win Probabilities**: Calculated probabilities for each of the 25 blocks
- **Risk Assessment**: Multi-level risk analysis (Low/Medium/High)
- **Efficiency Ratings**: Investment efficiency scores for each block

## Installation

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn package manager

### Setup
1. Clone the repository:
```bash
git clone <repository-url>
cd ore-winrate
```

2. Install dependencies:
```bash
npm install
```

3. Configure RPC endpoint (optional):
```bash
# Set custom RPC URL as environment variable
export RPC_URL="your-solana-rpc-endpoint"
```

## Usage

### Basic Commands

#### Run Probability Analysis
```bash
npm run analyze
# or
node probability-analyzer.js
```

#### Run Probability Analysis
```bash
npm run analyze
# or
node probability-analyzer.js
```

#### Read Current Round Data
```bash
npm run read-round
# or
node read-round.js
```

### Advanced Usage

#### Generate Smart Picks
```bash
node smart-picks.js
```

#### Run Advanced Analysis
```bash
node advanced-analyzer.js
```

#### Clean and Optimize Data
```bash
node cleanup-v2.js
```

## Understanding the Output

### Analysis Interface Elements

![Game Analysis Screenshot](https://raw.githubusercontent.com/JLBcode-code/ore-winrate-analyzer/main/images/ore-analysis-interface.png)

The analysis interface displays:

1. **Header Information**:
   - Current round number (e.g., round=43498)
   - Analysis status and winner count
   - Timestamp and processing statistics

2. **Block Grid (5x5)**:
   - Block numbers (#01-#25)
   - Participant counts (e.g., 51, 172, 92)
   - SOL amounts invested (e.g., 0.053SOL, 0.439SOL)
   - Win probability percentages (color-coded)

3. **Probability Color Coding**:
   - 🟢 **High Probability** (6.4%+): Best betting opportunities
   - 🟡 **Medium Probability** (4.0-6.3%): Moderate opportunities
   - 🟠 **Low Probability** (2.0-3.9%): Higher risk bets
   - 🔴 **Very Low Probability** (<2.0%): Avoid these blocks

4. **Recommended Picks**:
   - Displays top recommended blocks with reasoning
   - Shows specific probabilities and risk assessments

## File Structure

```
ore-winrate/
├── api-scraper.js          # Main analyzer and real-time monitor
├── probability-analyzer.js  # Core probability calculation engine
├── advanced-analyzer.js    # Advanced pattern analysis
├── smart-picks.js          # Bayesian recommendation system
├── read-round.js           # Round data reader
├── cleanup-v2.js           # Data cleaning utilities
├── ev-picks.js             # Expected value calculations
├── winners.json            # Historical winner data
├── package.json            # Project configuration
└── ore/                    # Solana program integration
    ├── api/                # API interface
    ├── cli/                # Command line tools
    └── program/            # Solana program code
```

## Algorithm Details

### 1. Bayesian Time-Decay Model
- Uses uniform Dirichlet prior (α = 1.0 per square)
- Applies exponential time decay with 10-round half-life
- Analyzes last 30 rounds of historical data
- Posterior probability: `p_k = (α + w_k) / (N*α + Σw)`

### 2. Anti-Streak Penalty System
- Recent winner: ×0.6 probability multiplier
- Previous round winner: ×0.8 probability multiplier
- Encourages diversification in betting strategy

### 3. Pool Efficiency Analysis
- Calculates investment efficiency ratios
- Considers participant count and SOL amounts
- Provides risk-adjusted recommendations

### 4. Pattern Recognition
- Identifies hot and cold streaks
- Analyzes temporal patterns in wins
- Adjusts probabilities based on recent trends

## Configuration

### Environment Variables
- `RPC_URL`: Custom Solana RPC endpoint (default: Helius mainnet)
- `PROGRAM_ID`: ORE program ID on Solana

### Analysis Parameters
- `BLOCKS_TO_ANALYZE`: Number of blocks in analysis (default: 25)
- `HISTORICAL_ROUNDS`: Rounds of historical data to consider (default: 30)
- `TIME_DECAY_HALF_LIFE`: Half-life for time decay (default: 10 rounds)

## API Integration

The analyzer integrates with the Solana blockchain to fetch real-time data:

- **Program ID**: `oreV3EG1i9BEgiAJ8b177Z2S2rMarzak4NMv1kULvWv`
- **Network**: Solana Mainnet
- **Data Sources**: On-chain program accounts and historical transactions

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and analytical purposes only. Gambling involves risk, and past performance does not guarantee future results. Always gamble responsibly and never bet more than you can afford to lose.

## Support

For technical support or questions:
- Telegram: [https://t.me/Block_devp](https://t.me/Block_devp)
- X: [https://x.com/OSDCoin](https://x.com/OSDCoin)

---

**Happy Analyzing! 🎯📊**
