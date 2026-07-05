"""Convert raw stat projections into ESPN standard (non-PPR) fantasy points."""

from . import config


def score_offense(stats: dict) -> float:
    return sum(stats.get(k, 0) * w for k, w in config.SCORING_OFFENSE.items())


def score_kicker(stats: dict) -> float:
    pts = sum(stats.get(k, 0) * w for k, w in config.SCORING_KICKER.items())
    # Some sources only give total field goals; approximate ESPN's distance
    # bonuses with the league-average distance mix (~3.35 pts/FG).
    if pts <= 0 and stats.get("fgm"):
        pts = stats.get("fgm", 0) * 3.35 + stats.get("xpm", 0) * 1.0
    return pts


def _tier_value(per_game: float, tiers) -> float:
    for lo, hi, val in tiers:
        if lo <= per_game <= hi:
            return float(val)
    return 0.0


def score_dst(stats: dict, games: int = config.GAMES_PER_SEASON) -> float:
    pts = sum(stats.get(k, 0) * w for k, w in config.SCORING_DST_COUNTING.items())
    # Points/yards allowed totals -> per-game tier value, scaled back up.
    # For weekly projections pass games=1 so the tiers apply directly.
    if stats.get("pts_allow") is not None:
        pa_per_game = stats["pts_allow"] / games
        pts += _tier_value(pa_per_game, config.DST_POINTS_ALLOWED_TIERS) * games
    if stats.get("yds_allow") is not None:
        ya_per_game = stats["yds_allow"] / games
        pts += _tier_value(ya_per_game, config.DST_YARDS_ALLOWED_TIERS) * games
    return pts


def score_player(position: str, stats: dict, games: int = config.GAMES_PER_SEASON) -> float:
    """Fantasy points for a player given projected stat totals over `games`."""
    if not stats:
        return 0.0
    if position == "K":
        pts = score_kicker(stats)
    elif position == "DST":
        pts = score_dst(stats, games)
    else:
        pts = score_offense(stats)
    # Fall back to the source's own standard-scoring total when we cannot
    # compute from raw stats (e.g. sparse projection rows).
    if pts == 0.0 and stats.get("pts_std"):
        pts = float(stats["pts_std"])
    return round(pts, 1)
