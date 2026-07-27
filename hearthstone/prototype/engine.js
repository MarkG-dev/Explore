// PARRY — rules engine.
//
// Pure ES module. No DOM, no imports, no globals, no wall clock.
// All randomness flows through one mulberry32 PRNG seeded from `seed` and
// carried inside the state, so `seed + action list => identical game`.
//
// Spec: ./SPEC.md   Cards: ./cards.json
//
// Public API (see also API NOTES at the bottom of this header):
//   createGame(seed, deckA, deckB, cards?) -> State
//   createGame({ seed, decks:{A,B}, cards, ...options }) -> State
//   legalActions(state)        -> Action[]
//   applyAction(state, action) -> State        (new state; input never mutated)
//   applyActionWithEvents(s,a) -> { state, events }
//   isTerminal(state)          -> boolean
//   winner(state)              -> null | 'A' | 'B' | 'DRAW'
//   hashState(state)           -> string
//
// The returned State carries `state.events` = the events produced by the action
// that created it. SPEC §10.1 writes the signature as `{ state, events }`; the
// task brief writes it as `newState`. Both are provided; they wrap one core.

export const ENGINE_VERSION = '1.0.0';

export const CONST = Object.freeze({
  HERO_HEALTH: 25,
  BOARD_WIDTH: 6,
  HAND_CAP: 10,
  MANA_CAP: 10,
  GUARD_CAP: 3,
  TURN_LIMIT: 40,
  DEATH_PASS_LIMIT: 16,
  TEXT_BUDGET: 60,
});

const WINDOWS = Object.freeze(['CAST', 'DEPLOY', 'STRIKE', 'END']);
const TRIGGERS = Object.freeze(['ARRIVAL', 'FALL', 'TURN_END', 'FUSE']);

// ---------------------------------------------------------------------------
// 1. PRNG — mulberry32, exactly as specified in SPEC §10. Do not substitute.
// ---------------------------------------------------------------------------

export function nextRandom(state) {
  let t = (state.rngState = (state.rngState + 0x6d2b79f5) >>> 0);
  t = Math.imul(t ^ (t >>> 15), t | 1);
  t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}

export function randInt(state, n) {
  return Math.floor(nextRandom(state) * n);
}

function shuffle(state, arr) {
  for (let i = arr.length - 1; i > 0; i--) {
    const j = randInt(state, i + 1);
    const tmp = arr[i];
    arr[i] = arr[j];
    arr[j] = tmp;
  }
  return arr;
}

// Seeds may be numbers or strings; strings are folded to a uint32 deterministically.
function seedToUint32(seed) {
  if (typeof seed === 'number' && Number.isFinite(seed)) return seed >>> 0;
  const s = String(seed);
  let h = 2166136261 >>> 0;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619) >>> 0;
  }
  return h >>> 0;
}

// ---------------------------------------------------------------------------
// 2. Card database + effect parser (kept OUT of the mutable state; shared and
//    frozen, so cloning a state never copies it).
// ---------------------------------------------------------------------------

function parseStmts(src) {
  return src
    .split(';')
    .map((x) => x.trim())
    .filter((x) => x.length > 0)
    .map((x) => x.split(':').map((p) => p.trim()));
}

export function parseEffect(str) {
  const src = (str == null ? '' : String(str)).trim();
  if (src === '' || src === 'NONE') {
    return { kind: 'plain', trigger: null, stmts: [] };
  }
  if (src.startsWith('RESPONSE|')) {
    const modes = src
      .split('|')
      .slice(1)
      .map((chunk, i) => {
        const at = chunk.indexOf('@');
        const gt = chunk.indexOf('>', at < 0 ? 0 : at);
        if (at < 0 || gt < 0) {
          throw new Error(`PARRY: malformed RESPONSE mode "${chunk}"`);
        }
        const windows = chunk
          .slice(at + 1, gt)
          .split(',')
          .map((w) => w.trim().toUpperCase());
        for (const w of windows) {
          if (w !== 'ANY' && !WINDOWS.includes(w)) {
            throw new Error(`PARRY: unknown window "${w}"`);
          }
        }
        return {
          index: i,
          label: chunk.slice(0, at),
          windows,
          stmts: parseStmts(chunk.slice(gt + 1)),
        };
      });
    return { kind: 'response', modes };
  }
  const m = /^([A-Z_]+)>([\s\S]*)$/.exec(src);
  if (m && TRIGGERS.includes(m[1])) {
    return { kind: 'plain', trigger: m[1], stmts: parseStmts(m[2]) };
  }
  return { kind: 'plain', trigger: null, stmts: parseStmts(src) };
}

function stmtsNeedTarget(stmts) {
  return stmts.length > 0 && stmts[0][0] === 'TARGET' ? stmts[0][1] : null;
}

function stmtsUseTrigger(stmts) {
  return stmts.some((p) => p.slice(1).some((a) => a === 'TRIGGER'));
}

function normalizeCard(raw) {
  const kws = (raw.keywords || []).map((k) => String(k).toUpperCase());
  const parsed = parseEffect(raw.effect);
  const card = {
    id: raw.id,
    name: raw.name,
    faction: raw.faction,
    type: raw.type,
    cost: raw.cost | 0,
    attack: raw.attack == null ? 0 : raw.attack | 0,
    health: raw.health == null ? 0 : raw.health | 0,
    keywords: kws,
    text: raw.text || '',
    effect: raw.effect == null ? 'NONE' : raw.effect,
    parsed,
    needsTarget: parsed.kind === 'plain' ? stmtsNeedTarget(parsed.stmts) : null,
  };
  return Object.freeze(card);
}

// Accepts: the parsed cards.json object, a bare array of cards, or an id->card map.
export function normalizeCards(input) {
  let list;
  if (!input) list = [];
  else if (Array.isArray(input)) list = input;
  else if (Array.isArray(input.cards)) list = input.cards;
  else list = Object.values(input);
  const byId = Object.create(null);
  for (const raw of list) {
    if (!raw || !raw.id) continue;
    byId[raw.id] = normalizeCard(raw);
  }
  return Object.freeze({ byId: Object.freeze(byId) });
}

