const fs = require('fs').promises;

/**
 * ORE Supply获胜概率算法
 * 基于历史数据分析每个格子的获胜概率
 */
class WinProbabilityAnalyzer {
    constructor() {
        this.winners = [];
        this.probabilities = new Array(25).fill(0);
        this.baseWeight = 1.0;
        this.lastCalculationHash = null; // 缓存机制 // 基础权重
        this.decayFactors = {
            immediate: 0.05,    // 上一轮获胜格子权重（几乎为0）
            recent: 0.3,        // 最近2-3轮获胜格子权重
            medium: 0.6,        // 最近4-6轮获胜格子权重
            distant: 0.8        // 更早期获胜格子权重
        };
    }

    /**
     * 加载历史获胜数据
     */
    async loadWinnerHistory() {
        try {
            const data = await fs.readFile('winners.json', 'utf8');
            const jsonData = JSON.parse(data);
            this.winners = jsonData.winners || [];
            
            // 创建最近15轮获胜者排名数组
            if (this.winners.length > 0) {
                const sortedWinners = [...this.winners].sort((a, b) => b.round - a.round);
                this.winnerRanks = sortedWinners.slice(0, 15).map(w => w.blockNumber);
            } else {
                this.winnerRanks = [];
            }
        } catch (error) {
            this.winners = [];
            this.winnerRanks = [];
        }
    }

    /**
     * 计算每个格子的获胜概率 - 新算法
     */
    calculateProbabilities() {
        // 检查是否需要重新计算（缓存机制）
        const currentHash = JSON.stringify(this.winners.slice(0, 25).map(w => `${w.blockNumber}-${w.round}`));
        if (this.lastCalculationHash === currentHash && this.probabilities.some(p => p > 0)) {
            return; // 数据未变化，跳过计算
        }
        this.lastCalculationHash = currentHash;

        // 初始化所有格子为基础权重
        this.probabilities = new Array(25).fill(this.baseWeight);
        
        if (this.winners.length === 0) {
            // 没有历史数据时，所有格子等概率
            this.probabilities = this.probabilities.map(() => 1.0 / 25);
            return;
        }

        // 按轮次排序，最新的在前
        const sortedWinners = [...this.winners].sort((a, b) => b.round - a.round);

        // 分别统计最近15轮和25轮的数据
        const recent15Winners = sortedWinners.slice(0, 15);
        const recent25Winners = sortedWinners.slice(0, 25);
        
        // 统计频率
        const recent15Frequency = new Array(25).fill(0);
        const recent25Frequency = new Array(25).fill(0);
        
        recent15Winners.forEach((winner) => {
            const blockIndex = winner.blockNumber - 1; // Convert 1-based to 0-based
            if (blockIndex >= 0 && blockIndex < 25) {
                recent15Frequency[blockIndex]++;
            }
        });
        
        recent25Winners.forEach((winner) => {
            const blockIndex = winner.blockNumber - 1; // Convert 1-based to 0-based
            if (blockIndex >= 0 && blockIndex < 25) {
                recent25Frequency[blockIndex]++;
            }
        });

        // 重新设计：严格按照时间和频率逻辑
        for (let blockIndex = 0; blockIndex < 25; blockIndex++) {
            const count15 = recent15Frequency[blockIndex];
            const count25 = recent25Frequency[blockIndex];
            
            // 1. 最近25轮都没获胜 → 概率最高
            if (count25 === 0) {
                this.probabilities[blockIndex] = 1.0; // 最高概率
                continue;
            }
            
            // 2. 找到最近一次获胜的位置（recent25Winners数组索引，0是最新的）
            let mostRecentPosition = -1;
            for (let i = 0; i < recent25Winners.length; i++) {
                if (recent25Winners[i].blockNumber - 1 === blockIndex) {
                    mostRecentPosition = i; // 找到最小索引（最近的位置）
                    break;
                }
            }
            
            // 3. 根据最近获胜位置分配概率（位置越小=越近=概率越低）
            if (mostRecentPosition === 0) {
                // 上一轮获胜 - 最低概率
                this.probabilities[blockIndex] = 0.01;
            } else if (mostRecentPosition <= 2) {
                // 最近2-3轮获胜 - 很低概率，如果频繁获胜则更低
                this.probabilities[blockIndex] = count15 >= 2 ? 0.02 : 0.05;
            } else if (mostRecentPosition <= 5) {
                // 最近4-6轮获胜 - 低概率，如果频繁获胜则更低
                this.probabilities[blockIndex] = count15 >= 2 ? 0.03 : 0.15;
            } else if (mostRecentPosition <= 10) {
                // 最近7-11轮获胜 - 中等偏低概率
                this.probabilities[blockIndex] = count15 >= 2 ? 0.1 : 0.35;
            } else if (mostRecentPosition <= 15) {
                // 最近12-16轮获胜 - 中等概率
                this.probabilities[blockIndex] = count15 >= 2 ? 0.15 : 0.5;
            } else {
                // 17-25轮前获胜 - 较高概率
                this.probabilities[blockIndex] = count15 >= 2 ? 0.2 : 0.7;
            }
        }

        // 归一化概率（确保总和为1）
        const totalWeight = this.probabilities.reduce((sum, prob) => sum + prob, 0);
        if (totalWeight > 0) {
            this.probabilities = this.probabilities.map(prob => prob / totalWeight);
        }
    }

