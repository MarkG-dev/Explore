#!/usr/bin/env python3
"""Build the downloadable Hearthstone Constructed card database.

Scope: cards playable in RANKED CONSTRUCTED (Standard + Wild ladder). Excludes
Battlegrounds, Mercenaries, cosmetic hero skins, and non-collectible tokens.

Dating: a card's release date comes from card_history.json (its first appearance in
a dated game build), NOT from its current CARD_SET tag -- Blizzard re-buckets cards
between sets (Classic cards now report LEGACY; Core is re-curated yearly), so the
set tag mis-dates thousands of cards. Set tag is still recorded as `card_set`.

Outputs into --out:
  cards.json    full records, sorted by release date then cost then name
  cards.csv     flat table for spreadsheets
  cards.sqlite  indexed + FTS5 full-text search on name/text/flavor
  mechanics.json  keyword -> {count, first_date, cards[]}
  manifest.json   provenance + counts + exclusion report
"""
import argparse
import csv
import html
import json
import os
import re
import sqlite3
import sys
from collections import defaultdict, Counter
from xml.etree import ElementTree

from hearthstone.cardxml import CardXML
from hearthstone import enums

# --- Sets that are not Constructed ranked content ------------------------------
# Verified against the data: among *collectible* cards the only non-Constructed
# bucket is HERO_SKINS (740 cosmetic hero portraits). Battlegrounds (BACON_*) and
# Mercenaries (LETTUCE_*) content is entirely non-collectible, so the collectible
# filter already removes it -- no set-name matching needed for those.
#
# Two buckets that LOOK excludable but must be KEPT:
#   PLACEHOLDER_202204 - 654 real Core-set reprints (CORE_AT_003, CORE_AV_226, ...)
#                        of cards from rotated years. Playable in Wild.
#   DEMON_HUNTER_INITIATE - the 20 real Demon Hunter launch cards.
EXCLUDE_SETS = {"HERO_SKINS"}

# Boolean CardXML properties that represent a player-facing keyword/mechanic.
MECHANIC_PROPS = [
    "adapt", "avenge", "battlecry", "choose_one", "colossal", "combo", "corrupt",
    "deathrattle", "discover", "divine_shield", "dredge", "echo", "elusive",
    "fabled", "forge", "forgetful", "freeze", "immune", "inspire", "jade_golem",
    "lifesteal", "magnetic", "manathirst", "miniaturize", "outcast", "overheal",
    "overkill", "overload", "poisonous", "quest", "reborn", "ritual", "rush",
    "secret", "sidequest", "spare_part", "spell_damage", "spellburst",
    "start_of_game", "taunt", "titan", "topdeck", "tradeable", "twinspell",
    "venomous", "windfury",
]
EXTRA_TAG_MECHANICS = {
    "CHARGE": enums.GameTag.CHARGE,
    "STEALTH": enums.GameTag.STEALTH,
    "SILENCE": getattr(enums.GameTag, "SILENCE", None),
    "AURA": getattr(enums.GameTag, "AURA", None),
    "FRENZY": getattr(enums.GameTag, "FRENZY", None),
    "HONORABLEKILL": getattr(enums.GameTag, "HONORABLEKILL", None),
    "INFUSE": getattr(enums.GameTag, "INFUSE", None),
    "EXCAVATE": getattr(enums.GameTag, "EXCAVATE", None),
    "IMBUE": getattr(enums.GameTag, "IMBUE", None),
    "STARSHIP": getattr(enums.GameTag, "STARSHIP", None),
    "TOURIST": getattr(enums.GameTag, "TOURIST", None),
    "DORMANT": getattr(enums.GameTag, "DORMANT_AWAKEN_CONDITION_ENCHANT", None),
    "FINALE": getattr(enums.GameTag, "FINALE", None),
    "LOCATION": None,
}


def clean(s):
    """Normalise card rules text: unescape entities, drop markup and damage sigils."""
    if not s:
        return ""
    out = html.unescape(str(s))
    out = re.sub(r"<[^>]+>", "", out)          # <b>, <i>, <br/>, ...
    out = (out.replace("\n", " ")
              .replace("[x]", "")
              # the client uses "_" as a non-breaking space to stop card text
              # wrapping mid-phrase ("Restore #4 Health to ALL_minions.")
              .replace("_", " ")
              # "$" and "#" prefix numbers the client recolours for spell damage
              # and healing bonuses; the digit itself is the real value
              .replace("$", "")
              .replace("#", ""))
    return " ".join(out.split())


def parse_all(path):
    db = {}
    ctx = ElementTree.iterparse(path, events=("start", "end"))
    root = None
    for action, elem in ctx:
        if action == "start" and elem.tag == "CardDefs":
            root = elem
            continue
        if action == "end" and elem.tag == "Entity":
            c = CardXML.from_xml(elem)
            c.locale = "enUS"
            db[c.id] = c
            elem.clear()
            if root is not None:
                root.clear()
    return db


