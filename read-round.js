// Read and print per-square deployed SOL and participant counts for current or given round
// Usage:
//   RPC_URL=https://api.mainnet-beta.solana.com node read-round.js [--round <id>]

const { Connection, PublicKey } = require('@solana/web3.js');

const PROGRAM_ID = new PublicKey('oreV3EG1i9BEgiAJ8b177Z2S2rMarzak4NMv1kULvWv');
const SEED_BOARD = Buffer.from('board');
const SEED_ROUND = Buffer.from('round');

const RPC_URL = process.env.RPC_URL || 'https://mainnet.helius-rpc.com/?api-key=17bc7417-7eb1-41b6-be51-9';

function getArg(name, def = undefined) {
  const i = process.argv.indexOf(name);
  if (i >= 0 && i + 1 < process.argv.length) return process.argv[i + 1];
  return def;
}

function le64(buf, offset) {
  // returns BigInt
  const view = new DataView(buf.buffer, buf.byteOffset, buf.byteLength);
  return view.getBigUint64(offset, true);
}

function decodeBoard(accData) {
  if (!accData || accData.length < 8 + 24) throw new Error('Board data too short');
  const data = accData.subarray(8); // skip 8-byte discriminator
  const round_id = le64(data, 0);
  const start_slot = le64(data, 8);
  const end_slot = le64(data, 16);
  return { round_id, start_slot, end_slot };
}

function decodeRound(accData) {
  if (!accData || accData.length < 8) throw new Error('Round data too short');
  const data = accData.subarray(8); // skip 8-byte discriminator
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
  return {
    id, deployed, slot_hash: Buffer.from(slot_hash), count, expires_at, motherlode,
    rent_payer, top_miner, top_miner_reward, total_deployed, total_vaulted, total_winnings,
  };
}

function u64leBytesFromBigInt(x) {
  const b = Buffer.alloc(8);
  b.writeBigUInt64LE(BigInt(x));
  return b;
}

async function findBoardPda() {
  const [pk] = PublicKey.findProgramAddressSync([SEED_BOARD], PROGRAM_ID);
  return pk;
}

async function findRoundPda(roundIdBigInt) {
  const [pk] = PublicKey.findProgramAddressSync([SEED_ROUND, u64leBytesFromBigInt(roundIdBigInt)], PROGRAM_ID);
  return pk;
}

function formatLamports(bi) {
  // returns string SOL with 9 decimals
  const LAMPORTS_PER_SOL = 1_000_000_000n;
  const whole = bi / LAMPORTS_PER_SOL;
  const frac = (bi % LAMPORTS_PER_SOL).toString().padStart(9, '0');
  return `${whole}.${frac}`;
}

function isAll(buf, value) {
  for (let i = 0; i < buf.length; i++) if (buf[i] !== value) return false;
  return true;
}

function winningSquareFromSlotHash(slotHashBuf) {
  if (!slotHashBuf || slotHashBuf.length !== 32) return { status: 'unavailable' };
  if (isAll(slotHashBuf, 0x00)) return { status: 'unavailable' };
  if (isAll(slotHashBuf, 0xff)) return { status: 'refund' };
  const v = new DataView(slotHashBuf.buffer, slotHashBuf.byteOffset, slotHashBuf.byteLength);
  const r1 = v.getBigUint64(0, true);
  const r2 = v.getBigUint64(8, true);
  const r3 = v.getBigUint64(16, true);
  const r4 = v.getBigUint64(24, true);
  const r = r1 ^ r2 ^ r3 ^ r4;
  const idx = Number(r % 25n);
  return { status: 'ok', index: idx };
}

