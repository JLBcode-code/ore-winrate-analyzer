// Smart pick recommendations from winners.json using a Bayesian, time-decayed model
// - Uses Dirichlet-multinomial posterior with uniform prior (alpha = 1 per square)
// - Exponential time decay on last 30 rounds (half-life = 10 rounds)
// - Light anti-streak penalty for very recent repeats (last 1-2 rounds)
// Outputs top 3 squares with 1-based indexing

const fs = require('fs');

function loadWinners(path = 'winners.json') {
  const raw = fs.readFileSync(path, 'utf8');
  const arr = JSON.parse(raw);
  return arr;
}

function dirichletTimeDecayedPriors(winners, options = {}) {
  const N = 25; // 5x5 grid
  const alpha = options.alpha ?? 1.0; // prior per square
  const halfLife = options.halfLife ?? 10; // rounds
  const maxRounds = options.maxRounds ?? 30;

  const sorted = [...winners].sort((a, b) => b.round - a.round).slice(0, maxRounds);
  const weights = sorted.map((_, i) => Math.pow(2, -i / halfLife)); // exp decay base-2

  const counts = new Array(N).fill(0);
  for (let i = 0; i < sorted.length; i++) {
    const idx0 = sorted[i].blockNumber; // 0-based in file
    if (Number.isInteger(idx0) && idx0 >= 0 && idx0 < N) counts[idx0] += weights[i];
  }

  // Posterior mean p_k = (alpha + w_k) / (N*alpha + sum_w)
  const sumW = counts.reduce((s, x) => s + x, 0);
  let probs = counts.map((w) => (alpha + w) / (N * alpha + sumW));

  // Anti-streak penalty for very recent repeats (light touch)
  // If a square won last round: x0.6; if won in round-1: x0.8
  // Keeps recommendations diversified, though RNG is uniform in theory
  const recentIdx0 = sorted[0]?.blockNumber;
  const prevIdx0 = sorted[1]?.blockNumber;
  if (Number.isInteger(recentIdx0)) probs[recentIdx0] *= 0.6;
  if (Number.isInteger(prevIdx0)) probs[prevIdx0] *= 0.8;

  // Renormalize after penalties
  const s = probs.reduce((a, b) => a + b, 0);
  probs = probs.map((p) => (s > 0 ? p / s : 1 / N));

  return probs;
}

function topN(probs, n = 3) {
  const arr = probs.map((p, i) => ({ index0: i, index1: i + 1, p }));
  arr.sort((a, b) => b.p - a.p);
  return arr.slice(0, n);
}

function fmtPct(p) { return (p * 100).toFixed(2) + '%'; }

function main() {
  const winners = loadWinners();
  if (!Array.isArray(winners) || winners.length === 0) {
    console.log('No winners data found.');
    process.exit(0);
  }
  const probs = dirichletTimeDecayedPriors(winners, { alpha: 1.0, halfLife: 10, maxRounds: 30 });
  const picks = topN(probs, 3);
  console.log('Top 3 smart picks (1-based):');
  for (let i = 0; i < picks.length; i++) {
    console.log(`  ${i + 1}. #${picks[i].index1}  (${fmtPct(picks[i].p)})`);
  }
}

if (require.main === module) main();

module.exports = { dirichletTimeDecayedPriors, topN };