function cardDef(s, id) {
  const c = s.cards.byId[id];
  if (!c) throw new Error(`PARRY: unknown card id "${id}"`);
  return c;
}

// ---------------------------------------------------------------------------
// 3. Structural clone + canonical hashing
// ---------------------------------------------------------------------------

function deepClone(v) {
  if (v === null || typeof v !== 'object') return v;
  if (Array.isArray(v)) {
    const out = new Array(v.length);
    for (let i = 0; i < v.length; i++) out[i] = deepClone(v[i]);
    return out;
  }
  const out = {};
  for (const k in v) out[k] = deepClone(v[k]);
  return out;
}

function cloneState(s) {
  const out = {};
  for (const k in s) {
    if (k === 'cards') out[k] = s[k]; // frozen shared card DB: never cloned
    else out[k] = deepClone(s[k]);
  }
  return out;
}

const HASH_SKIP = new Set(['cards', 'events']);

function canon(v) {
  if (v === null || typeof v !== 'object') return JSON.stringify(v) ?? 'null';
  if (Array.isArray(v)) return '[' + v.map(canon).join(',') + ']';
  const keys = Object.keys(v)
    .filter((k) => !HASH_SKIP.has(k))
    .sort();
  return '{' + keys.map((k) => JSON.stringify(k) + ':' + canon(v[k])).join(',') + '}';
}

export function serializeState(state) {
  return canon(state);
}

export function hashState(state) {
  const str = canon(state);
  let h1 = 2166136261 >>> 0;
  let h2 = 0x811c9dc5 >>> 0;
  for (let i = 0; i < str.length; i++) {
    const c = str.charCodeAt(i);
    h1 = Math.imul(h1 ^ c, 16777619) >>> 0;
    h2 = Math.imul(h2 + c + i, 2246822519) >>> 0;
    h2 = ((h2 << 13) | (h2 >>> 19)) >>> 0;
  }
  return (
    str.length.toString(16) +
    '-' +
    h1.toString(16).padStart(8, '0') +
    h2.toString(16).padStart(8, '0')
  );
}

// ---------------------------------------------------------------------------
// 4. References. A ref is a short string: "u<uid>" for a unit, "hA"/"hB" for a hero.
// ---------------------------------------------------------------------------

const other = (p) => (p === 'A' ? 'B' : 'A');
const heroRef = (p) => 'h' + p;
const unitRef = (u) => 'u' + u.uid;

function findUnit(s, uid) {
  for (const p of ['A', 'B']) {
    const b = s.players[p].board;
    for (let i = 0; i < b.length; i++) if (b[i].uid === uid) return { u: b[i], owner: p, idx: i };
  }
  return null;
}

function deref(s, ref) {
  if (typeof ref !== 'string' || ref.length < 2) return null;
  if (ref[0] === 'h') {
    const p = ref.slice(1);
    if (p !== 'A' && p !== 'B') return null;
    return { kind: 'hero', player: p, hero: s.players[p].hero };
  }
  if (ref[0] === 'u') {
    const uid = Number(ref.slice(1));
    const hit = findUnit(s, uid);
    return hit ? { kind: 'unit', player: hit.owner, unit: hit.u } : null;
  }
  return null;
}

const validRef = (s, ref) => deref(s, ref) !== null;

// ---------------------------------------------------------------------------
// 5. Events
// ---------------------------------------------------------------------------

function ev(s, e) {
  s.events.push(e);
  return e;
}

// ---------------------------------------------------------------------------
// 6. Setup
// ---------------------------------------------------------------------------

function makePlayer(id) {
  return {
    id,
    hero: { health: CONST.HERO_HEALTH, maxHealth: CONST.HERO_HEALTH, armor: 0 },
    deck: [],
    hand: [],
    discard: [],
    board: [],
    mana: 0,
    manaMax: 0,
    guard: 0,
    response: null, // { card } — face-down; cost is public via cards[card].cost
    responseUsedThisTurn: false,
    fuse: [], // FIFO [{ card }]
    fatigue: 0,
    mulliganDone: false,
  };
}

/**
 * createGame(seed, deckA, deckB, cards)
 * createGame({ seed, decks:{A,B}, cards, shuffle?, firstPlayer?, skipMulligan? })
 *
 * Deck entries are card ids (strings) when `cards` is supplied, or card objects
 * (which are then registered into the card DB automatically).
 *
 * `shuffle:false`, `firstPlayer` and `skipMulligan:true` are test affordances;
 * the default path is exactly SPEC §1.
 */
