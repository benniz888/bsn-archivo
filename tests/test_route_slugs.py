"""One URL per archive player (PHASE_ROUTE_FIX). The app builds these slugs in JavaScript when
index/players.json lands (buildPlayerSlugs); this is the same rule in Python, run over the committed
index, so a data change that breaks uniqueness fails here before it reaches a browser. The real
curated pool (PINDEX) only exists at runtime; the browser checks in docs/session.md cover it exactly."""

import collections
import json
import re
import unicodedata

from src.wayback_cdx import REPO_ROOT

INDEX = REPO_ROOT / "web" / "data" / "index" / "players.json"
APP = REPO_ROOT / "app" / "bsn_archivo.html"

# The 11 shared slugs whose plain URL moved from the lowest id to the richest member.
CHANGED = {
    "alamo-candido-fret": 268, "carter-maurice": 12972, "farmer-anthony": 172, "figueroa-carlos": 2631,
    "ortiz-chris": 13057, "ramirez-francis": 710, "santana-edson": 990021, "smith-greg": 13199,
    "stewart-kebu": 1387, "vigo-castillo-julio": 1379, "williams-corey": 2738,
}


def slug(s):
    """Port of slug() in app/bsn_archivo.html."""
    s = unicodedata.normalize("NFD", str(s).lower())
    s = re.sub(r"[̀-ͯ]", "", s)
    s = re.sub(r"[«»\"'.]", "", s)
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def load():
    return json.loads(INDEX.read_text(encoding="utf-8"))


def urls_for(players):
    """(url -> id, id -> url, slug -> members, slug -> plain-slug owner), as buildPlayerSlugs() does."""
    groups = collections.defaultdict(list)
    for p in players:
        groups[slug(p["name"])].append(p)
    rank = lambda p: (-(p["career_seasons"] or 0), 0 if p["birth_year"] else 1, p["id"])
    by_url, by_id, owner = {}, {}, {}
    rest = []
    for s, members in groups.items():
        best = min(members, key=rank) if len(members) > 1 else members[0]
        owner[s] = best["id"]
        by_url[s], by_id[best["id"]] = best["id"], s
        rest += [(s, p) for p in members if p is not best]
    for s, p in rest:
        u = f"{s}-{p['id']}"
        while u in by_url:
            u += f"-{p['id']}"
        by_url[u], by_id[p["id"]] = p["id"], u
    return by_url, by_id, groups, owner


class TestUniqueUrls:
    def test_every_player_gets_its_own_url(self):
        players = load()
        by_url, by_id, _, _ = urls_for(players)
        assert len(players) == 3333
        assert len(by_url) == len(by_id) == len(players)
        assert all(by_url[by_id[p["id"]]] == p["id"] for p in players)

    def test_a_suffixed_url_never_equals_another_plain_slug(self):
        players = load()
        _, by_id, groups, _ = urls_for(players)
        plain = set(groups)
        suffixed = [u for i, u in by_id.items() if u not in plain]
        assert len(suffixed) == 61
        assert all(re.search(r"-\d+$", u) for u in suffixed)

    def test_57_shared_slugs_hold_118_players(self):
        _, _, groups, _ = urls_for(load())
        shared = {s: m for s, m in groups.items() if len(m) > 1}
        assert len(shared) == 57 and sum(len(m) for m in shared.values()) == 118

    def test_11_plain_urls_move_to_the_richest_member_and_46_stay(self):
        _, _, groups, owner = urls_for(load())
        shared = {s: m for s, m in groups.items() if len(m) > 1}
        moved = {s: owner[s] for s, m in shared.items() if owner[s] != min(p["id"] for p in m)}
        assert moved == CHANGED
        assert sum(1 for s, m in shared.items() if owner[s] == min(p["id"] for p in m)) == 46

    def test_every_other_member_is_slug_dash_id(self):
        _, by_id, groups, owner = urls_for(load())
        for s, members in groups.items():
            for p in members:
                assert by_id[p["id"]] == (s if p["id"] == owner[s] else f"{s}-{p['id']}")

    def test_the_richest_member_wins_on_career_rows_then_birth_year(self):
        players = {p["id"]: p for p in load()}
        # 2631 has 7 rows against 2 for 286; 1379 has 10 against 0 with the same birth date
        assert players[2631]["career_seasons"] > players[286]["career_seasons"]
        assert players[1379]["career_seasons"] > players[1378]["career_seasons"]
        # both have 0 rows: the one with a birth year takes the plain URL
        assert players[2738]["birth_year"] and not players[402]["birth_year"]
        assert players[402]["career_seasons"] == players[2738]["career_seasons"] == 0


class TestCuratedPool:
    """Best effort: the pool is assembled at runtime, so this reads the names written in the app file
    (a subset of it) and checks none of them takes an archive player's URL. The exact check (378 names)
    runs in the browser."""

    def test_no_pool_name_shares_a_slug_with_an_archive_player(self):
        text = APP.read_text(encoding="utf-8")
        lit = r'"((?:[^"\\]|\\.)*)"'
        names = set(re.findall(r'(?<![A-Za-z_])"?n"?\s*:\s*' + lit, text))
        names |= set(re.findall(r"(?<![A-Za-z_])n\s*:\s*'((?:[^'\\]|\\.)*)'", text))
        names |= set(re.findall(r"\[\s*\d+\s*,\s*" + lit, text))
        pool = {slug(n) for n in names if slug(n)}
        assert len(pool) > 300
        by_url, _, _, _ = urls_for(load())
        assert sorted(pool & set(by_url)) == []


class TestAppMatchesThisRule:
    def test_the_app_uses_the_same_ordering_and_route(self):
        text = APP.read_text(encoding="utf-8")
        assert "const rank=(a,b)=>(b.career_seasons||0)-(a.career_seasons||0)||(b.birth_year?1:0)-(a.birth_year?1:0)||a.id-b.id;" in text
        assert "const q=PSLUG&&PSLUG.get(c);" in text
        assert "PSLUG.set(u,p); USLUG.set(p.id,u);" in text
        assert "buildPlayerSlugs(); if(typeof refreshPlayerIndexArchive" in text