    /**
     * 获取概率颜色（ANSI颜色代码）
     */
    getProbabilityColor(probability) {
        const avgProb = 1.0 / 25; // 平均概率 4%
        
        // 根据概率高低决定颜色
        if (probability >= avgProb * 1.2) {
            return '\x1b[32m'; // 绿色 - 高概率 (>4.8%)
        } else if (probability >= avgProb * 0.8) {
            return '\x1b[33m'; // 黄色 - 中等概率 (3.2%-4.8%)
        } else if (probability >= avgProb * 0.3) {
            return '\x1b[31m'; // 红色 - 低概率 (1.2%-3.2%)
        } else {
            return '\x1b[91m'; // 亮红色 - 极低概率 (<1.2%)
        }
    }

    /**
     * 重置颜色
     */
    getResetColor() {
        return '\x1b[0m';
    }

    /**
     * 获取最近获胜者排名 (返回最近15轮的所有排名，支持重复)
     */
    getRecentWinnerRank(blockNumber) {
        if (this.winners.length === 0) return null;
        
        // 按轮次排序，最新的在前
        const sortedWinners = [...this.winners].sort((a, b) => b.round - a.round);

        // 查找块号在最近15个获胜者中的所有位置
        const ranks = [];
        for (let i = 0; i < Math.min(15, sortedWinners.length); i++) {
            if (sortedWinners[i].blockNumber === blockNumber) {
                ranks.push(-(i + 1)); // 添加排名 -1, -2, -3, ..., -15
            }
        }
        
        return ranks.length > 0 ? ranks : null;
    }

    /**
     * 获取最近获胜者标记的颜色 (处理排名数组)
     */
    getWinnerRankColor(ranks) {
        if (!ranks || ranks.length === 0) return '\x1b[37m'; // 白色 - 无排名
        
        const firstRank = ranks[0]; // 使用最近的排名决定颜色
        if (firstRank === -1) return '\x1b[31m'; // 红色 - 最近获胜者
        if (firstRank >= -5) return '\x1b[33m'; // 黄色 - 最近5个获胜者
        if (firstRank >= -10) return '\x1b[36m'; // 青色 - 最近10个获胜者
        if (firstRank >= -15) return '\x1b[35m'; // 紫色 - 最近15个获胜者
        return '\x1b[37m'; // 白色 - 其他
    }

    /**
     * 获取格子分析详情
     */
    getBlockAnalysis(blockNumber) {
        if (this.winners.length === 0) return null;
        
        const sortedWinners = [...this.winners].sort((a, b) => b.round - a.round);
        const recent25Winners = sortedWinners.slice(0, 25);
        
        const blockIndex = blockNumber - 1;
        const winCount = recent25Winners.filter(w => w.blockNumber === blockNumber).length;
        const winPositions = recent25Winners
            .map((w, i) => w.blockNumber === blockNumber ? i : -1)
            .filter(pos => pos >= 0);
        
        const lastWinRound = winPositions.length > 0 ? winPositions[0] : -1;
        const neverWon = winCount === 0;
        const isRepeater = winCount > 1;
        const recentRepeater = lastWinRound === 0 && winPositions.length > 1;
        
        return {
            winCount,
            winPositions,
            lastWinRound,
            neverWon,
            isRepeater,
            recentRepeater,
            roundsSinceWin: lastWinRound >= 0 ? lastWinRound : 25
        };
    }

