"""Bundled sample player pool (2026 season, plausible projections).

This exists so the app works instantly — including full draft dry-runs —
before you refresh real data from Sleeper/FantasyPros on draft week.
Sample players use the id prefix "smpl:"; a successful live refresh
removes them (unless a logged pick references one).

Tuples below are season stat projections:
  QB : (name, team, pass_yd, pass_td, int, rush_yd, rush_td)
  RB : (name, team, rush_yd, rush_td, rec, rec_yd, rec_td)
  WR : (name, team, rec, rec_yd, rec_td, rush_yd)
  TE : (name, team, rec, rec_yd, rec_td)
  K  : (name, team, fg_short, fg_40, fg_50, xpm)   [made FGs by distance band]
  DST: (name, sack, int, fum_rec, td, pts_allow, yds_allow)
"""

from . import db, scoring
from .data_sources import norm_name

QBS = [
    ("Josh Allen", "BUF", 4250, 32, 11, 540, 11),
    ("Lamar Jackson", "BAL", 3950, 33, 7, 780, 5),
    ("Jayden Daniels", "WAS", 3900, 27, 9, 750, 7),
    ("Jalen Hurts", "PHI", 3500, 22, 8, 610, 12),
    ("Joe Burrow", "CIN", 4700, 37, 10, 190, 3),
    ("Patrick Mahomes", "KC", 4250, 30, 10, 380, 3),
    ("Baker Mayfield", "TB", 4350, 33, 12, 320, 3),
    ("Kyler Murray", "ARI", 3850, 25, 9, 520, 5),
    ("Justin Herbert", "LAC", 4100, 27, 8, 350, 4),
    ("Bo Nix", "DEN", 3900, 27, 10, 420, 5),
    ("Caleb Williams", "CHI", 3900, 25, 9, 450, 4),
    ("Drake Maye", "NE", 3850, 25, 9, 480, 4),
    ("Dak Prescott", "DAL", 4300, 29, 11, 180, 2),
    ("Jordan Love", "GB", 4000, 28, 10, 160, 2),
    ("Justin Fields", "NYJ", 3200, 18, 8, 750, 7),
    ("C.J. Stroud", "HOU", 3900, 24, 9, 220, 2),
    ("Brock Purdy", "SF", 4000, 26, 9, 280, 3),
    ("Jared Goff", "DET", 4300, 29, 10, 40, 1),
    ("Trevor Lawrence", "JAX", 3800, 23, 10, 280, 3),
    ("Tua Tagovailoa", "MIA", 3900, 25, 10, 60, 1),
    ("J.J. McCarthy", "MIN", 3650, 24, 11, 250, 3),
    ("Michael Penix Jr.", "ATL", 3800, 23, 10, 120, 2),
    ("Bryce Young", "CAR", 3650, 22, 9, 260, 4),
    ("Matthew Stafford", "LAR", 4000, 27, 10, 30, 0),
    ("Sam Darnold", "SEA", 3700, 22, 11, 150, 1),
    ("Geno Smith", "LV", 3800, 22, 11, 180, 2),
]