export function createGame(a, b, c, d) {
  let opts;
  if (a && typeof a === 'object' && !Array.isArray(a)) opts = a;
  else opts = { seed: a, decks: { A: b, B: c }, cards: d };

  const rawA = (opts.decks && opts.decks.A) || opts.deckA || [];
  const rawB = (opts.decks && opts.decks.B) || opts.deckB || [];

  // Build the card DB: whatever was passed in, plus any inline card objects in decks.
  const supplied = [];
  if (opts.cards) {
    const n = normalizeCards(opts.cards);
    for (const k in n.byId) supplied.push(n.byId[k]);
  }
  for (const entry of [].concat(rawA, rawB)) {
    if (entry && typeof entry === 'object') supplied.push(entry);
  }
  const cards = normalizeCards(supplied);

  const idsOf = (deck) => deck.map((e) => (typeof e === 'object' && e ? e.id : e));

  const s = {
    seed: opts.seed == null ? 0 : opts.seed,
    rngState: seedToUint32(opts.seed == null ? 0 : opts.seed),
    cards,
    turn: 0,
    active: 'A',
    phase: 'MULLIGAN', // MULLIGAN | PLAY | OVER
    mulliganTurn: null,
    firstPlayer: 'A',
    players: { A: makePlayer('A'), B: makePlayer('B') },
    awaiting: null,
    result: null,
    nextUid: 1,
    events: [],
  };

  s.players.A.deck = idsOf(rawA);
  s.players.B.deck = idsOf(rawB);
  for (const p of ['A', 'B']) {
    for (const id of s.players[p].deck) cardDef(s, id); // fail loudly on unknown ids
  }

  // PRNG call order is fixed (SPEC §10): shuffle A, shuffle B, coin flip,
  // then mulligan reshuffles first-player-then-second.
  const doShuffle = opts.shuffle !== false;
  if (doShuffle) {
    shuffle(s, s.players.A.deck);
    shuffle(s, s.players.B.deck);
  }
  const coin = nextRandom(s);
  s.firstPlayer = opts.firstPlayer === 'A' || opts.firstPlayer === 'B'
    ? opts.firstPlayer
    : coin < 0.5 ? 'A' : 'B';
  const second = other(s.firstPlayer);

  ev(s, { e: 'SETUP', first: s.firstPlayer });

  drawCards(s, s.firstPlayer, 3);
  drawCards(s, second, 4);
  s.players[second].guard = 1; // §1.3 — the going-second compensation, paid in Guard
  ev(s, { e: 'GUARD', player: second, guard: 1, reason: 'GOING_SECOND' });

  if (opts.skipMulligan) {
    s.players.A.mulliganDone = true;
    s.players.B.mulliganDone = true;
    s.phase = 'PLAY';
    startTurn(s, s.firstPlayer);
  } else {
    s.mulliganTurn = s.firstPlayer;
  }
  return s;
}

// ---------------------------------------------------------------------------
// 7. Primitive state mutators (operate on the working clone only)
// ---------------------------------------------------------------------------

function drawCards(s, pid, n) {
  const p = s.players[pid];
  for (let i = 0; i < n; i++) {
    if (s.result) return;
    if (p.deck.length === 0) {
      p.fatigue += 1;
      ev(s, { e: 'FATIGUE', player: pid, amount: p.fatigue });
      damageHero(s, pid, p.fatigue);
      continue;
    }
    const card = p.deck.shift();
    if (p.hand.length >= CONST.HAND_CAP) {
      p.discard.push(card);
      ev(s, { e: 'BURN', player: pid, card });
    } else {
      p.hand.push(card);
      ev(s, { e: 'DRAW', player: pid, card });
    }
  }
}

function damageHero(s, pid, n) {
  if (n <= 0) return;
  const h = s.players[pid].hero;
  const absorbed = Math.min(h.armor, n);
  h.armor -= absorbed;
  h.health -= n - absorbed;
  ev(s, { e: 'DAMAGE_HERO', player: pid, amount: n, absorbed, health: h.health });
  checkHeroes(s);
}

function damageUnit(s, unit, n) {
  if (n <= 0) return;
  const i = unit.keywords.indexOf('WARD');
  if (i >= 0) {
    unit.keywords.splice(i, 1);
    ev(s, { e: 'WARD_BROKEN', uid: unit.uid });
    return;
  }
  unit.health -= n;
  ev(s, { e: 'DAMAGE_UNIT', uid: unit.uid, amount: n, health: unit.health });
}

function healEntity(s, target, n) {
  if (n <= 0) return;
  if (target.kind === 'hero') {
    target.hero.health = Math.min(target.hero.maxHealth, target.hero.health + n);
    ev(s, { e: 'HEAL_HERO', player: target.player, health: target.hero.health });
  } else {
    const u = target.unit;
    u.health = Math.min(u.maxHealth, u.health + n);
    ev(s, { e: 'HEAL_UNIT', uid: u.uid, health: u.health });
  }
}

function gainGuard(s, pid, n) {
  const p = s.players[pid];
  p.guard = Math.min(CONST.GUARD_CAP, p.guard + n);
  ev(s, { e: 'GUARD', player: pid, guard: p.guard });
}

function makeUnit(s, owner, spec) {
  return {
    uid: s.nextUid++,
    cardId: spec.cardId || null,
    name: spec.name,
    attack: spec.attack,
    health: spec.health,
    maxHealth: spec.health,
    keywords: spec.keywords.slice(),
    attacksUsed: 0,
    summoningSick: true,
    stun: 0,
    owner,
    token: !!spec.token,
  };
}

function placeUnit(s, owner, unit) {
  const p = s.players[owner];
  if (p.board.length >= CONST.BOARD_WIDTH) return null; // SUMMON into a full board: skipped
  p.board.push(unit);
  ev(s, { e: 'UNIT_ENTER', player: owner, uid: unit.uid, name: unit.name });
  return unit;
}

function checkHeroes(s) {
  if (s.result) return;
  const a = s.players.A.hero.health <= 0;
  const b = s.players.B.hero.health <= 0;
  if (a && b) setResult(s, 'DRAW');
  else if (a) setResult(s, 'B');
  else if (b) setResult(s, 'A');
}

function setResult(s, r) {
  if (s.result) return;
  s.result = r;
  s.phase = 'OVER';
  s.awaiting = null;
  ev(s, { e: 'GAME_OVER', result: r });
}

// Death collection. SPEC §6.4: after the current effect has fully resolved,
// deaths are collected and FALL> triggers fire left to right by board index;
// deaths caused by a FALL> go into a second pass, hard limit 16 passes.
function resolveDeaths(s) {
  for (let pass = 0; pass < CONST.DEATH_PASS_LIMIT; pass++) {
    if (s.result) return;
    const dead = [];
    for (const pid of [s.active, other(s.active)]) {
      const b = s.players[pid].board;
      for (let i = 0; i < b.length; i++) if (b[i].health <= 0) dead.push({ u: b[i], owner: pid });
    }
    if (dead.length === 0) return;
    for (const d of dead) {
      const b = s.players[d.owner].board;
      const at = b.indexOf(d.u);
      if (at >= 0) b.splice(at, 1);
      if (!d.u.token && d.u.cardId) s.players[d.owner].discard.push(d.u.cardId);
      ev(s, { e: 'UNIT_DIES', player: d.owner, uid: d.u.uid, name: d.u.name });
    }
    for (const d of dead) {
      if (s.result) return;
      runUnitTrigger(s, d.u, d.owner, 'FALL', null, /*selfOnBoard*/ false);
    }
    checkHeroes(s);
  }
}

