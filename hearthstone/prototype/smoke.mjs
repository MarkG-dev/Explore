#!/usr/bin/env node
/**
 * Reference driver for the PARRY engine — correct API usage, plus the three
 * measurements that decide whether the design works.
 *
 * Written because the API is easy to misuse. Three wrong guesses while verifying
 * this engine, each of which *looked* like an engine bug and was not:
 *
 *   buildDeck(cards, 'A')          -> the 2nd arg is `copies`, not a deck name.
 *                                     'A' fails `i < copies`, so you silently get
 *                                     an empty deck and every game ends in fatigue.
 *   createGame(seed, dA, dB)       -> takes ONE options object:
 *                                     createGame({ seed, decks: { A, B }, cards })
 *   validateDeck(deck)             -> needs the card registry as a 2nd arg, or it
 *                                     reports every card as "unknown".
 *
 * If a run here looks broken, suspect the call before the engine.
 *
 * Usage:  node smoke.mjs [games]
 */
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import * as E from './engine.js';

const HERE = dirname(fileURLToPath(import.meta.url));
const db = JSON.parse(readFileSync(join(HERE, 'cards.json'), 'utf8'));
const GAMES = Number(process.argv[2] || 200);

// --- decks, built the way the engine expects -------------------------------
const deckOf = (name) => {
  const sd = db.starter_decks[name];
  return E.buildDeck(sd.list || sd, 2);   // 15 distinct ids x 2 copies = 30
};
const names = Object.keys(db.starter_decks);
const A = deckOf(names[0]);
const B = deckOf(names[1]);

let fail = 0;
const check = (label, cond, detail = '') => {
  if (!cond) fail++;
  console.log(`  ${cond ? 'PASS' : 'FAIL'}  ${label}${detail ? '  ' + detail : ''}`);
};

console.log(`${db.game} — engine smoke test`);
console.log(`decks: ${names[0]} (${A.length}) vs ${names[1]} (${B.length})\n`);

console.log('structure');
check('deck A legal', E.validateDeck(A, db.cards).length === 0, JSON.stringify(E.validateDeck(A, db.cards)).slice(0, 90));
check('deck B legal', E.validateDeck(B, db.cards).length === 0);
check('card text within budget',
  db.cards.every(c => (c.text || '').length <= (E.CONST.TEXT_BUDGET + 10)),
  `budget ${E.CONST.TEXT_BUDGET}, max seen ${Math.max(...db.cards.map(c => (c.text || '').length))}`);

const newGame = (seed) => E.createGame({ seed, decks: { A, B }, cards: db.cards });

console.log('\ndeterminism & purity');
{
  const h = (s) => (E.hashState ? E.hashState(s) : JSON.stringify(s));
  check('same seed => same initial hash', h(newGame(42)) === h(newGame(42)));
  // replay an identical action sequence from one seed and compare
  const run = () => {
    let s = newGame(1234), n = 0;
    while (!E.isTerminal(s) && n < 500) {
      const la = E.legalActions(s);
      if (!la.length) break;
      s = E.applyAction(s, la[n % la.length]);
      n++;
    }
    return h(s);
  };
  check('same seed + same actions => same final hash', run() === run());
  const s0 = newGame(9);
  const before = JSON.stringify(s0);
  E.applyAction(s0, E.legalActions(s0)[0]);
  check('applyAction does not mutate its input', JSON.stringify(s0) === before);
}

// --- self-play ------------------------------------------------------------
console.log(`\nself-play (${GAMES} games, substantive-action bias)`);
const lens = [];
const wins = { A: 0, B: 0, draw: 0 };
const offered = {};
let armedChosen = 0, firedChosen = 0, gamesWithFire = 0, turnsTotal = 0;

for (let seed = 1; seed <= GAMES; seed++) {
  let s = newGame(seed), n = 0, firedHere = 0;
  while (!E.isTerminal(s) && n < 5000) {
    const la = E.legalActions(s);
    if (!la.length) break;
    for (const a of la) offered[a.t] = (offered[a.t] || 0) + 1;
    // prefer doing something over ending the turn, so games are real
    const real = la.filter(a => a.t !== 'END_TURN' && a.t !== 'PASS');
    const pool = real.length ? real : la;
    const a = pool[(seed * 7919 + n * 104729) % pool.length];
    if (a.t === 'ARM') armedChosen++;
    if (a.t === 'FIRE') { firedChosen++; firedHere++; }
    s = E.applyAction(s, a);
    n++;
  }
  lens.push(n);
  turnsTotal += s.turn || 0;
  const w = E.winner(s);
  wins[w === 'A' ? 'A' : w === 'B' ? 'B' : 'draw']++;
  if (firedHere) gamesWithFire++;
}
lens.sort((a, b) => a - b);
const med = lens[Math.floor(lens.length / 2)];
const p1 = wins.A / GAMES;

console.log(`  actions/game   median ${med}  range ${lens[0]}-${lens[lens.length - 1]}`);
console.log(`  turns/game     mean ${(turnsTotal / GAMES).toFixed(1)}  (TURN_LIMIT ${E.CONST.TURN_LIMIT})`);
console.log(`  winner         A ${wins.A}  B ${wins.B}  draw ${wins.draw}   (P1 ${(p1 * 100).toFixed(1)}%)`);
console.log(`  ARM chosen     ${armedChosen}   FIRE chosen ${firedChosen}`);
console.log(`  games where a Response fired: ${gamesWithFire}/${GAMES} (${(gamesWithFire / GAMES * 100).toFixed(1)}%)`);
console.log(`  action types offered: ${Object.entries(offered).map(([k, v]) => k + ':' + v).join('  ')}`);

console.log('\nthe question this prototype exists to answer');
// Random play is not skilled play, so these are floors, not verdicts.
check('games reach a real length (not fatigue-stalling)', med > 30, `median ${med} actions`);
check('the Response layer is reachable', (offered.ARM || 0) > 0 && (offered.FIRE || 0) > 0);
check('Responses actually fire, not just get armed', gamesWithFire / GAMES > 0.10,
  `${(gamesWithFire / GAMES * 100).toFixed(1)}% of games`);
check('no runaway first-player advantage', p1 > 0.35 && p1 < 0.65, `P1 ${(p1 * 100).toFixed(1)}%`);

console.log(`\n${fail ? fail + ' CHECK(S) FAILED' : 'ALL CHECKS PASSED'}`);
console.log('Note: random action selection is a lower bound on how much the Response\n' +
            'layer gets used. A competent agent should use it more, not less.');
process.exit(fail ? 1 : 0);
