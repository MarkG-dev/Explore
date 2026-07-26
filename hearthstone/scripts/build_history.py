#!/usr/bin/env python3
"""Reconstruct Hearthstone's full card history from the hsdata build snapshots.

Why this exists
---------------
A card's *current* CARD_SET tag is not a reliable release date. Blizzard re-buckets
cards between sets over time (original Classic cards now report LEGACY; the Core set
is re-curated every year). So sorting a card database by its current set mis-dates
thousands of cards.

Instead we walk all ~320 dated build snapshots of CardDefs.xml in chronological
order and record, per card, the first build it ever appeared in. That is empirical
ground truth from the game client. The same pass yields the balance changelog:
every cost / attack / health / durability / armor / text change a card ever received,
with the build and date it happened.

Outputs (into --out):
  card_history.json   {card_id: {first_build, first_date, last_build, last_date, changes:[...]}}
  sets_first_seen.json {set_enum: {set_id, first_build, first_date, n_cards_at_first_build}}
  build_index.json    [{build, date, n_entities, n_collectible}]
"""
import argparse
import bz2
import json
import os
import pickle
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor

REPO_DEFAULT = "/tmp/claude-0/-home-user-Explore/8c030bc7-79b3-5ce1-9234-e85134000e1b/scratchpad/hsdata-full"

# --- GameTag ids we fingerprint ------------------------------------------------
T_COST, T_ATK, T_HEALTH, T_DURABILITY, T_ARMOR = 48, 47, 45, 187, 292
T_CARDNAME, T_CARDTEXT = 185, 184
T_CARDSET, T_COLLECTIBLE, T_RARITY, T_CLASS, T_CARDTYPE = 183, 321, 203, 199, 202

ENTITY_RE = re.compile(rb'<Entity\s+CardID="([^"]+)"[^>]*>(.*?)</Entity>', re.S)


def _int_tag(body, enum_id):
    m = re.search(rb'enumID="%d"[^>]*value="(-?\d+)"' % enum_id, body)
    return int(m.group(1)) if m else None


def _loc_tag(body, enum_id):
    """Extract the enUS value of a LocString tag."""
    m = re.search(
        rb'enumID="%d"[^>]*type="LocString"\s*>(.*?)</Tag>' % enum_id, body, re.S
    )
    if not m:
        return None
    en = re.search(rb"<enUS>(.*?)</enUS>", m.group(1), re.S)
    return en.group(1).decode("utf-8", "replace") if en else None


def fingerprint_build(args):
    """Return (tag, date, {card_id: tuple}, n_entities, n_collectible)."""
    tag, date, repo = args
    p = subprocess.run(
        ["git", "-C", repo, "show", f"{tag}:CardDefs.xml"],
        capture_output=True,
    )
    if p.returncode != 0:
        return tag, date, None, 0, 0
    data = p.stdout
    fp = {}
    n_coll = 0
    for m in ENTITY_RE.finditer(data):
        cid = m.group(1).decode()
        body = m.group(2)
        coll = _int_tag(body, T_COLLECTIBLE) == 1
        if coll:
            n_coll += 1
        name = _loc_tag(body, T_CARDNAME)
        text = _loc_tag(body, T_CARDTEXT)
        fp[cid] = (
            name,
            _int_tag(body, T_COST),
            _int_tag(body, T_ATK),
            _int_tag(body, T_HEALTH),
            _int_tag(body, T_DURABILITY),
            _int_tag(body, T_ARMOR),
            _int_tag(body, T_CARDSET),
            1 if coll else 0,
            _int_tag(body, T_RARITY),
            _int_tag(body, T_CLASS),
            _int_tag(body, T_CARDTYPE),
            # store the text itself (normalised) so we can diff wording changes
            re.sub(r"\s+", " ", text).strip() if text else None,
        )
    return tag, date, fp, len(fp), n_coll


FIELDS = ["name", "cost", "atk", "health", "durability", "armor",
          "card_set", "collectible", "rarity", "card_class", "card_type", "text"]
# fields whose changes are balance-relevant (vs cosmetic re-bucketing)
BALANCE_FIELDS = {"cost", "atk", "health", "durability", "armor", "text"}