// ---------------------------------------------------------------------------
// 8. Selectors and the effect resolver — SPEC §11. The whole engine is one switch.
// ---------------------------------------------------------------------------

function selectRefs(s, ctx, sel) {
  const me = ctx.controller;
  const foe = other(me);
  switch (sel) {
    case 'T':
      return ctx.bound && validRef(s, ctx.bound) ? [ctx.bound] : [];
    case 'TRIGGER':
      return ctx.trigger && validRef(s, ctx.trigger) ? [ctx.trigger] : [];
    case 'SELF':
      return ctx.self && validRef(s, ctx.self) ? [ctx.self] : [];
    case 'SELF_HERO':
      return [heroRef(me)];
    case 'ENEMY_HERO':
      return [heroRef(foe)];
    case 'ALL_ALLY_UNITS':
      return s.players[me].board.map(unitRef);
    case 'ALL_ENEMY_UNITS':
      return s.players[foe].board.map(unitRef);
    case 'ALL_UNITS':
      return s.players[me].board.map(unitRef).concat(s.players[foe].board.map(unitRef));
    case 'RANDOM_ENEMY_UNIT': {
      const b = s.players[foe].board;
      if (b.length === 0) return [];
      return [unitRef(b[randInt(s, b.length)])];
    }
    // Target-only selectors: meaningful in TARGET:<sel>, empty as an apply-time set.
    case 'UNIT':
    case 'ALLY_UNIT':
    case 'ENEMY_UNIT':
    case 'ANY':
      return [];
    default:
      throw new Error(`PARRY: unknown selector "${sel}"`);
  }
}

// Candidate list for TARGET:<sel>, used by legalActions.
export function targetCandidates(s, controller, sel) {
  const me = controller;
  const foe = other(me);
  switch (sel) {
    case 'UNIT':
      return s.players[me].board.map(unitRef).concat(s.players[foe].board.map(unitRef));
    case 'ALLY_UNIT':
      return s.players[me].board.map(unitRef);
    case 'ENEMY_UNIT':
      return s.players[foe].board.map(unitRef);
    case 'ANY':
      return s.players[me].board
        .map(unitRef)
        .concat(s.players[foe].board.map(unitRef))
        .concat([heroRef(me), heroRef(foe)]);
    case 'ENEMY_HERO':
      return [heroRef(foe)];
    case 'SELF_HERO':
      return [heroRef(me)];
    default:
      return [];
  }
}

function mkCtx(controller, opts) {
  return {
    controller,
    self: (opts && opts.self) || null,
    trigger: (opts && opts.trigger) || null,
    bound: (opts && opts.bound) || null,
    window: (opts && opts.window) || null,
    counter: false,
    cancelAttack: false,
  };
}

function resolveStmts(s, ctx, stmts) {
  for (const parts of stmts) {
    if (s.result) return ctx;
    applyStmt(s, ctx, parts);
  }
  return ctx;
}

function applyStmt(s, ctx, parts) {
  const verb = parts[0];
  const me = ctx.controller;
  switch (verb) {
    case 'NONE':
      return;

    case 'TARGET':
      // The binding was chosen when the action was declared; nothing to do here.
      // (An unbound TARGET makes every later `T` select nothing, which fizzles.)
      return;

    case 'DEAL': {
      const n = Number(parts[1]);
      for (const ref of selectRefs(s, ctx, parts[2])) {
        const t = deref(s, ref);
        if (!t) continue;
        if (t.kind === 'hero') damageHero(s, t.player, n);
        else damageUnit(s, t.unit, n);
      }
      return;
    }

    case 'HEAL': {
      const n = Number(parts[1]);
      for (const ref of selectRefs(s, ctx, parts[2])) {
        const t = deref(s, ref);
        if (t) healEntity(s, t, n);
      }
      return;
    }

    case 'ARMOR': {
      const n = Number(parts[1]);
      s.players[me].hero.armor += n;
      ev(s, { e: 'ARMOR', player: me, armor: s.players[me].hero.armor });
      return;
    }

    case 'DRAW':
      drawCards(s, me, Number(parts[1]));
      return;

    case 'SUMMON': {
      const [atk, hp] = parts[1].split('/').map(Number);
      const name = parts[2];
      const kws = (parts[3] ? parts[3].split(',') : []).map((k) => k.trim().toUpperCase());
      const u = makeUnit(s, me, { name, attack: atk, health: hp, keywords: kws, token: true });
      placeUnit(s, me, u); // opens no DEPLOY window — SPEC §6
      return;
    }

    case 'BUFF': {
      const [atk, hp] = parts[1].split('/').map(Number);
      for (const ref of selectRefs(s, ctx, parts[2])) {
        const t = deref(s, ref);
        if (!t || t.kind !== 'unit') continue;
        t.unit.attack += atk;
        t.unit.maxHealth += hp;
        t.unit.health += hp;
        ev(s, { e: 'BUFF', uid: t.unit.uid, attack: t.unit.attack, health: t.unit.health });
      }
      return;
    }

    case 'GRANT': {
      const kw = String(parts[1]).toUpperCase();
      for (const ref of selectRefs(s, ctx, parts[2])) {
        const t = deref(s, ref);
        if (!t || t.kind !== 'unit') continue;
        if (!t.unit.keywords.includes(kw)) t.unit.keywords.push(kw);
        ev(s, { e: 'GRANT', uid: t.unit.uid, keyword: kw });
      }
      return;
    }

    case 'DESTROY': {
      for (const ref of selectRefs(s, ctx, parts[1])) {
        const t = deref(s, ref);
        if (!t || t.kind !== 'unit') continue;
        t.unit.health = 0; // ignores Ward by construction: Ward only intercepts damage
        ev(s, { e: 'DESTROY', uid: t.unit.uid });
      }
      return;
    }

    case 'RETURN': {
      for (const ref of selectRefs(s, ctx, parts[1])) {
        const t = deref(s, ref);
        if (!t || t.kind !== 'unit') continue;
        const owner = t.unit.owner;
        const b = s.players[owner].board;
        const at = b.indexOf(t.unit);
        if (at >= 0) b.splice(at, 1);
        if (!t.unit.token && t.unit.cardId) {
          if (s.players[owner].hand.length < CONST.HAND_CAP) {
            s.players[owner].hand.push(t.unit.cardId);
            ev(s, { e: 'RETURN', uid: t.unit.uid, player: owner, card: t.unit.cardId });
          } else {
            ev(s, { e: 'RETURN_LOST', uid: t.unit.uid, player: owner });
          }
        } else {
          ev(s, { e: 'TOKEN_GONE', uid: t.unit.uid, player: owner });
        }
      }
      return;
    }

    case 'STUN': {
      for (const ref of selectRefs(s, ctx, parts[1])) {
        const t = deref(s, ref);
        if (!t || t.kind !== 'unit') continue;
        t.unit.stun = 2;
        ev(s, { e: 'STUN', uid: t.unit.uid });
      }
      return;
    }

    case 'GAIN_GUARD':
      gainGuard(s, me, Number(parts[1]));
      return;

    case 'REFRESH_ATTACKS': {
      for (const ref of selectRefs(s, ctx, parts[1])) {
        const t = deref(s, ref);
        if (!t || t.kind !== 'unit') continue;
        t.unit.attacksUsed = 0;
        ev(s, { e: 'REFRESH', uid: t.unit.uid });
      }
      return;
    }

    case 'COUNTER':
      ctx.counter = true;
      return;

    case 'CANCEL_ATTACK':
      ctx.cancelAttack = true;
      return;

    default:
      throw new Error(`PARRY: unknown verb "${verb}"`);
  }
}