RBS = [
    ("Bijan Robinson", "ATL", 1450, 12, 60, 500, 2),
    ("Jahmyr Gibbs", "DET", 1250, 12, 55, 480, 3),
    ("Saquon Barkley", "PHI", 1500, 12, 30, 250, 2),
    ("Ashton Jeanty", "LV", 1350, 10, 45, 340, 2),
    ("Christian McCaffrey", "SF", 1100, 9, 65, 520, 3),
    ("De'Von Achane", "MIA", 950, 8, 65, 540, 3),
    ("Derrick Henry", "BAL", 1400, 12, 15, 120, 1),
    ("Jonathan Taylor", "IND", 1300, 11, 35, 270, 1),
    ("Josh Jacobs", "GB", 1250, 11, 35, 280, 1),
    ("Bucky Irving", "TB", 1150, 8, 50, 400, 2),
    ("Kyren Williams", "LAR", 1200, 11, 30, 230, 1),
    ("James Cook", "BUF", 1150, 10, 30, 240, 2),
    ("Chase Brown", "CIN", 1100, 9, 45, 350, 2),
    ("Breece Hall", "NYJ", 1000, 7, 50, 400, 2),
    ("Kenneth Walker", "SEA", 1000, 9, 35, 280, 1),
    ("Omarion Hampton", "LAC", 1050, 8, 40, 310, 1),
    ("Chuba Hubbard", "CAR", 1050, 8, 40, 300, 1),
    ("James Conner", "ARI", 1000, 8, 40, 320, 1),
    ("TreVeyon Henderson", "NE", 850, 6, 50, 420, 2),
    ("Quinshon Judkins", "CLE", 1000, 8, 30, 220, 1),
    ("RJ Harvey", "DEN", 850, 7, 40, 330, 2),
    ("Alvin Kamara", "NO", 850, 6, 55, 420, 1),
    ("David Montgomery", "DET", 850, 8, 30, 220, 1),
    ("Joe Mixon", "HOU", 950, 8, 30, 220, 1),
    ("Aaron Jones", "MIN", 800, 5, 45, 350, 1),
    ("D'Andre Swift", "CHI", 850, 6, 40, 300, 1),
    ("Kaleb Johnson", "PIT", 900, 7, 25, 180, 1),
    ("Tony Pollard", "TEN", 950, 6, 35, 250, 1),
    ("Isiah Pacheco", "KC", 800, 6, 30, 220, 1),
    ("Rhamondre Stevenson", "NE", 750, 6, 30, 220, 1),
    ("Brian Robinson", "SF", 750, 6, 20, 140, 0),
    ("Jaylen Warren", "PIT", 750, 5, 40, 300, 1),
    ("Zach Charbonnet", "SEA", 700, 6, 30, 230, 1),
    ("Javonte Williams", "DAL", 800, 6, 30, 210, 1),
    ("J.K. Dobbins", "DEN", 750, 6, 20, 150, 1),
    ("Tyrone Tracy", "NYG", 700, 5, 35, 250, 1),
    ("Najee Harris", "LAC", 700, 5, 25, 170, 0),
    ("Cam Skattebo", "NYG", 750, 6, 30, 220, 1),
    ("Jordan Mason", "MIN", 700, 5, 15, 100, 0),
    ("Tank Bigsby", "JAX", 700, 6, 10, 70, 0),
    ("Rachaad White", "TB", 550, 4, 40, 300, 1),
    ("Braelon Allen", "NYJ", 600, 5, 15, 110, 0),
    ("Trey Benson", "ARI", 600, 4, 20, 150, 1),
    ("Jerome Ford", "CLE", 500, 4, 30, 230, 1),
    ("Bhayshul Tuten", "JAX", 550, 4, 20, 160, 1),
    ("Ray Davis", "BUF", 500, 4, 15, 120, 1),
    ("Dylan Sampson", "CLE", 450, 3, 30, 230, 1),
    ("Austin Ekeler", "WAS", 400, 3, 35, 280, 1),
    ("Nick Chubb", "HOU", 550, 4, 10, 70, 0),
    ("Justice Hill", "BAL", 350, 2, 30, 250, 1),
    ("Roschon Johnson", "CHI", 350, 3, 20, 150, 0),
    ("Devin Neal", "NO", 450, 3, 20, 140, 0),
    ("Kareem Hunt", "KC", 450, 4, 15, 100, 0),
    ("Ollie Gordon", "MIA", 400, 4, 10, 80, 0),
    ("Kendre Miller", "NO", 400, 3, 10, 80, 0),
]