    /**
     * 格式化概率显示
     */
    formatProbability(probability) {
        const percentage = (probability * 100).toFixed(1);
        return `${percentage}%`;
    }

    /**
     * 显示概率分析结果
     */
    displayProbabilities() {
        console.log('\n🎲 获胜概率分析 (基于历史数据)');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        
        // 显示颜色说明
        console.log('📈 概率说明:');
        console.log(`   ${this.getProbabilityColor(0.08)}■${this.getResetColor()} 绿色: 高概率 (>4.8%)`);
        console.log(`   ${this.getProbabilityColor(0.04)}■${this.getResetColor()} 黄色: 中等概率 (3.2%-4.8%)`);
        console.log(`   ${this.getProbabilityColor(0.02)}■${this.getResetColor()} 红色: 低概率 (1.2%-3.2%)`);
        console.log(`   ${this.getProbabilityColor(0.01)}■${this.getResetColor()} 亮红色: 极低概率 (<1.2%)`);
        console.log('');

        // 显示5x5网格
        for (let row = 0; row < 5; row++) {
            let line = '';
            for (let col = 0; col < 5; col++) {
                const index = row * 5 + col;
                const blockNumber = index + 1;
                const probability = this.probabilities[index];
                const color = this.getProbabilityColor(probability);
                const reset = this.getResetColor();
                const probText = this.formatProbability(probability);
                
                line += `${color}#${blockNumber.toString().padStart(2, '0')} ${probText.padEnd(5)}${reset} `;
            }
            console.log(line);
        }

        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        
        // 显示统计信息
        const maxProb = Math.max(...this.probabilities);
        const minProb = Math.min(...this.probabilities);
        const maxIndex = this.probabilities.indexOf(maxProb);
        const minIndex = this.probabilities.indexOf(minProb);
        
        console.log(`🎯 最高概率: ${this.getProbabilityColor(maxProb)}#${maxIndex + 1} (${this.formatProbability(maxProb)})${this.getResetColor()}`);
        console.log(`⚠️  最低概率: ${this.getProbabilityColor(minProb)}#${minIndex + 1} (${this.formatProbability(minProb)})${this.getResetColor()}`);
        
        if (this.winners.length > 0) {
            const lastWinner = this.winners[this.winners.length - 1];
            console.log(`📜 上轮获胜: #${lastWinner.blockNumber} (Round #${lastWinner.round.toLocaleString()})`);
        }
        
        console.log(`📊 基于 ${this.winners.length} 条历史记录的分析`);
    }

    /**
     * 获取推荐投注格子
     */
    getRecommendations(topN = 5) {
        const indexed = this.probabilities.map((prob, index) => ({
            blockNumber: index + 1,
            probability: prob,
            index: index
        }));

        // 按概率排序
        indexed.sort((a, b) => b.probability - a.probability);

        console.log(`\n🎯 推荐投注格子 (Top ${topN}):`);
        for (let i = 0; i < Math.min(topN, indexed.length); i++) {
            const item = indexed[i];
            const color = this.getProbabilityColor(item.probability);
            const reset = this.getResetColor();
            console.log(`   ${i + 1}. ${color}#${item.blockNumber} - ${this.formatProbability(item.probability)}${reset}`);
        }

        return indexed.slice(0, topN);
    }

    /**
     * 主要分析函数
     */
    async analyze() {
        console.log('🔮 ORE Supply 获胜概率分析器');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        
        await this.loadWinnerHistory();
        this.calculateProbabilities();
        this.displayProbabilities();
        this.getRecommendations();
        
        console.log('\n💡 提示: 这是基于历史数据的概率分析，不保证准确性，请谨慎投注！');
    }
}

// 如果直接运行此文件
if (require.main === module) {
    const analyzer = new WinProbabilityAnalyzer();
    analyzer.analyze().catch(console.error);
}

module.exports = WinProbabilityAnalyzer;