// Fire a unit's ARRIVAL>/FALL>/TURN_END> trigger.
function runUnitTrigger(s, unit, owner, which, boundTarget, selfOnBoard) {
  if (s.result) return;
  if (!unit.cardId) return; // tokens have no printed effect
  const def = cardDef(s, unit.cardId);
  const parsed = def.parsed;
  if (parsed.kind !== 'plain' || parsed.trigger !== which) return;
  const needs = stmtsNeedTarget(parsed.stmts);
  if (needs && !validRef(s, boundTarget)) return; // no legal target => trigger skipped
  const ctx = mkCtx(owner, {
    self: selfOnBoard ? unitRef(unit) : null,
    bound: boundTarget || null,
  });
  ev(s, { e: 'TRIGGER', which, player: owner, uid: unit.uid, card: unit.cardId });
  resolveStmts(s, ctx, parsed.stmts);
  resolveDeaths(s);
}

// ---------------------------------------------------------------------------
// 9. Turn structure
// ---------------------------------------------------------------------------

function startTurn(s, pid) {
  if (s.result) return;
  const p = s.players[pid];
  const foe = s.players[other(pid)];

  s.turn += 1; // 1
  s.active = pid;
  p.manaMax = Math.min(CONST.MANA_CAP, p.manaMax + 1); // 2
  p.mana = p.manaMax;
  foe.responseUsedThisTurn = false; // 3 — the defender's one firing is refreshed
  ev(s, { e: 'TURN_START', player: pid, turn: s.turn, mana: p.mana });

  // 4 — Fuse queue, FIFO. Opens no response window.
  while (p.fuse.length > 0) {
    if (s.result) return;
    const entry = p.fuse.shift();
    const def = cardDef(s, entry.card);
    ev(s, { e: 'FUSE_RESOLVE', player: pid, card: entry.card });
    resolveStmts(s, mkCtx(pid, {}), def.parsed.stmts);
    resolveDeaths(s);
    p.discard.push(entry.card);
  }
  if (s.result) return;

  for (const u of p.board) {
    // 5
    u.attacksUsed = 0;
    u.summoningSick = false;
  }
  drawCards(s, pid, 1); // 6
}

// End Step, part 1: TURN_END> triggers, then the END window.
function beginEndStep(s) {
  const pid = s.active;
  const board = s.players[pid].board.slice(); // left to right by board index
  for (const u of board) {
    if (s.result) return;
    if (s.players[pid].board.indexOf(u) < 0) continue;
    runUnitTrigger(s, u, pid, 'TURN_END', null, true);
  }
  if (s.result) return;
  openWindow(s, 'END', { kind: 'END' });
}

// End Step, part 2: everything after the END window.
function finishEndStep(s) {
  if (s.result) return;
  const pid = s.active;
  const p = s.players[pid];

  // 3 — leftover mana converts to Guard at 2:1, capped, no overflow banking.
  const gained = Math.floor(p.mana / 2);
  if (gained > 0) gainGuard(s, pid, gained);
  p.mana = 0;

  // 4 — stun ticks down on the active player's own units
  for (const u of p.board) if (u.stun > 0) u.stun -= 1;

  // 5 — discard down to hand cap, rightmost first
  while (p.hand.length > CONST.HAND_CAP) {
    const card = p.hand.pop();
    p.discard.push(card);
    ev(s, { e: 'DISCARD_OVER_CAP', player: pid, card });
  }

  ev(s, { e: 'TURN_END', player: pid, turn: s.turn });

  if (s.turn >= CONST.TURN_LIMIT) {
    setResult(s, 'DRAW'); // §9 — turn 40 completes => draw
    return;
  }
  startTurn(s, other(pid));
}

