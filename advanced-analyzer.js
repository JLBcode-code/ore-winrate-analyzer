const WinProbabilityAnalyzer = require('./probability-analyzer');

/**
 * 高级胜率分析器 - 基于智能合约机制优化
 */
class AdvancedWinAnalyzer extends WinProbabilityAnalyzer {
    constructor() {
        super();
        this.participantThreshold = 100; // 参与人数阈值
        this.amountThreshold = 0.25; // SOL投入阈值
    }

    /**
     * 资金池效率分析 - 寻找投入少但奖励高的格子
     */
    calculatePoolEfficiency(blocks) {
        const efficiency = [];
        
        for (let i = 0; i < 25; i++) {
            const block = blocks[i];
            if (!block) continue;
            
            // 计算投入产出比
            const participants = block.participants || 100;
            const amount = block.amount || 0.04;
            
            // 效率 = 预期奖励 / 投入成本
            // 预期奖励 = (其他24格总投入) / 参与人数
            const expectedOtherInvestment = participants * amount * 24; // 假设其他格子类似
            const expectedReward = expectedOtherInvestment / participants;
            const efficiency_ratio = expectedReward / amount;
            
            efficiency[i] = {
                blockNumber: i + 1,
                participants,
                amount,
                efficiency: efficiency_ratio,
                expectedReward,
                riskLevel: this.calculateRiskLevel(i + 1, participants, amount)
            };
        }
        
        return efficiency.sort((a, b) => b.efficiency - a.efficiency);
    }

    /**
     * 风险等级评估
     */
    calculateRiskLevel(blockNumber, participants, amount) {
        const winnerRanks = this.getRecentWinnerRank(blockNumber);
        
        let risk = 'LOW';
        
        // 最近获胜过的格子风险极高
        if (winnerRanks && winnerRanks.includes(-1)) risk = 'EXTREME';
        else if (winnerRanks && winnerRanks.some(r => r >= -3)) risk = 'HIGH';
        else if (participants > this.participantThreshold) risk = 'MEDIUM';
        else if (amount > this.amountThreshold) risk = 'MEDIUM';
        
        return risk;
    }

    /**
     * 智能投注建议
     */
    getSmartBettingAdvice(blocks) {
        const efficiency = this.calculatePoolEfficiency(blocks);
        const recommendations = [];
        
        // 策略1: 寻找高效率低风险格子
        const safeBets = efficiency.filter(e => 
            e.riskLevel === 'LOW' && 
            e.efficiency > 1.2 && 
            e.participants < this.participantThreshold
        ).slice(0, 3);
        
        // 策略2: 从未获胜的格子（奖励机制中的bonus）
        const neverWonBlocks = [];
        for (let i = 1; i <= 25; i++) {
            const ranks = this.getRecentWinnerRank(i);
            if (!ranks) {
                const blockEfficiency = efficiency.find(e => e.blockNumber === i);
                if (blockEfficiency) neverWonBlocks.push(blockEfficiency);
            }
        }
        
        // 策略3: 反向投资（投注人数最少的格子）
        const lowParticipation = efficiency
            .filter(e => e.riskLevel !== 'EXTREME')
            .sort((a, b) => a.participants - b.participants)
            .slice(0, 2);

        return {
            primary: safeBets,
            neverWon: neverWonBlocks.slice(0, 2),
            contrarian: lowParticipation,
            analysis: {
                avgEfficiency: efficiency.reduce((sum, e) => sum + e.efficiency, 0) / efficiency.length,
                bestEfficiency: efficiency[0],
                totalParticipants: efficiency.reduce((sum, e) => sum + e.participants, 0)
            }
        };
    }

    /**
     * 动态资金分配策略
     */
    calculateOptimalAllocation(totalBudget, recommendations) {
        const allocation = [];
        let remaining = totalBudget;
        
        // 60% 分配给主要推荐
        const primaryBudget = totalBudget * 0.6;
        if (recommendations.primary.length > 0) {
            const perPrimary = primaryBudget / recommendations.primary.length;
            recommendations.primary.forEach(rec => {
                allocation.push({
                    blockNumber: rec.blockNumber,
                    amount: perPrimary,
                    reason: `高效率低风险 (效率: ${rec.efficiency.toFixed(2)})`
                });
            });
            remaining -= primaryBudget;
        }
        
        // 25% 分配给从未获胜格子
        const neverWonBudget = totalBudget * 0.25;
        if (recommendations.neverWon.length > 0) {
            const perNeverWon = neverWonBudget / recommendations.neverWon.length;
            recommendations.neverWon.forEach(rec => {
                allocation.push({
                    blockNumber: rec.blockNumber,
                    amount: perNeverWon,
                    reason: `从未获胜奖励 (效率: ${rec.efficiency.toFixed(2)})`
                });
            });
            remaining -= neverWonBudget;
        }
        
        // 15% 分配给反向策略
        if (recommendations.contrarian.length > 0 && remaining > 0) {
            const perContrarian = remaining / recommendations.contrarian.length;
            recommendations.contrarian.forEach(rec => {
                allocation.push({
                    blockNumber: rec.blockNumber,
                    amount: perContrarian,
                    reason: `反向投资 (人数: ${rec.participants})`
                });
            });
        }
        
        return allocation;
    }

    /**
     * 显示高级分析结果
     */
    displayAdvancedAnalysis(blocks, totalBudget = 1.0) {
        console.log('\n🧠 ORE Supply 高级胜率分析');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        
        const advice = this.getSmartBettingAdvice(blocks);
        const allocation = this.calculateOptimalAllocation(totalBudget, advice);
        
        console.log('\n💡 智能投注建议:');
        console.log(`📊 市场分析: 平均效率 ${advice.analysis.avgEfficiency.toFixed(2)}, 总参与人数 ${advice.analysis.totalParticipants}`);
        console.log(`🏆 最佳效率: 块 #${advice.analysis.bestEfficiency.blockNumber} (${advice.analysis.bestEfficiency.efficiency.toFixed(2)})`);
        
        console.log('\n🎯 推荐投注分配:');
        allocation.forEach((alloc, index) => {
            const percentage = (alloc.amount / totalBudget * 100).toFixed(1);
            console.log(`${index + 1}. 块 #${alloc.blockNumber.toString().padStart(2)} - ${alloc.amount.toFixed(4)} SOL (${percentage}%) - ${alloc.reason}`);
        });
        
        console.log('\n⚠️  风险提示:');
        console.log('- 基于历史数据和智能合约分析');
        console.log('- 真随机数无法预测，仅提供概率优化');
        console.log('- 建议小额测试，逐步调整策略');
        
        return allocation;
    }
}

module.exports = AdvancedWinAnalyzer;