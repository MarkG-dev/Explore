#!/usr/bin/env python3
"""Shard the full HearthPwn deck archive into 4 committable gzip parts, losslessly.

The normalised archive is ~307 MB of NDJSON — over GitHub's 100 MB per-file hard
limit. Rather than drop it (losing 346,232 real decklists), split it into 4 gzipped
shards of roughly 9 MB each and commit all of them, so the complete archive lives in
the repo.

Losslessness is *proved*, not asserted: a manifest records the SHA-256 and line count
of the original, of each shard, and of the reassembled file, and `--verify` rebuilds
the archive and checks the digest end to end.

Usage:
    python3 shard_decks.py                # split + write manifest
    python3 shard_decks.py --verify       # rebuild from shards and check SHA-256
    python3 shard_decks.py --restore OUT  # just reassemble to OUT
"""
import argparse
import gzip
import hashlib
import json
import os
import sys

DEFAULT_SRC = ("/home/user/Explore/hearthstone/data/research/"
               "decks_NJacobsohn-Hearthstone-Data-Analysis.ndjson")
SHARD_DIR = "/home/user/Explore/hearthstone/data/research/decks_hearthpwn_shards"
N_SHARDS = 4
BASENAME = "decks_hearthpwn.part{:02d}.ndjson.gz"
MANIFEST = "manifest.json"


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def sha256_lines(path_or_stream_iter):
    h = hashlib.sha256()
    n = 0
    for line in path_or_stream_iter:
        h.update(line)
        n += 1
    return h.hexdigest(), n


def split(src, outdir, n_shards):
    if not os.path.exists(src):
        print(f"[shard] source missing: {src}", file=sys.stderr)
        print("[shard] regenerate it per data/research/decksets_README.md", file=sys.stderr)
        return 1
    os.makedirs(outdir, exist_ok=True)

    total_lines = 0
    with open(src, "rb") as f:
        for _ in f:
            total_lines += 1
    per = -(-total_lines // n_shards)  # ceil
    src_sha = sha256_file(src)
    src_bytes = os.path.getsize(src)
    print(f"[shard] source: {total_lines:,} lines, {src_bytes/1048576:.1f} MB", file=sys.stderr)
    print(f"[shard] {n_shards} shards of up to {per:,} lines each", file=sys.stderr)

    shards = []
    with open(src, "rb") as f:
        for i in range(n_shards):
            name = BASENAME.format(i + 1)
            path = os.path.join(outdir, name)
            written = 0
            hsh = hashlib.sha256()
            with gzip.open(path, "wb", compresslevel=9) as g:
                for _ in range(per):
                    line = f.readline()
                    if not line:
                        break
                    g.write(line)
                    hsh.update(line)
                    written += 1
            shards.append({
                "file": name,
                "lines": written,
                "gz_bytes": os.path.getsize(path),
                "sha256_of_lines": hsh.hexdigest(),
            })
            print(f"[shard]   {name}: {written:,} lines, "
                  f"{os.path.getsize(path)/1048576:.1f} MB gz", file=sys.stderr)
            if written == 0:
                os.remove(path)
                shards.pop()

    man = {
        "description": "Lossless 4-way gzip shard of the normalised HearthPwn deck "
                       "archive (346,232 ranked+unranked decklists, 2013-05 to 2017-03). "
                       "Concatenating the shards in order reproduces the original file "
                       "byte for byte.",
        "original_file": os.path.basename(src),
        "original_lines": total_lines,
        "original_bytes": src_bytes,
        "original_sha256": src_sha,
        "n_shards": len(shards),
        "shards": shards,
        "reassemble": "python3 scripts/shard_decks.py --restore out.ndjson",
        "reassemble_shell": "zcat decks_hearthpwn.part*.ndjson.gz > out.ndjson",
    }
    with open(os.path.join(outdir, MANIFEST), "w") as f:
        json.dump(man, f, indent=2)
    total_gz = sum(s["gz_bytes"] for s in shards)
    print(f"[shard] wrote {len(shards)} shards, {total_gz/1048576:.1f} MB total "
          f"({total_gz/src_bytes*100:.1f}% of raw)", file=sys.stderr)
    return 0


def iter_shards(outdir):
    with open(os.path.join(outdir, MANIFEST)) as f:
        man = json.load(f)
    for s in man["shards"]:
        with gzip.open(os.path.join(outdir, s["file"]), "rb") as g:
            for line in g:
                yield line


def restore(outdir, dest):
    n = 0
    h = hashlib.sha256()
    with open(dest, "wb") as out:
        for line in iter_shards(outdir):
            out.write(line)
            h.update(line)
            n += 1
    return h.hexdigest(), n


def verify(outdir):
    with open(os.path.join(outdir, MANIFEST)) as f:
        man = json.load(f)
    tmp = os.path.join(outdir, "_verify.tmp")
    try:
        sha, n = restore(outdir, tmp)
        file_sha = sha256_file(tmp)
        ok_lines = n == man["original_lines"]
        ok_sha = file_sha == man["original_sha256"]
        print(f"[verify] lines {n:,} vs {man['original_lines']:,}  -> {'OK' if ok_lines else 'MISMATCH'}")
        print(f"[verify] sha256 {file_sha[:16]}… vs {man['original_sha256'][:16]}…  -> {'OK' if ok_sha else 'MISMATCH'}")
        if ok_lines and ok_sha:
            print("[verify] LOSSLESS: shards reproduce the original byte for byte.")
            return 0
        print("[verify] FAILED", file=sys.stderr)
        return 1
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=DEFAULT_SRC)
    ap.add_argument("--dir", default=SHARD_DIR)
    ap.add_argument("--shards", type=int, default=N_SHARDS)
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--restore", metavar="DEST")
    a = ap.parse_args()
    if a.verify:
        return verify(a.dir)
    if a.restore:
        sha, n = restore(a.dir, a.restore)
        print(f"[restore] {n:,} lines -> {a.restore}", file=sys.stderr)
        return 0
    return split(a.src, a.dir, a.shards)


if __name__ == "__main__":
    raise SystemExit(main())