// ---------------------------------------------------------------------------
// 10. Response windows — SPEC §6
// ---------------------------------------------------------------------------

// Returns true if the engine halted and is now awaiting a defender decision.
function openWindow(s, kind, pending) {
  if (s.result) return false;
  const d = other(s.active);
  const dp = s.players[d];
  // NO INFORMATION LEAK BY CONSTRUCTION: the offer depends only on "a Response is
  // armed and unspent this turn". It does NOT depend on whether a mode is legal.
  if (dp.response == null || dp.responseUsedThisTurn) {
    resumePending(s, pending, { counter: false, cancelAttack: false });
    return false;
  }
  s.awaiting = { player: d, kind: 'RESPONSE', window: kind, pending, trigger: pending.trigger || null };
  ev(s, { e: 'WINDOW_OPEN', player: d, window: kind });
  return true;
}

function resumePending(s, pending, cancel) {
  if (s.result || !pending) return;
  switch (pending.kind) {
    case 'DEPLOY': {
      const hit = findUnit(s, pending.uid);
      if (!hit) {
        ev(s, { e: 'ARRIVAL_SKIPPED', uid: pending.uid });
        break; // bounced or killed inside the window: its ARRIVAL> never happens
      }
      runUnitTrigger(s, hit.u, hit.owner, 'ARRIVAL', pending.target, true);
      break;
    }

    case 'CAST': {
      const p = s.players[pending.controller];
      if (cancel.counter) {
        p.discard.push(pending.card);
        ev(s, { e: 'COUNTERED', player: pending.controller, card: pending.card });
        break; // mana stays spent, no effect resolves
      }
      const def = cardDef(s, pending.card);
      if (def.parsed.trigger === 'FUSE') {
        p.fuse.push({ card: pending.card });
        ev(s, { e: 'FUSE_ARMED', player: pending.controller, card: pending.card });
        break; // the card lives in the fuse queue; it hits the discard when it resolves
      }
      const needs = def.needsTarget;
      if (needs && !validRef(s, pending.target)) {
        ev(s, { e: 'FIZZLE', player: pending.controller, card: pending.card });
      } else {
        const ctx = mkCtx(pending.controller, { bound: pending.target || null });
        resolveStmts(s, ctx, def.parsed.stmts);
      }
      p.discard.push(pending.card);
      resolveDeaths(s);
      break;
    }

    case 'STRIKE': {
      // attacks_used was already spent at declaration (see ACT_ATTACK).
      if (cancel.cancelAttack) {
        ev(s, { e: 'ATTACK_CANCELLED', uid: pending.attacker });
        break;
      }
      const att = findUnit(s, pending.attacker);
      if (!att) {
        ev(s, { e: 'ATTACK_FIZZLE', uid: pending.attacker });
        break; // attacker died inside the window: no damage, attack still spent
      }
      const tgt = deref(s, pending.target);
      if (!tgt) {
        ev(s, { e: 'ATTACK_FIZZLE', uid: pending.attacker });
        break;
      }
      const outgoing = att.u.attack;
      ev(s, { e: 'COMBAT', attacker: att.u.uid, target: pending.target, amount: outgoing });
      if (tgt.kind === 'hero') {
        damageHero(s, tgt.player, outgoing);
      } else {
        const incoming = tgt.unit.attack; // simultaneous
        damageUnit(s, tgt.unit, outgoing);
        damageUnit(s, att.u, incoming);
      }
      resolveDeaths(s);
      break;
    }

    case 'END':
      finishEndStep(s);
      break;

    default:
      throw new Error(`PARRY: unknown pending kind "${pending.kind}"`);
  }
}

function modeLegal(s, aw, mode) {
  if (!mode.windows.includes('ANY') && !mode.windows.includes(aw.window)) return false;
  if (stmtsUseTrigger(mode.stmts) && !validRef(s, aw.trigger)) return false;
  for (const parts of mode.stmts) {
    if (parts[0] === 'COUNTER' && aw.window !== 'CAST') return false;
    if (parts[0] === 'CANCEL_ATTACK' && aw.window !== 'STRIKE') return false;
  }
  const needs = stmtsNeedTarget(mode.stmts);
  if (needs && targetCandidates(s, aw.player, needs).length === 0) return false;
  return true;
}

// ---------------------------------------------------------------------------
// 11. legalActions
// ---------------------------------------------------------------------------

function attackTargets(s, pid, attacker) {
  const foe = other(pid);
  const board = s.players[foe].board;
  const bulwarks = board.filter((u) => u.keywords.includes('BULWARK'));
  if (bulwarks.length > 0) return bulwarks.map(unitRef);
  const out = board.map(unitRef);
  // Swift's arrival-turn attack may not hit the enemy hero.
  if (!attacker.summoningSick) out.push(heroRef(foe));
  return out;
}

function canAttack(s, pid, u) {
  if (u.attacksUsed >= 1) return false;
  if (u.attack <= 0) return false;
  if (u.stun > 0) return false;
  if (u.summoningSick && !u.keywords.includes('SWIFT')) return false;
  return true;
}

function subsets(n) {
  const out = [];
  for (let mask = 0; mask < 1 << n; mask++) {
    const pick = [];
    for (let i = 0; i < n; i++) if (mask & (1 << i)) pick.push(i);
    out.push(pick);
  }
  return out;
}