WRS = [
    ("Ja'Marr Chase", "CIN", 115, 1550, 12, 20),
    ("Justin Jefferson", "MIN", 105, 1500, 9, 15),
    ("CeeDee Lamb", "DAL", 105, 1400, 9, 40),
    ("Puka Nacua", "LAR", 105, 1380, 8, 60),
    ("Malik Nabers", "NYG", 100, 1350, 8, 20),
    ("Amon-Ra St. Brown", "DET", 105, 1280, 9, 15),
    ("Nico Collins", "HOU", 90, 1300, 8, 10),
    ("Brian Thomas Jr.", "JAX", 90, 1280, 8, 25),
    ("A.J. Brown", "PHI", 85, 1250, 8, 5),
    ("Drake London", "ATL", 95, 1250, 8, 5),
    ("Ladd McConkey", "LAC", 90, 1150, 7, 20),
    ("Tee Higgins", "CIN", 80, 1100, 9, 0),
    ("Terry McLaurin", "WAS", 80, 1080, 9, 5),
    ("Marvin Harrison Jr.", "ARI", 80, 1100, 8, 0),
    ("Garrett Wilson", "NYJ", 85, 1080, 7, 10),
    ("Rashee Rice", "KC", 90, 1050, 7, 20),
    ("Jaxon Smith-Njigba", "SEA", 90, 1100, 6, 15),
    ("Davante Adams", "LAR", 80, 1050, 8, 0),
    ("Tyreek Hill", "MIA", 80, 1080, 7, 25),
    ("Mike Evans", "TB", 75, 1050, 9, 0),
    ("DJ Moore", "CHI", 85, 1020, 6, 40),
    ("DK Metcalf", "PIT", 70, 1000, 8, 10),
    ("Zay Flowers", "BAL", 80, 1020, 6, 30),
    ("Courtland Sutton", "DEN", 75, 1000, 7, 0),
    ("DeVonta Smith", "PHI", 75, 980, 6, 5),
    ("Xavier Worthy", "KC", 75, 950, 6, 50),
    ("Jameson Williams", "DET", 65, 1000, 6, 40),
    ("George Pickens", "DAL", 65, 980, 6, 0),
    ("Travis Hunter", "JAX", 75, 900, 6, 10),
    ("Tetairoa McMillan", "CAR", 75, 950, 6, 0),
    ("Jerry Jeudy", "CLE", 75, 950, 5, 0),
    ("Rome Odunze", "CHI", 70, 920, 6, 0),
    ("Jordan Addison", "MIN", 70, 900, 6, 0),
    ("Calvin Ridley", "TEN", 70, 950, 5, 0),
    ("Chris Godwin", "TB", 75, 850, 5, 0),
    ("Emeka Egbuka", "TB", 70, 850, 6, 10),
    ("Chris Olave", "NO", 75, 900, 5, 0),
    ("Jakobi Meyers", "LV", 75, 850, 5, 10),
    ("Stefon Diggs", "NE", 70, 820, 5, 0),
    ("Khalil Shakir", "BUF", 75, 800, 5, 10),
    ("Matthew Golden", "GB", 65, 850, 5, 10),
    ("Deebo Samuel", "WAS", 65, 780, 5, 60),
    ("Josh Downs", "IND", 70, 780, 5, 0),
    ("Jayden Reed", "GB", 60, 780, 5, 40),
    ("Ricky Pearsall", "SF", 65, 820, 5, 0),
    ("Cooper Kupp", "SEA", 65, 750, 5, 0),
    ("Rashid Shaheed", "NO", 60, 800, 5, 20),
    ("Keon Coleman", "BUF", 60, 780, 6, 0),
    ("Michael Pittman", "IND", 70, 780, 4, 0),
    ("Darnell Mooney", "ATL", 60, 780, 5, 0),
    ("Brandon Aiyuk", "SF", 60, 780, 4, 0),
    ("Luther Burden", "CHI", 60, 700, 4, 30),
    ("Jayden Higgins", "HOU", 60, 720, 5, 0),
    ("Christian Kirk", "HOU", 60, 700, 4, 0),
    ("Tre Harris", "LAC", 55, 700, 4, 0),
    ("Marvin Mims", "DEN", 55, 700, 5, 30),
    ("Hollywood Brown", "KC", 55, 650, 4, 0),
    ("Rashod Bateman", "BAL", 50, 700, 5, 0),
    ("Quentin Johnston", "LAC", 50, 650, 5, 0),
    ("Romeo Doubs", "GB", 50, 620, 5, 0),
    ("Cedric Tillman", "CLE", 55, 650, 4, 0),
    ("Wan'Dale Robinson", "NYG", 65, 600, 3, 0),
    ("Adam Thielen", "CAR", 55, 600, 4, 0),
    ("DeAndre Hopkins", "BAL", 45, 550, 5, 0),
    ("Jauan Jennings", "SF", 55, 650, 4, 0),
]

TES = [
    ("Brock Bowers", "LV", 100, 1150, 8),
    ("Trey McBride", "ARI", 95, 1050, 6),
    ("George Kittle", "SF", 75, 1000, 7),
    ("Sam LaPorta", "DET", 70, 800, 6),
    ("T.J. Hockenson", "MIN", 70, 750, 5),
    ("Tucker Kraft", "GB", 60, 700, 6),
    ("Tyler Warren", "IND", 65, 700, 5),
    ("David Njoku", "CLE", 65, 650, 5),
    ("Mark Andrews", "BAL", 55, 650, 6),
    ("Evan Engram", "DEN", 65, 600, 4),
    ("Colston Loveland", "CHI", 60, 620, 4),
    ("Dalton Kincaid", "BUF", 55, 600, 4),
    ("Jake Ferguson", "DAL", 60, 580, 4),
    ("Dallas Goedert", "PHI", 55, 580, 4),
    ("Hunter Henry", "NE", 55, 580, 4),
    ("Kyle Pitts", "ATL", 50, 550, 4),
    ("Jonnu Smith", "PIT", 55, 520, 4),
    ("Pat Freiermuth", "PIT", 45, 480, 4),
    ("Isaiah Likely", "BAL", 45, 500, 4),
    ("Zach Ertz", "WAS", 50, 480, 4),
    ("Cade Otton", "TB", 45, 450, 3),
    ("Chig Okonkwo", "TEN", 45, 450, 3),
    ("Brenton Strange", "JAX", 45, 440, 3),
    ("Ja'Tavion Sanders", "CAR", 40, 420, 3),
]