(async () => {
  const connection = new Connection(RPC_URL, 'confirmed');
  const roundArg = getArg('--round', null);
  const recentArg = getArg('--recent', null);
  let roundId;

  // Always fetch board for countdowns
  const boardPda = await findBoardPda();
  const boardAcc = await connection.getAccountInfo(boardPda);
  if (!boardAcc) throw new Error(`Board account not found at ${boardPda.toBase58()}`);
  const board = decodeBoard(boardAcc.data);

  if (roundArg !== null) {
    roundId = BigInt(roundArg);
  } else {
    roundId = board.round_id;
    console.log(`Current round id: ${roundId.toString()}`);
  }

  if (recentArg !== null) {
    const want = Math.max(0, parseInt(recentArg, 10) || 0);
    if (want <= 0) throw new Error('--recent must be a positive integer');
    const results = [];
    // Last completed round is always current board.round_id - 1
    let cur = roundId > 0n ? roundId - 1n : 0n;
    while (results.length < want && cur >= 0n) {
      const pda = await findRoundPda(cur);
      const acc = await connection.getAccountInfo(pda);
      if (!acc) break;
      const r = decodeRound(acc.data);
      const w = winningSquareFromSlotHash(r.slot_hash);
      if (w.status === 'ok') {
        results.push({ id: r.id.toString(), square: w.index });
      } else {
        results.push({ id: r.id.toString(), square: null, status: w.status });
      }
      if (cur === 0n) break;
      cur -= 1n;
    }
    console.log(`Recent ${results.length} rounds winners (latest first):`);
    for (const item of results) {
      if (item.square !== null) {
        console.log(`  round ${item.id}: square ${item.square}`);
      } else {
        console.log(`  round ${item.id}: ${item.status}`);
      }
    }
    return;
  }

  const roundPda = await findRoundPda(roundId);
  const roundAcc = await connection.getAccountInfo(roundPda);
  if (!roundAcc) throw new Error(`Round account not found at ${roundPda.toBase58()} (id=${roundId.toString()})`);
  const round = decodeRound(roundAcc.data);

  console.log(`Round PDA: ${roundPda.toBase58()}`);
  console.log(`Round id: ${round.id.toString()}`);
  console.log(`Total deployed (SOL): ${formatLamports(round.total_deployed)}`);
  // Countdown: time until current round end (mining window)
  const U64_MAX = (1n << 64n) - 1n;
  try {
    const currentSlot = BigInt(await connection.getSlot('confirmed'));
    if (board.end_slot !== U64_MAX) {
      const remain = board.end_slot > currentSlot ? (board.end_slot - currentSlot) : 0n;
      const mins = remain / 150n; // 150 slots per minute
      const secs = ((remain % 150n) * 60n) / 150n;
      console.log(`Time to round end: ${mins.toString()}m ${secs.toString()}s (slots ${remain.toString()})`);
    } else {
      console.log('Time to round end: not started (waiting for first deploy)');
    }

    // Also show checkpoint deadline for last completed round
    if (round.id > 0n) {
      const prevId = round.id - 1n;
      const prevPda = await findRoundPda(prevId);
      const prevAcc = await connection.getAccountInfo(prevPda);
      if (prevAcc) {
        const prev = decodeRound(prevAcc.data);
        if (prev.expires_at !== U64_MAX) {
          const remainCk = prev.expires_at > currentSlot ? (prev.expires_at - currentSlot) : 0n;
          const minsCk = remainCk / 150n;
          const secsCk = ((remainCk % 150n) * 60n) / 150n;
          console.log(`Time to checkpoint expiry (last completed): ${minsCk.toString()}m ${secsCk.toString()}s (slots ${remainCk.toString()})`);
        }
      }
    }
  } catch {}

  const w = winningSquareFromSlotHash(round.slot_hash);
  if (w.status === 'ok') {
    console.log(`Winning square (this round): ${w.index}`);
  } else if (w.status === 'refund') {
    console.log('Winning square (this round): refund round (slot hash unavailable)');
  } else {
    console.log('Winning square (this round): unavailable (current round not reset yet)');
    // Try previous (last completed) round for the winner
    if (round.id > 0n) {
      const prevId = round.id - 1n;
      try {
        const prevPda = await findRoundPda(prevId);
        const prevAcc = await connection.getAccountInfo(prevPda);
        if (prevAcc) {
          const prev = decodeRound(prevAcc.data);
          const pw = winningSquareFromSlotHash(prev.slot_hash);
          if (pw.status === 'ok') {
            console.log(`Last completed round id: ${prev.id.toString()}`);
            console.log(`Winning square (last completed): ${pw.index}`);
          }
        }
      } catch {}
    }
  }
  console.log('Per-square deployed (SOL) and count:');
  for (let i = 0; i < 25; i++) {
    const sol = formatLamports(round.deployed[i]);
    const cnt = round.count[i].toString();
    console.log(`  [${i}] deployed=${sol}  count=${cnt}`);
  }
})().catch((e) => {
  console.error(e);
  process.exit(1);
});