export function legalActions(state) {
  const s = state;
  if (s.result) return [];

  if (s.awaiting) {
    const aw = s.awaiting;
    const out = [{ t: 'PASS' }];
    const armed = s.players[aw.player].response;
    if (armed) {
      const def = cardDef(s, armed.card);
      if (def.parsed.kind === 'response') {
        for (const mode of def.parsed.modes) {
          if (!modeLegal(s, aw, mode)) continue;
          const needs = stmtsNeedTarget(mode.stmts);
          if (needs) {
            for (const tref of targetCandidates(s, aw.player, needs)) {
              out.push({ t: 'FIRE', mode: mode.index, target: tref });
            }
          } else {
            out.push({ t: 'FIRE', mode: mode.index });
          }
        }
      }
    }
    return out;
  }

  if (s.phase === 'MULLIGAN') {
    const pid = s.mulliganTurn;
    const n = s.players[pid].hand.length;
    return subsets(n).map((toss) => ({ t: 'MULLIGAN', player: pid, toss }));
  }

  const pid = s.active;
  const p = s.players[pid];
  const out = [];
  const seen = new Set();

  for (const cardId of p.hand) {
    if (seen.has(cardId)) continue; // copies are interchangeable
    seen.add(cardId);
    const def = cardDef(s, cardId);

    if (def.type === 'UNIT') {
      if (def.cost > p.mana) continue;
      if (p.board.length >= CONST.BOARD_WIDTH) continue;
      const needs = def.parsed.trigger === 'ARRIVAL' ? def.needsTarget : null;
      if (needs) {
        const cands = targetCandidates(s, pid, needs);
        if (cands.length === 0) out.push({ t: 'PLAY_UNIT', card: cardId, target: null });
        else for (const tref of cands) out.push({ t: 'PLAY_UNIT', card: cardId, target: tref });
      } else {
        out.push({ t: 'PLAY_UNIT', card: cardId, target: null });
      }
    } else if (def.type === 'SPELL') {
      if (def.cost > p.mana) continue;
      const needs = def.parsed.trigger === null || def.parsed.trigger === 'FUSE' ? def.needsTarget : null;
      if (needs) {
        const cands = targetCandidates(s, pid, needs);
        for (const tref of cands) out.push({ t: 'PLAY_SPELL', card: cardId, target: tref });
        // no legal target => the spell is illegal to play (SPEC §11)
      } else {
        out.push({ t: 'PLAY_SPELL', card: cardId, target: null });
      }
    } else if (def.type === 'RESPONSE') {
      // ARM: own Main Step only, slot must be empty, cost paid in Guard.
      if (p.response != null) continue;
      if (def.cost > p.guard) continue;
      out.push({ t: 'ARM', card: cardId });
    }
  }

  for (const u of p.board) {
    if (!canAttack(s, pid, u)) continue;
    for (const tref of attackTargets(s, pid, u)) {
      out.push({ t: 'ATTACK', attacker: u.uid, target: tref });
    }
  }

  out.push({ t: 'END_TURN' });
  return out;
}

// ---------------------------------------------------------------------------
// 12. applyAction
// ---------------------------------------------------------------------------

function sameAction(a, b) {
  if (a.t !== b.t) return false;
  switch (a.t) {
    case 'PLAY_UNIT':
    case 'PLAY_SPELL':
      return a.card === b.card && (a.target || null) === (b.target || null);
    case 'ARM':
      return a.card === b.card;
    case 'ATTACK':
      return a.attacker === b.attacker && a.target === b.target;
    case 'FIRE':
      return a.mode === b.mode && (a.target || null) === (b.target || null);
    case 'MULLIGAN':
      return String(a.toss || []) === String(b.toss || []);
    default:
      return true;
  }
}

function normalizeAction(action) {
  const a = Object.assign({}, action);
  if (a.t === 'ARM_RESPONSE') a.t = 'ARM'; // brief spells it ARM_RESPONSE, §10.1 spells it ARM
  if (a.t === 'FIRE' && a.mode == null) a.mode = 0;
  return a;
}

export function applyAction(state, action) {
  if (!action || typeof action.t !== 'string') throw new Error('PARRY: malformed action');
  if (state.result) throw new Error('PARRY: game is over');

  const act = normalizeAction(action);
  const legal = legalActions(state);
  if (!legal.some((l) => sameAction(l, act))) {
    throw new Error(`PARRY: illegal action ${JSON.stringify(action)}`);
  }

  const s = cloneState(state);
  s.events = [];

  switch (act.t) {
    case 'MULLIGAN':
      actMulligan(s, act);
      break;
    case 'PLAY_UNIT':
      actPlayUnit(s, act);
      break;
    case 'PLAY_SPELL':
      actPlaySpell(s, act);
      break;
    case 'ARM':
      actArm(s, act);
      break;
    case 'ATTACK':
      actAttack(s, act);
      break;
    case 'END_TURN':
      beginEndStep(s);
      break;
    case 'PASS':
      actPass(s);
      break;
    case 'FIRE':
      actFire(s, act);
      break;
    default:
      throw new Error(`PARRY: unknown action "${act.t}"`);
  }
  return s;
}

export function applyActionWithEvents(state, action) {
  const next = applyAction(state, action);
  return { state: next, events: next.events };
}

function actMulligan(s, act) {
  const pid = s.mulliganTurn;
  const p = s.players[pid];
  const toss = (act.toss || []).slice().sort((x, y) => x - y);
  const returned = toss.map((i) => p.hand[i]);
  p.hand = p.hand.filter((_, i) => !toss.includes(i));
  for (const c of returned) p.deck.push(c);
  if (returned.length > 0) shuffle(s, p.deck);
  drawCards(s, pid, returned.length);
  p.mulliganDone = true;
  ev(s, { e: 'MULLIGAN', player: pid, count: returned.length });

  const secondPlayer = other(s.firstPlayer);
  if (pid === s.firstPlayer && !s.players[secondPlayer].mulliganDone) {
    s.mulliganTurn = secondPlayer;
  } else {
    s.mulliganTurn = null;
    s.phase = 'PLAY';
    startTurn(s, s.firstPlayer);
  }
}

function takeFromHand(p, cardId) {
  const i = p.hand.indexOf(cardId);
  if (i < 0) throw new Error(`PARRY: card "${cardId}" not in hand`);
  p.hand.splice(i, 1);
}