def mechanics_of(c):
    found = []
    for p in MECHANIC_PROPS:
        try:
            if getattr(c, p):
                found.append(p.upper())
        except Exception:
            pass
    for name, tag in EXTRA_TAG_MECHANICS.items():
        if tag is None:
            continue
        try:
            if c.tags.get(tag):
                found.append(name)
        except Exception:
            pass
    if c.type == enums.CardType.LOCATION:
        found.append("LOCATION")
    return sorted(set(found))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--carddefs", default="/tmp/claude-0/-home-user-Explore/"
                    "8c030bc7-79b3-5ce1-9234-e85134000e1b/scratchpad/hsdata-test/CardDefs.xml")
    ap.add_argument("--out", default="/home/user/Explore/hearthstone/data")
    ap.add_argument("--history", default="/home/user/Explore/hearthstone/data/card_history.json")
    args = ap.parse_args()

    print("[cards] parsing CardDefs.xml ...", file=sys.stderr)
    db = parse_all(args.carddefs)
    print(f"[cards] {len(db)} entities parsed", file=sys.stderr)

    hist = {}
    if os.path.exists(args.history):
        with open(args.history) as f:
            hist = json.load(f)
        print(f"[cards] history loaded for {len(hist)} cards", file=sys.stderr)
    else:
        print("[cards] WARNING: no card_history.json -- dates will be empty", file=sys.stderr)

    # Public set release dates, if a researched spine is available. These differ from
    # data_first_seen: card data ships to the client days-to-weeks before a set goes
    # live (e.g. GVG data appears 2014-12-04, public release 2014-12-08). We report
    # both rather than conflating them.
    set_release = {}
    spine_path = os.path.join(os.path.dirname(args.history), "sets_spine.json")
    if os.path.exists(spine_path):
        try:
            with open(spine_path) as f:
                spine = json.load(f)
            entries = spine.get("sets", spine) if isinstance(spine, dict) else spine
            if isinstance(entries, list):
                for e in entries:
                    if e.get("set_enum") and e.get("release_date"):
                        set_release[e["set_enum"]] = e["release_date"]
            print(f"[cards] set release dates loaded for {len(set_release)} sets", file=sys.stderr)
        except Exception as ex:
            print(f"[cards] could not read sets_spine.json: {ex}", file=sys.stderr)

    excluded = Counter()
    rows = []
    for c in db.values():
        if not c.collectible:
            excluded["not_collectible"] += 1
            continue
        setname = c.card_set.name
        if setname in EXCLUDE_SETS:
            excluded[f"set:{setname}"] += 1
            continue

        h = hist.get(c.id, {})
        changes = h.get("changes", [])
        balance_changes = [ch for ch in changes if ch.get("balance")]

        rows.append({
            "id": c.id,
            "dbf_id": c.dbf_id,
            "name": c.name,
            "text": clean(c.description),
            "flavor": clean(c.flavortext),
            "card_set": setname,
            # empirical: first dated client build containing this card
            "data_first_seen": h.get("first_date") or "",
            "release_build": h.get("first_build") or "",
            # researched public release date of the card's set, when known
            "set_release_date": set_release.get(setname, ""),
            "type": c.type.name,
            "card_class": c.card_class.name,
            "classes": [x.name for x in (c.classes or [])],
            "multi_class": bool(c.multiple_classes),
            "rarity": c.rarity.name,
            "cost": c.cost,
            "attack": c.atk,
            "health": c.health,
            "durability": c.durability,
            "armor": c.armor,
            "spell_school": c.spell_school.name if c.spell_school else "NONE",
            "races": [r.name for r in (c.races or [])],
            "mechanics": mechanics_of(c),
            "artist": c.artist or "",
            "legendary": bool(c.elite),
            "max_in_deck": c.max_count_in_deck,
            "craftable": bool(c.craftable),
            "n_changes": len(changes),
            "n_balance_changes": len(balance_changes),
            "balance_history": [
                {"date": ch["date"], "build": ch["build"],
                 "deltas": {k: ([clean(v[0]), clean(v[1])] if k == "text" else v)
                            for k, v in ch["deltas"].items()
                            if k in ("cost", "atk", "health", "durability", "armor", "text")}}
                for ch in balance_changes
            ],
        })

    # sort by release date, then cost, then name
    rows.sort(key=lambda r: (r["data_first_seen"] or "9999", r["cost"] or 0, r["name"] or ""))

    # --- reprint detection -----------------------------------------------------
    # The same card exists under several CardIDs: the original printing plus Core /
    # Legacy / Vanilla re-buckets (Fireball is CS2_029 in LEGACY and also appears as
    # a CORE_* reprint). All are genuine client cards, so we keep every row, but we
    # mark which is the original so consumers can collapse to unique cards.
    groups = defaultdict(list)
    for r in rows:
        key = (r["name"].strip().lower(), r["card_class"], r["type"])
        groups[key].append(r)
    for key, members in groups.items():
        # rows are already release-date ordered, so members[0] is the earliest
        original = members[0]
        for r in members:
            r["n_printings"] = len(members)
            r["is_reprint"] = r is not original
            r["original_id"] = original["id"]
            r["printings"] = [m["id"] for m in members]
    n_unique = len(groups)
    n_reprints = sum(1 for r in rows if r["is_reprint"])

    os.makedirs(args.out, exist_ok=True)

    # ---- JSON ----
    with open(os.path.join(args.out, "cards.json"), "w") as f:
        json.dump(rows, f, separators=(",", ":"))

    # ---- lite index for the web browser (columnar, small over the wire) ----
    # Same rows, minus flavor text and per-card change history, emitted as parallel
    # arrays so the payload stays a fraction of cards.json.
    lite_keys = ["id", "name", "text", "card_set", "data_first_seen", "type",
                 "card_class", "rarity", "cost", "attack", "health", "mechanics",
                 "races", "spell_school", "is_reprint", "n_balance_changes",
                 "n_printings", "legendary"]
    lite = {
        "keys": lite_keys,
        "rows": [
            [("|".join(r[k]) if isinstance(r[k], list)
              else (int(r[k]) if isinstance(r[k], bool) else r[k]))
             for k in lite_keys]
            for r in rows
        ],
    }
    with open(os.path.join(args.out, "cards_lite.json"), "w") as f:
        json.dump(lite, f, separators=(",", ":"))

    # ---- changelog: every balance change, flat and date-ordered ----
    changelog = []
    for r in rows:
        for ch in r["balance_history"]:
            changelog.append({
                "date": ch["date"], "build": ch["build"], "card_id": r["id"],
                "name": r["name"], "card_set": r["card_set"],
                "card_class": r["card_class"], "deltas": ch["deltas"],
            })
    changelog.sort(key=lambda c: (c["date"], c["name"]))
    with open(os.path.join(args.out, "changelog.json"), "w") as f:
        json.dump(changelog, f, separators=(",", ":"))

    # ---- CSV ----
    flat_cols = ["id", "dbf_id", "name", "text", "card_set", "data_first_seen",
                 "set_release_date", "type",
                 "card_class", "classes", "rarity", "cost", "attack", "health",
                 "durability", "armor", "spell_school", "races", "mechanics",
                 "artist", "legendary", "n_balance_changes", "is_reprint",
                 "n_printings", "original_id", "flavor"]
    with open(os.path.join(args.out, "cards.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=flat_cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            rr = dict(r)
            for k in ("classes", "races", "mechanics"):
                rr[k] = "|".join(rr[k])
            w.writerow(rr)

    # ---- SQLite ----
    dbpath = os.path.join(args.out, "cards.sqlite")
    if os.path.exists(dbpath):
        os.remove(dbpath)
    con = sqlite3.connect(dbpath)
    con.executescript("""
        CREATE TABLE cards (
          id TEXT PRIMARY KEY, dbf_id INTEGER, name TEXT, text TEXT, flavor TEXT,
          card_set TEXT, data_first_seen TEXT, release_build TEXT,
          set_release_date TEXT, type TEXT,
          card_class TEXT, classes TEXT, multi_class INTEGER, rarity TEXT,
          cost INTEGER, attack INTEGER, health INTEGER, durability INTEGER,
          armor INTEGER, spell_school TEXT, races TEXT, mechanics TEXT,
          artist TEXT, legendary INTEGER, max_in_deck INTEGER, craftable INTEGER,
          n_changes INTEGER, n_balance_changes INTEGER,
          is_reprint INTEGER, n_printings INTEGER, original_id TEXT
        );
        CREATE TABLE card_mechanics (card_id TEXT, mechanic TEXT);
        CREATE TABLE balance_changes (
          card_id TEXT, name TEXT, date TEXT, build TEXT,
          field TEXT, old_value TEXT, new_value TEXT
        );
        CREATE INDEX idx_set     ON cards(card_set);
        CREATE INDEX idx_release ON cards(data_first_seen);
        CREATE INDEX idx_class   ON cards(card_class);
        CREATE INDEX idx_cost    ON cards(cost);
        CREATE INDEX idx_rarity  ON cards(rarity);
        CREATE INDEX idx_mech    ON card_mechanics(mechanic);
        CREATE INDEX idx_bc_card ON balance_changes(card_id);
        CREATE INDEX idx_bc_date ON balance_changes(date);
        CREATE INDEX idx_reprint ON cards(is_reprint);
    """)
    for r in rows:
        con.execute(
            "INSERT INTO cards VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (r["id"], r["dbf_id"], r["name"], r["text"], r["flavor"], r["card_set"],
             r["data_first_seen"], r["release_build"], r["set_release_date"],
             r["type"], r["card_class"],
             "|".join(r["classes"]), int(r["multi_class"]), r["rarity"], r["cost"],
             r["attack"], r["health"], r["durability"], r["armor"], r["spell_school"],
             "|".join(r["races"]), "|".join(r["mechanics"]), r["artist"],
             int(r["legendary"]), r["max_in_deck"], int(r["craftable"]),
             r["n_changes"], r["n_balance_changes"],
             int(r["is_reprint"]), r["n_printings"], r["original_id"]))
        for m in r["mechanics"]:
            con.execute("INSERT INTO card_mechanics VALUES (?,?)", (r["id"], m))
        for ch in r["balance_history"]:
            for field, (old, new) in ch["deltas"].items():
                con.execute("INSERT INTO balance_changes VALUES (?,?,?,?,?,?,?)",
                            (r["id"], r["name"], ch["date"], ch["build"],
                             field, str(old), str(new)))
    con.executescript("""
        CREATE VIRTUAL TABLE cards_fts USING fts5(
          id UNINDEXED, name, text, flavor, content=''
        );
    """)
    for r in rows:
        con.execute("INSERT INTO cards_fts (id,name,text,flavor) VALUES (?,?,?,?)",
                    (r["id"], r["name"], r["text"], r["flavor"]))
    con.commit()
    con.close()

    # ---- mechanics index ----
    mech = defaultdict(lambda: {"count": 0, "first_date": "9999", "cards": []})
    for r in rows:
        for m in r["mechanics"]:
            e = mech[m]
            e["count"] += 1
            if r["data_first_seen"] and r["data_first_seen"] < e["first_date"]:
                e["first_date"] = r["data_first_seen"]
            e["cards"].append(r["id"])
    mech_out = {k: v for k, v in sorted(mech.items(), key=lambda kv: -kv[1]["count"])}
    with open(os.path.join(args.out, "mechanics_index.json"), "w") as f:
        json.dump(mech_out, f, indent=2)

    # ---- manifest ----
    by_set = Counter(r["card_set"] for r in rows)
    by_year = Counter((r["data_first_seen"] or "?")[:4] for r in rows)
    manifest = {
        "source": "HearthSim/hsdata CardDefs.xml (datamined from the Hearthstone client)",
        "source_url": "https://github.com/HearthSim/hsdata",
        "scope": "Collectible Constructed cards for ranked ladder (Standard + Wild). "
                 "Excludes Battlegrounds, Mercenaries, Tavern Brawl-only content, "
                 "cosmetic hero skins, and non-collectible tokens.",
        "dating_method": "Each card's data_first_seen is the date of the earliest dated "
                         "game build in which the card appears in CardDefs.xml. Current "
                         "CARD_SET tags are unreliable for dating because Blizzard "
                         "re-buckets cards (Classic -> LEGACY, yearly Core re-curation).",
        "n_cards": len(rows),
        "n_unique_cards": n_unique,
        "n_reprints": n_reprints,
        "reprint_note": "The same card can exist under several CardIDs (original "
                        "printing plus Core/Legacy/Vanilla re-buckets). Every printing "
                        "is kept as its own row; is_reprint=0 selects the "
                        f"{n_unique} unique cards.",
        "n_entities_in_source": len(db),
        "n_with_balance_changes": sum(1 for r in rows if r["n_balance_changes"]),
        "n_balance_change_events": sum(r["n_balance_changes"] for r in rows),
        "cards_by_set": dict(by_set.most_common()),
        "cards_by_release_year": dict(sorted(by_year.items())),
        "excluded": dict(excluded.most_common()),
        "files": {
            "cards.json": "full records incl. per-card balance change history",
            "cards.csv": "flat table (list columns pipe-delimited)",
            "cards.sqlite": "indexed SQLite + FTS5 search; tables: cards, card_mechanics, balance_changes",
            "mechanics_index.json": "mechanic -> count, first appearance, card ids",
        },
    }
    with open(os.path.join(args.out, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"[cards] wrote {len(rows)} constructed cards", file=sys.stderr)
    print(f"[cards] balance change events: {manifest['n_balance_change_events']}", file=sys.stderr)
    print(f"[cards] by year: {manifest['cards_by_release_year']}", file=sys.stderr)
    print(f"[cards] excluded: {dict(list(excluded.most_common())[:12])}", file=sys.stderr)


if __name__ == "__main__":
    main()