def build_list(repo):
    out = subprocess.run(
        ["git", "-C", repo, "for-each-ref", "--sort=creatordate",
         "--format=%(refname:short)\t%(creatordate:short)", "refs/tags"],
        capture_output=True, check=True,
    ).stdout.decode()
    rows = []
    for line in out.splitlines():
        if "\t" in line:
            tag, date = line.split("\t", 1)
            rows.append((tag.strip(), date.strip()))
    seen = set()
    uniq = []
    for tag, date in rows:
        if tag not in seen:
            seen.add(tag)
            uniq.append((tag, date))
    return uniq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO_DEFAULT)
    ap.add_argument("--out", default="/home/user/Explore/hearthstone/data")
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0, help="debug: only N builds")
    ap.add_argument("--cache", default="")
    args = ap.parse_args()

    builds = build_list(args.repo)
    if args.limit:
        builds = builds[: args.limit]
    print(f"[history] {len(builds)} builds: {builds[0][1]} .. {builds[-1][1]}", file=sys.stderr)

    history = {}       # card_id -> record
    sets_first = {}    # set_id -> record
    build_index = []
    prev = None

    tasks = [(t, d, args.repo) for t, d in builds]
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for i, (tag, date, fp, n_ent, n_coll) in enumerate(
            ex.map(fingerprint_build, tasks, chunksize=1)
        ):
            if fp is None:
                print(f"  !! build {tag} unreadable, skipped", file=sys.stderr)
                continue
            build_index.append({"build": tag, "date": date,
                                "n_entities": n_ent, "n_collectible": n_coll})

            for cid, vals in fp.items():
                rec = history.get(cid)
                if rec is None:
                    history[cid] = {
                        "first_build": tag, "first_date": date,
                        "last_build": tag, "last_date": date,
                        "first_name": vals[0],
                        "first_collectible": vals[7],
                        "changes": [],
                    }
                    sid = vals[6]
                    if sid is not None and vals[7] == 1 and sid not in sets_first:
                        sets_first[sid] = {"set_id": sid, "first_build": tag,
                                           "first_date": date,
                                           "n_cards_at_first_build": 0}
                else:
                    rec["last_build"] = tag
                    rec["last_date"] = date

            # diff against previous build
            if prev is not None:
                for cid, vals in fp.items():
                    old = prev.get(cid)
                    if old is None or old == vals:
                        continue
                    deltas = {}
                    for idx, fname in enumerate(FIELDS):
                        if old[idx] != vals[idx]:
                            deltas[fname] = [old[idx], vals[idx]]
                    if not deltas:
                        continue
                    history[cid]["changes"].append({
                        "build": tag, "date": date,
                        "balance": any(k in BALANCE_FIELDS for k in deltas),
                        "deltas": deltas,
                    })
            prev = fp
            if i % 25 == 0:
                print(f"  ...{i}/{len(builds)} ({date}) cards={len(history)}", file=sys.stderr)

    # count cards per set at that set's first build
    for sid, rec in sets_first.items():
        rec["n_cards_at_first_build"] = sum(
            1 for h in history.values()
            if h["first_build"] == rec["first_build"] and h["first_collectible"] == 1
        )

    from hearthstone.enums import CardSet
    named_sets = {}
    for sid, rec in sorted(sets_first.items(), key=lambda kv: kv[1]["first_date"]):
        try:
            nm = CardSet(sid).name
        except ValueError:
            nm = f"UNKNOWN_{sid}"
        named_sets[nm] = rec

    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, "card_history.json"), "w") as f:
        json.dump(history, f, separators=(",", ":"))
    with open(os.path.join(args.out, "sets_first_seen.json"), "w") as f:
        json.dump(named_sets, f, indent=2)
    with open(os.path.join(args.out, "build_index.json"), "w") as f:
        json.dump(build_index, f, indent=2)

    n_changes = sum(len(h["changes"]) for h in history.values())
    n_bal = sum(1 for h in history.values() for c in h["changes"] if c["balance"])
    print(f"[history] cards tracked      : {len(history)}", file=sys.stderr)
    print(f"[history] total change events: {n_changes}", file=sys.stderr)
    print(f"[history] balance changes    : {n_bal}", file=sys.stderr)
    print(f"[history] sets dated         : {len(named_sets)}", file=sys.stderr)
    for nm, rec in named_sets.items():
        print(f"    {rec['first_date']}  {nm:32s} build={rec['first_build']}")


if __name__ == "__main__":
    main()