KICKERS = [
    ("Brandon Aubrey", "DAL", 16, 8, 8, 35),
    ("Jake Bates", "DET", 15, 8, 6, 42),
    ("Cameron Dicker", "LAC", 16, 8, 5, 36),
    ("Chris Boswell", "PIT", 16, 7, 5, 32),
    ("Ka'imi Fairbairn", "HOU", 15, 7, 5, 33),
    ("Tyler Bass", "BUF", 14, 7, 4, 44),
    ("Jake Elliott", "PHI", 14, 7, 4, 40),
    ("Harrison Butker", "KC", 15, 6, 4, 38),
    ("Evan McPherson", "CIN", 14, 7, 4, 36),
    ("Younghoe Koo", "ATL", 14, 6, 4, 34),
    ("Cairo Santos", "CHI", 15, 6, 3, 32),
    ("Jason Sanders", "MIA", 14, 6, 4, 30),
    ("Wil Lutz", "DEN", 14, 6, 3, 33),
    ("Chase McLaughlin", "TB", 13, 6, 4, 34),
    ("Matt Gay", "WAS", 13, 6, 3, 32),
]

DSTS = [
    ("Denver Broncos", 52, 14, 10, 4, 300, 5100),
    ("Baltimore Ravens", 48, 14, 10, 3, 310, 5200),
    ("Philadelphia Eagles", 45, 14, 10, 3, 305, 5150),
    ("Pittsburgh Steelers", 46, 13, 10, 3, 320, 5300),
    ("Houston Texans", 47, 13, 9, 3, 325, 5350),
    ("Minnesota Vikings", 45, 13, 9, 3, 330, 5300),
    ("Green Bay Packers", 42, 14, 9, 3, 330, 5400),
    ("Detroit Lions", 42, 12, 9, 3, 340, 5450),
    ("Kansas City Chiefs", 42, 12, 9, 2, 335, 5400),
    ("Buffalo Bills", 41, 13, 9, 2, 340, 5450),
    ("Seattle Seahawks", 42, 12, 8, 2, 345, 5500),
    ("Los Angeles Chargers", 40, 12, 8, 2, 340, 5450),
    ("New York Jets", 40, 11, 8, 2, 350, 5550),
    ("San Francisco 49ers", 40, 11, 8, 2, 355, 5600),
    ("Dallas Cowboys", 39, 11, 8, 2, 360, 5650),
]


def _rows():
    for n, t, py, ptd, pi, ry, rtd in QBS:
        yield n, t, "QB", {"pass_yd": py, "pass_td": ptd, "pass_int": pi,
                           "rush_yd": ry, "rush_td": rtd, "fum_lost": 3}
    for n, t, ry, rtd, rec, recy, rectd in RBS:
        yield n, t, "RB", {"rush_yd": ry, "rush_td": rtd, "rec": rec,
                           "rec_yd": recy, "rec_td": rectd, "fum_lost": 1}
    for n, t, rec, recy, rectd, ry in WRS:
        yield n, t, "WR", {"rec": rec, "rec_yd": recy, "rec_td": rectd,
                           "rush_yd": ry, "fum_lost": 1}
    for n, t, rec, recy, rectd in TES:
        yield n, t, "TE", {"rec": rec, "rec_yd": recy, "rec_td": rectd, "fum_lost": 0}
    for n, t, fgs, fg40, fg50, xp in KICKERS:
        yield n, t, "K", {"fgm_0_19": 1, "fgm_20_29": fgs // 2, "fgm_30_39": fgs - fgs // 2 - 1,
                          "fgm_40_49": fg40, "fgm_50p": fg50, "fgmiss": 3, "xpm": xp, "xpmiss": 1}
    for n, sack, ints, fr, td, pa, ya in DSTS:
        yield n, None, "DST", {"sack": sack, "int": ints, "fum_rec": fr,
                               "def_td": td, "pts_allow": pa, "yds_allow": ya}


def load():
    """Insert the sample pool. Returns number of players loaded."""
    rows = []
    for name, team, pos, stats in _rows():
        rows.append({
            "id": f"smpl:{norm_name(name).replace(' ', '-')}:{pos}",
            "name": name,
            "position": pos,
            "team": team,
            "stats": stats,
            "points": scoring.score_player(pos, stats),
        })
    db.upsert_players(rows, source="sample")
    db.meta_set("last_refresh", {"source": "sample", "players": len(rows)})
    return len(rows)
