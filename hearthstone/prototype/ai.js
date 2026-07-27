/**
 * PARRY opponent AI — a readable greedy heuristic.
 *
 * The one thing it must do is USE the Response layer, otherwise the prototype
 * demonstrates nothing. So it arms when it can afford to, fires when the incoming
 * action is actually worth answering, and — the part that makes the mechanic a real
 * decision — sometimes holds, because a spent Response is a Response you no longer
 * threaten with.
 *
 * It also plays around a VISIBLE enemy Response, which is the skill the design is
 * trying to create: opponent.response being non-null is public information.
 *
 * Pure functions over engine state. No DOM.
 */

const UNIT_W = { attack: 1.0, health: 0.8, keyword: 0.6 };

function cardOf(state, id) {
  return state.cards[id] || null;
}

function boardValue(u) {
  if (!u) return 0;
  return u.attack * UNIT_W.attack + u.health * UNIT_W.health +
         (u.keywords || []).length * UNIT_W.keyword;
}

function sideScore(state, me) {
  const p = state.players[me];
  const o = state.players[me === 'A' ? 'B' : 'A'];
  const board = p.board.reduce((n, u) => n + boardValue(u), 0);
  const oppBoard = o.board.reduce((n, u) => n + boardValue(u), 0);
  return (board - oppBoard)
       + (p.hero.health + p.hero.armor) * 0.9
       - (o.hero.health + o.hero.armor) * 0.9
       + p.hand.length * 0.35
       + (p.response ? 1.2 : 0)      // an armed Response has threat value unspent
       + p.guard * 0.4;
}

/** Would this action kill the opponent outright? */
function isLethal(state, action, me, engine) {
  try {
    const next = engine.applyAction(state, action);
    return engine.isTerminal(next) && engine.winner(next) === me;
  } catch { return false; }
}

/**
 * Pick an action. `engine` is passed in so this module stays dependency-free and
 * testable against a stubbed engine.
 */
export function chooseAction(engine, state, me = 'B', rnd = Math.random) {
  const legal = engine.legalActions(state);
  if (!legal.length) return null;

  // Mulligan: keep the hand. Deck evaluation is out of scope for a heuristic.
  const mull = legal.find(a => a.t === 'MULLIGAN');
  if (mull) return { ...mull, toss: [] };

  // --- responding on the opponent's turn -------------------------------------
  const fires = legal.filter(a => a.t === 'FIRE');
  if (fires.length) {
    const pass = legal.find(a => a.t === 'PASS');
    // Fire if it wins, or if it improves the position by a real margin. The margin
    // is what stops the AI dumping a Response on a 1/1 -- holding has value.
    let best = null, bestGain = 0;
    const base = sideScore(state, me);
    for (const f of fires) {
      if (isLethal(state, f, me, engine)) return f;
      let gain;
      try { gain = sideScore(engine.applyAction(state, f), me) - base; }
      catch { continue; }
      if (gain > bestGain) { bestGain = gain; best = f; }
    }
    const THRESHOLD = 1.6;
    if (best && bestGain >= THRESHOLD) return best;
    if (pass) return pass;
    return best || fires[0];
  }

  // --- our own turn ----------------------------------------------------------
  const opp = state.players[me === 'A' ? 'B' : 'A'];
  const oppArmed = !!opp.response;          // public by design; play around it

  // 1. take a win if one exists
  for (const a of legal) {
    if (a.t === 'ATTACK' || a.t === 'PLAY_SPELL' || a.t === 'PLAY_UNIT') {
      if (isLethal(state, a, me, engine)) return a;
    }
  }

  // 2. score every non-terminal action one ply deep
  const base = sideScore(state, me);
  const scored = [];
  for (const a of legal) {
    if (a.t === 'END_TURN') continue;
    let sc;
    try { sc = sideScore(engine.applyAction(state, a), me) - base; }
    catch { continue; }

    // Playing into a live enemy Response is a real risk. Discount committing a
    // big unit or a key spell while they are armed -- this is the counterplay the
    // public-information design is meant to create.
    if (oppArmed) {
      const c = a.card ? cardOf(state, a.card) : null;
      if (c && (c.cost || 0) >= 3) sc -= 1.1;
      if (a.t === 'PLAY_SPELL') sc -= 0.8;   // counterable
    }
    // Arming is an investment, not immediate value; nudge it so it happens.
    if (a.t === 'ARM') sc += 1.5;

    scored.push({ a, sc });
  }

  if (!scored.length) return legal.find(a => a.t === 'END_TURN') || legal[0];

  scored.sort((x, y) => y.sc - x.sc);
  const top = scored[0];

  // 3. end the turn rather than make a clearly bad play
  if (top.sc <= 0.05) {
    const end = legal.find(a => a.t === 'END_TURN');
    if (end) return end;
  }

  // slight noise among near-equal options so games are not identical
  const band = scored.filter(s => s.sc >= top.sc - 0.35);
  return band[Math.floor(rnd() * band.length)].a;
}

export default { chooseAction };