function actPlayUnit(s, act) {
  const pid = s.active;
  const p = s.players[pid];
  const def = cardDef(s, act.card);
  takeFromHand(p, act.card);
  p.mana -= def.cost;
  const unit = makeUnit(s, pid, {
    cardId: def.id,
    name: def.name,
    attack: def.attack,
    health: def.health,
    keywords: def.keywords,
  });
  placeUnit(s, pid, unit); // board fullness was checked in legalActions
  ev(s, { e: 'PLAY_UNIT', player: pid, card: def.id, uid: unit.uid, mana: p.mana });

  const pending = { kind: 'DEPLOY', uid: unit.uid, target: act.target || null, controller: pid, trigger: unitRef(unit) };
  if (def.keywords.includes('SEALED')) {
    ev(s, { e: 'SEALED', card: def.id });
    resumePending(s, pending, { counter: false, cancelAttack: false });
  } else {
    openWindow(s, 'DEPLOY', pending);
  }
}

function actPlaySpell(s, act) {
  const pid = s.active;
  const p = s.players[pid];
  const def = cardDef(s, act.card);
  takeFromHand(p, act.card);
  p.mana -= def.cost;
  ev(s, { e: 'PLAY_SPELL', player: pid, card: def.id, target: act.target || null, mana: p.mana });

  const pending = {
    kind: 'CAST',
    card: def.id,
    target: act.target || null,
    controller: pid,
    trigger: act.target || null, // §6: TRIGGER at a CAST window is the spell's target
  };
  if (def.keywords.includes('SEALED')) {
    ev(s, { e: 'SEALED', card: def.id });
    resumePending(s, pending, { counter: false, cancelAttack: false });
  } else {
    openWindow(s, 'CAST', pending);
  }
}

function actArm(s, act) {
  const pid = s.active;
  const p = s.players[pid];
  const def = cardDef(s, act.card);
  takeFromHand(p, act.card);
  p.guard -= def.cost; // pre-paid, immediately and irreversibly
  p.response = { card: def.id };
  ev(s, { e: 'ARM', player: pid, cost: def.cost, guard: p.guard });
  // Opens no window, ever (SPEC §2.2).
}

function actAttack(s, act) {
  const pid = s.active;
  const hit = findUnit(s, act.attacker);
  const att = hit.u;
  // The attack is spent at declaration. SPEC §6.3 requires attacks_used to be
  // incremented even when the strike is cancelled or the attacker dies in the
  // window; spending it up front is the simplest way to guarantee that.
  att.attacksUsed += 1;
  ev(s, { e: 'ATTACK_DECLARED', player: pid, attacker: att.uid, target: act.target });
  openWindow(s, 'STRIKE', {
    kind: 'STRIKE',
    attacker: att.uid,
    target: act.target,
    controller: pid,
    trigger: unitRef(att), // §6: TRIGGER at a STRIKE window is the attacking unit
  });
}

function actPass(s) {
  const aw = s.awaiting;
  s.awaiting = null;
  ev(s, { e: 'PASS', player: aw.player, window: aw.window });
  // The Response stays armed and response_used_this_turn is NOT set (§6.1).
  resumePending(s, aw.pending, { counter: false, cancelAttack: false });
}

function actFire(s, act) {
  const aw = s.awaiting;
  s.awaiting = null;
  const pid = aw.player;
  const p = s.players[pid];
  const def = cardDef(s, p.response.card);
  const mode = def.parsed.modes[act.mode];

  ev(s, {
    e: 'FIRE',
    player: pid,
    window: aw.window,
    card: def.id,
    mode: act.mode,
    label: mode.label,
  });

  const ctx = mkCtx(pid, {
    trigger: aw.trigger || null,
    bound: act.target || null,
    window: aw.window,
  });
  resolveStmts(s, ctx, mode.stmts);
  resolveDeaths(s);

  // Nothing may respond to a Response: no window is opened during the above.
  p.response = null;
  p.discard.push(def.id);
  p.responseUsedThisTurn = true;

  resumePending(s, aw.pending, { counter: ctx.counter, cancelAttack: ctx.cancelAttack });
}

// ---------------------------------------------------------------------------
// 13. Terminal state
// ---------------------------------------------------------------------------

export function isTerminal(state) {
  return state.result != null;
}

export function winner(state) {
  return state.result == null ? null : state.result;
}

// SPEC §10.1 writes isTerminal as returning null|'A'|'B'|'DRAW'; the task brief
// writes it as a boolean. `result` is the §10.1 shape under a non-colliding name.
export function result(state) {
  return state.result;
}

// ---------------------------------------------------------------------------
// 14. Deck legality (SPEC §1) — not enforced by createGame so that tests and
//     tooling can build synthetic decks. Call it explicitly for real matches.
// ---------------------------------------------------------------------------

export function validateDeck(deck, cardsInput) {
  const cards = normalizeCards(cardsInput);
  const errs = [];
  if (deck.length !== 30) errs.push(`deck size ${deck.length}, must be 30`);
  const counts = new Map();
  const factions = new Set();
  for (const id of deck) {
    const c = cards.byId[id];
    if (!c) {
      errs.push(`unknown card "${id}"`);
      continue;
    }
    counts.set(id, (counts.get(id) || 0) + 1);
    factions.add(c.faction);
  }
  for (const [id, n] of counts) if (n > 2) errs.push(`${n} copies of "${id}", max 2`);
  if (factions.size > 1) errs.push(`mixed factions: ${[...factions].join(', ')}`);
  return errs;
}

// A tiny convenience for building the starter decks out of cards.json.
export function buildDeck(listOrDeckDef, copies = 2) {
  const list = Array.isArray(listOrDeckDef) ? listOrDeckDef : listOrDeckDef.list;
  const out = [];
  for (const id of list) for (let i = 0; i < copies; i++) out.push(id);
  return out;
}
