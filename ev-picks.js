// Expected value (EV) top-3 picker using on-chain per-square deployed amounts
// Model (single-square selection):
//   S_win_i ≈ 0.99*a + 0.891 * ( (Total+a) - (Deployed[i]+a) ) * ( a / (Deployed[i]+a) )
//   EV_i = -a + S_win_i / 25
// where 0.99 accounts for 1% admin on winners' own principal, and 0.891 = 0.99 * 0.90
// Outputs top-3 squares (1-based indices) by EV for a given bet size.

const { Connection, PublicKey } = require('@solana/web3.js');

const PROGRAM_ID = new PublicKey('oreV3EG1i9BEgiAJ8b177Z2S2rMarzak4NMv1kULvWv');
const SEED_BOARD = Buffer.from('board');
const SEED_ROUND = Buffer.from('round');
const RPC_URL = process.env.RPC_URL || 'https://api.mainnet-beta.solana.com';

function getArg(name, def = undefined) {
  const i = process.argv.indexOf(name);
  if (i >= 0 && i + 1 < process.argv.length) return process.argv[i + 1];
  return def;
}

function le64(buf, offset) {
  const view = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  return view.getBigUint64(offset, true);
}

function decodeBoard(accData) {
  const data = accData.subarray(8);
  return { round_id: le64(data, 0), start_slot: le64(data, 8), end_slot: le64(data, 16) };
}

function decodeRound(accData) {
  const data = accData.subarray(8);
  let o = 0;
  const id = le64(data, o); o += 8;
  const deployed = [];
  for (let i = 0; i < 25; i++) { deployed.push(le64(data, o)); o += 8; }
  const slot_hash = data.subarray(o, o + 32); o += 32;
  const count = [];
  for (let i = 0; i < 25; i++) { count.push(le64(data, o)); o += 8; }
  const expires_at = le64(data, o); o += 8;
  const motherlode = le64(data, o); o += 8;
  const rent_payer = new PublicKey(data.subarray(o, o + 32)); o += 32;
  const top_miner = new PublicKey(data.subarray(o, o + 32)); o += 32;
  const top_miner_reward = le64(data, o); o += 8;
  const total_deployed = le64(data, o); o += 8;
  const total_vaulted = le64(data, o); o += 8;
  const total_winnings = le64(data, o); o += 8;
  return { id, deployed, count, total_deployed };
}

function solToLamports(sol) { return BigInt(Math.round(Number(sol) * 1e9)); }
function lamportsToSol(lam) { return Number(lam) / 1e9; }

function evForSquare(deployed, total, aLamports) {
  const N = 25n;
  const a = BigInt(aLamports);
  const totalNew = total + a;
  const depNew = deployed + a;
  // S_win ≈ 0.99*a + 0.891 * ( (totalNew - depNew) * (a / depNew) )
  const base = a * 99n / 100n; // 0.99*a (integer approx)
  // 0.891 factor as rational: 0.99 * 0.9 = 99/100 * 9/10 = 891/1000
  const pot = totalNew - depNew;
  // Compute share term in BigInt with scaling of 1000 for 0.891
  const shareNumer = pot * a * 891n;
  const share = shareNumer / (depNew * 1000n);
  const S_win = base + share;
  // EV = -a + S_win / 25
  const EV = (-a) + (S_win / N);
  return { S_win, EV };
}

async function main() {
  const betArg = getArg('--bet', '0.1'); // in SOL
  const betLamports = solToLamports(parseFloat(betArg));
  const connection = new Connection(RPC_URL, 'confirmed');

  const [boardPda] = PublicKey.findProgramAddressSync([SEED_BOARD], PROGRAM_ID);
  const boardAcc = await connection.getAccountInfo(boardPda);
  if (!boardAcc) throw new Error('Board not found');
  const board = decodeBoard(boardAcc.data);

  const [roundPda] = PublicKey.findProgramAddressSync([SEED_ROUND, (() => { const b = Buffer.alloc(8); b.writeBigUInt64LE(board.round_id); return b; })()], PROGRAM_ID);
  const roundAcc = await connection.getAccountInfo(roundPda);
  if (!roundAcc) throw new Error('Round not found');
  const round = decodeRound(roundAcc.data);

  const results = [];
  for (let i = 0; i < 25; i++) {
    const { EV } = evForSquare(round.deployed[i], round.total_deployed, betLamports);
    results.push({ idx0: i, idx1: i + 1, EV });
  }
  results.sort((a, b) => (Number(b.EV - a.EV)));

  console.log(`EV Top 3 (bet ${betArg} SOL each, 1-based):`);
  for (let i = 0; i < 3; i++) {
    const r = results[i];
    const evSol = lamportsToSol(r.EV);
    console.log(`  ${i + 1}. #${r.idx1}  EV=${evSol.toFixed(6)} SOL`);
  }
}

if (require.main === module) {
  main().catch((e) => { console.error(e); process.exit(1); });
}

module.exports = { evForSquare };

