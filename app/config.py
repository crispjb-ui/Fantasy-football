"""League configuration for the 2026-27 season.

10-team ESPN league, standard (non-PPR) scoring, $500 auction budgets,
16 roster spots + 1 IR, keepers (max 2 per team, max 1 per position,
cost = last year's auction price + $15), $200 season FAAB.

Everything here is a default; runtime overrides live in the SQLite
`meta` table and are merged in db.get_config().
"""

LEAGUE = {
    "season": 2026,
    "num_teams": 10,
    "auction_budget": 500,
    "faab_budget": 200,
    "keeper_surcharge": 15,
    "max_keepers_per_team": 2,
    "max_keepers_per_position": 1,
    # Starting lineup: QB/RB/RB/WR/WR/TE/FLEX/DST/K (FLEX = RB/WR/TE)
    "starters": {"QB": 1, "RB": 2, "WR": 2, "TE": 1, "FLEX": 1, "DST": 1, "K": 1},
    "flex_positions": ["RB", "WR", "TE"],
    "bench_spots": 6,
    "ir_spots": 1,
    # 9 starters + 6 bench = 15 auction-filled spots per team
    "roster_size": 15,
    # How the 6 bench spots are typically allocated per team in a 10-team
    # league. Drives replacement-level (bench demand) per position.
    "bench_allocation": {"QB": 0.6, "RB": 2.4, "WR": 2.4, "TE": 0.4, "K": 0.1, "DST": 0.1},
    # Weight given to market AAV (vs. our projection model) in blended values.
    "market_blend": 0.35,
    # Point-gap thresholds that start a new tier within a position.
    "tier_gaps": {"QB": 12.0, "RB": 11.0, "WR": 11.0, "TE": 11.0, "K": 6.0, "DST": 6.0},
    # Dampen K/DST value: projections overstate their edge because weekly
    # variance is huge — real auctions pay $1-3 for kickers and defenses.
    "position_value_mult": {"K": 0.12, "DST": 0.25},
    # Auto-refresh live data in the background when it's stale (hours).
    "auto_refresh": True,
    "auto_refresh_hours": 20,
    # Volatility priors: sigma/mean by position. Season CV drives floor/
    # ceiling pricing; weekly CV drives win-probability and start/sit tilts.
    "pos_season_cv": {"QB": 0.12, "RB": 0.22, "WR": 0.20, "TE": 0.24, "K": 0.15, "DST": 0.15},
    "pos_weekly_cv": {"QB": 0.35, "RB": 0.45, "WR": 0.52, "TE": 0.55, "K": 0.55, "DST": 0.55},
    # Fantasy regular season / playoff shape (overwritten by ESPN sync).
    "regular_season_weeks": 14,
    "playoff_teams": 4,
    # League temperament: how much this room overpays for elite players
    # relative to fair value (0.20 = elites go ~20% over sticker, funded by
    # discounts on the mid/low tiers). Auto-calibrated from imported
    # last-year draft prices; override in Data & Setup.
    "elite_premium": 0.20,
}

POSITIONS = ["QB", "RB", "WR", "TE", "K", "DST"]

# --- ESPN standard (non-PPR) scoring -------------------------------------
# Keys follow Sleeper's projection stat names so fetched projections can be
# scored directly.

SCORING_OFFENSE = {
    "pass_yd": 0.04,
    "pass_td": 4.0,
    "pass_int": -2.0,
    "pass_2pt": 2.0,
    "rush_yd": 0.1,
    "rush_td": 6.0,
    "rush_2pt": 2.0,
    "rec": 0.0,           # non-PPR
    "rec_yd": 0.1,
    "rec_td": 6.0,
    "rec_2pt": 2.0,
    "fum_lost": -2.0,
}

SCORING_KICKER = {
    "xpm": 1.0,
    "xpmiss": -1.0,
    "fgm_0_19": 3.0,
    "fgm_20_29": 3.0,
    "fgm_30_39": 3.0,
    "fgm_40_49": 4.0,
    "fgm_50p": 5.0,
    "fgmiss": -1.0,
}

SCORING_DST_COUNTING = {
    "sack": 1.0,
    "int": 2.0,
    "fum_rec": 2.0,
    "def_td": 6.0,
    "def_st_td": 6.0,
    "safe": 2.0,
    "blk_kick": 2.0,
}

# ESPN D/ST points-allowed tiers, applied per game.
DST_POINTS_ALLOWED_TIERS = [
    (0, 0, 5), (1, 6, 4), (7, 13, 3), (14, 17, 1),
    (18, 21, 0), (22, 27, -1), (28, 34, -3), (35, 45, -5), (46, 999, -7),
]

# ESPN D/ST yards-allowed tiers, applied per game.
DST_YARDS_ALLOWED_TIERS = [
    (0, 99, 5), (100, 199, 3), (200, 299, 2), (300, 349, 0),
    (350, 399, -1), (400, 449, -3), (450, 499, -5), (500, 9999, -6),
]

GAMES_PER_SEASON = 17
