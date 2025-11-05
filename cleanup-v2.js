#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🧹 清理不必要的文件和依赖...\n');

// 需要删除的文件列表
const filesToDelete = [
  'cleanup.js',  // 旧的清理脚本
  'scraper.js'   // 旧的浏览器版本
];

// 删除文件
filesToDelete.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    try {
      fs.unlinkSync(filePath);
      console.log(`✅ 已删除: ${file}`);
    } catch (error) {
      console.log(`❌ 删除失败: ${file} - ${error.message}`);
    }
  } else {
    console.log(`⏩ 文件不存在: ${file}`);
  }
});

console.log('\n🎉 清理完成！');
console.log('\n📋 当前项目结构:');
console.log('  api-scraper.js          - 🆕 主程序 (API版本)');
console.log('  read-round.js           - 📡 区块链数据读取工具');
console.log('  probability-analyzer.js - 📊 概率分析引擎');
console.log('  advanced-analyzer.js    - 🧠 高级策略分析器');
console.log('  package.json            - 📦 项目配置 (已更新)');
console.log('  README-API-v2.md        - 📖 使用说明');
console.log('  winners.json            - 💾 历史数据存储');

console.log('\n🚀 使用方法:');
console.log('  npm start               - 启动API分析器');
console.log('  node read-round.js      - 查看当前轮次数据');
console.log('  node read-round.js --recent 10  - 查看最近10轮获胜记录');

console.log('\n✅ 项目已升级到API版本 2.0！');