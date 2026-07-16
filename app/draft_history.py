"""League UNC auction results 2021-2025, bundled with the copilot.
Transcribed from FantasyPros draft-summary exports supplied by Brett.
team = sheet alias (last name / Nova); keeper = kept at that draft
(flagged for 2024-25 only; keeper prices are formula prices, prior
year + $15, and are excluded from temperament calibration)."""

DRAFTS = {
 "2025": [
  {
   "player": "Ja'Marr Chase",
   "pos": "WR",
   "team": "Crisp",
   "price": 171
  },
  {
   "player": "Saquon Barkley",
   "pos": "RB",
   "team": "Lesesne",
   "price": 156,
   "keeper": True
  },
  {
   "player": "Bijan Robinson",
   "pos": "RB",
   "team": "Byrd",
   "price": 198,
   "keeper": True
  },
  {
   "player": "Jahmyr Gibbs",
   "pos": "RB",
   "team": "Link",
   "price": 105,
   "keeper": True
  },
  {
   "player": "Derrick Henry",
   "pos": "RB",
   "team": "Ned",
   "price": 105,
   "keeper": True
  },
  {
   "player": "Justin Jefferson",
   "pos": "WR",
   "team": "Crisp",
   "price": 155
  },
  {
   "player": "Christian McCaffrey",
   "pos": "RB",
   "team": "Omar",
   "price": 127
  },
  {
   "player": "Jonathan Taylor",
   "pos": "RB",
   "team": "Link",
   "price": 110
  },
  {
   "player": "CeeDee Lamb",
   "pos": "WR",
   "team": "Nova",
   "price": 131
  },
  {
   "player": "Josh Jacobs",
   "pos": "RB",
   "team": "Singer",
   "price": 86,
   "keeper": True
  },
  {
   "player": "Puka Nacua",
   "pos": "WR",
   "team": "Omar",
   "price": 88,
   "keeper": True
  },
  {
   "player": "Ashton Jeanty",
   "pos": "RB",
   "team": "Farmer",
   "price": 118
  },
  {
   "player": "Malik Nabers",
   "pos": "WR",
   "team": "Nova",
   "price": 75,
   "keeper": True
  },
  {
   "player": "Kyren Williams",
   "pos": "RB",
   "team": "Rob",
   "price": 95
  },
  {
   "player": "Nico Collins",
   "pos": "WR",
   "team": "Singer",
   "price": 75,
   "keeper": True
  },
  {
   "player": "Brian Thomas Jr.",
   "pos": "WR",
   "team": "Rob",
   "price": 20,
   "keeper": True
  },
  {
   "player": "De'Von Achane",
   "pos": "RB",
   "team": "Farmer",
   "price": 49,
   "keeper": True
  },
  {
   "player": "Amon-Ra St. Brown",
   "pos": "WR",
   "team": "Farmer",
   "price": 110
  },
  {
   "player": "Josh Allen",
   "pos": "QB",
   "team": "Farmer",
   "price": 83
  },
  {
   "player": "Brock Bowers",
   "pos": "TE",
   "team": "Ned",
   "price": 32,
   "keeper": True
  },
  {
   "player": "Lamar Jackson",
   "pos": "QB",
   "team": "Byrd",
   "price": 45,
   "keeper": True
  },
  {
   "player": "Bucky Irving",
   "pos": "RB",
   "team": "Singer",
   "price": 125
  },
  {
   "player": "George Kittle",
   "pos": "TE",
   "team": "Lesesne",
   "price": 35,
   "keeper": True
  },
  {
   "player": "A.J. Brown",
   "pos": "WR",
   "team": "Byrd",
   "price": 80
  },
  {
   "player": "James Cook",
   "pos": "RB",
   "team": "Crisp",
   "price": 79
  },
  {
   "player": "Chase Brown",
   "pos": "RB",
   "team": "Rob",
   "price": 157
  },
  {
   "player": "Drake London",
   "pos": "WR",
   "team": "Nova",
   "price": 96
  },
  {
   "player": "Tyreek Hill",
   "pos": "WR",
   "team": "Omar",
   "price": 53
  },
  {
   "player": "Trey McBride",
   "pos": "TE",
   "team": "Singer",
   "price": 50
  },
  {
   "player": "Mike Evans",
   "pos": "WR",
   "team": "Ned",
   "price": 50
  },
  {
   "player": "Jalen Hurts",
   "pos": "QB",
   "team": "Singer",
   "price": 62
  },
  {
   "player": "Ladd McConkey",
   "pos": "WR",
   "team": "Farmer",
   "price": 79
  },
  {
   "player": "Jayden Daniels",
   "pos": "QB",
   "team": "Nova",
   "price": 28,
   "keeper": True
  },
  {
   "player": "Tee Higgins",
   "pos": "WR",
   "team": "Lesesne",
   "price": 72
  },
  {
   "player": "James Conner",
   "pos": "RB",
   "team": "Omar",
   "price": 42
  },
  {
   "player": "Kenneth Walker III",
   "pos": "RB",
   "team": "Ned",
   "price": 73
  },
  {
   "player": "Davante Adams",
   "pos": "WR",
   "team": "Lesesne",
   "price": 46
  },
  {
   "player": "Terry McLaurin",
   "pos": "WR",
   "team": "Rob",
   "price": 43
  },
  {
   "player": "Chuba Hubbard",
   "pos": "RB",
   "team": "Rob",
   "price": 45
  },
  {
   "player": "Omarion Hampton",
   "pos": "RB",
   "team": "Nova",
   "price": 111
  },
  {
   "player": "Breece Hall",
   "pos": "RB",
   "team": "Crisp",
   "price": 51
  },
  {
   "player": "Alvin Kamara",
   "pos": "RB",
   "team": "Nova",
   "price": 46
  },
  {
   "player": "DK Metcalf",
   "pos": "WR",
   "team": "Link",
   "price": 39
  },
  {
   "player": "Joe Burrow",
   "pos": "QB",
   "team": "Omar",
   "price": 26,
   "keeper": True
  },
  {
   "player": "Marvin Harrison Jr.",
   "pos": "WR",
   "team": "Singer",
   "price": 57
  },
  {
   "player": "Jaxon Smith-Njigba",
   "pos": "WR",
   "team": "Byrd",
   "price": 53
  },
  {
   "player": "David Montgomery",
   "pos": "RB",
   "team": "Link",
   "price": 44
  },
  {
   "player": "D'Andre Swift",
   "pos": "RB",
   "team": "Farmer",
   "price": 46
  },
  {
   "player": "Xavier Worthy",
   "pos": "WR",
   "team": "Link",
   "price": 37
  },
  {
   "player": "Sam LaPorta",
   "pos": "TE",
   "team": "Rob",
   "price": 26
  },
  {
   "player": "Zay Flowers",
   "pos": "WR",
   "team": "Rob",
   "price": 40
  },
  {
   "player": "Mark Andrews",
   "pos": "TE",
   "team": "Crisp",
   "price": 12
  },
  {
   "player": "TreVeyon Henderson",
   "pos": "RB",
   "team": "Byrd",
   "price": 78
  },
  {
   "player": "Tony Pollard",
   "pos": "RB",
   "team": "Rob",
   "price": 38
  },
  {
   "player": "Courtland Sutton",
   "pos": "WR",
   "team": "Crisp",
   "price": 35
  },
  {
   "player": "Patrick Mahomes II",
   "pos": "QB",
   "team": "Rob",
   "price": 10
  },
  {
   "player": "DJ Moore",
   "pos": "WR",
   "team": "Ned",
   "price": 22
  },
  {
   "player": "Aaron Jones Sr.",
   "pos": "RB",
   "team": "Ned",
   "price": 31
  },
  {
   "player": "Jameson Williams",
   "pos": "WR",
   "team": "Singer",
   "price": 30
  },
  {
   "player": "Garrett Wilson",
   "pos": "WR",
   "team": "Farmer",
   "price": 32
  },
  {
   "player": "Calvin Ridley",
   "pos": "WR",
   "team": "Omar",
   "price": 41
  },
  {
   "player": "George Pickens",
   "pos": "WR",
   "team": "Singer",
   "price": 35
  },
  {
   "player": "Travis Kelce",
   "pos": "TE",
   "team": "Omar",
   "price": 7
  },
  {
   "player": "Isiah Pacheco",
   "pos": "RB",
   "team": "Lesesne",
   "price": 40
  },
  {
   "player": "RJ Harvey",
   "pos": "RB",
   "team": "Omar",
   "price": 35
  },
  {
   "player": "DeVonta Smith",
   "pos": "WR",
   "team": "Omar",
   "price": 17
  },
  {
   "player": "Baker Mayfield",
   "pos": "QB",
   "team": "Lesesne",
   "price": 7
  },
  {
   "player": "Joe Mixon",
   "pos": "RB",
   "team": "Ned",
   "price": 34
  },
  {
   "player": "Kaleb Johnson",
   "pos": "RB",
   "team": "Singer",
   "price": 32
  },
  {
   "player": "T.J. Hockenson",
   "pos": "TE",
   "team": "Lesesne",
   "price": 5
  },
  {
   "player": "Kyler Murray",
   "pos": "QB",
   "team": "Crisp",
   "price": 27
  },
  {
   "player": "Tyrone Tracy Jr.",
   "pos": "RB",
   "team": "Crisp",
   "price": 22
  },
  {
   "player": "Jerry Jeudy",
   "pos": "WR",
   "team": "Ned",
   "price": 11
  },
  {
   "player": "David Njoku",
   "pos": "TE",
   "team": "Nova",
   "price": 6
  },
  {
   "player": "Brock Purdy",
   "pos": "QB",
   "team": "Rob",
   "price": 2
  },
  {
   "player": "Deebo Samuel Sr.",
   "pos": "WR",
   "team": "Byrd",
   "price": 7
  },
  {
   "player": "Jaylen Warren",
   "pos": "RB",
   "team": "Nova",
   "price": 12
  },
  {
   "player": "Tetairoa McMillan",
   "pos": "WR",
   "team": "Ned",
   "price": 10
  },
  {
   "player": "Bo Nix",
   "pos": "QB",
   "team": "Omar",
   "price": 3
  },
  {
   "player": "Quinshon Judkins",
   "pos": "RB",
   "team": "Nova",
   "price": 11
  },
  {
   "player": "Jakobi Meyers",
   "pos": "WR",
   "team": "Link",
   "price": 5
  },
  {
   "player": "Jaylen Waddle",
   "pos": "WR",
   "team": "Lesesne",
   "price": 34
  },
  {
   "player": "Tyler Warren",
   "pos": "TE",
   "team": "Farmer",
   "price": 4
  },
  {
   "player": "Jordan Mason",
   "pos": "RB",
   "team": "Crisp",
   "price": 5
  },
  {
   "player": "J.K. Dobbins",
   "pos": "RB",
   "team": "Lesesne",
   "price": 14
  },
  {
   "player": "Travis Etienne Jr.",
   "pos": "RB",
   "team": "Lesesne",
   "price": 9
  },
  {
   "player": "Matthew Golden",
   "pos": "WR",
   "team": "Link",
   "price": 11
  },
  {
   "player": "Javonte Williams",
   "pos": "RB",
   "team": "Singer",
   "price": 25
  },
  {
   "player": "Justin Fields",
   "pos": "QB",
   "team": "Byrd",
   "price": 2
  },
  {
   "player": "Zach Charbonnet",
   "pos": "RB",
   "team": "Singer",
   "price": 14
  },
  {
   "player": "Jauan Jennings",
   "pos": "WR",
   "team": "Ned",
   "price": 10
  },
  {
   "player": "Tucker Kraft",
   "pos": "TE",
   "team": "Link",
   "price": 7
  },
  {
   "player": "Travis Hunter",
   "pos": "WR",
   "team": "Omar",
   "price": 15
  },
  {
   "player": "Tank Bigsby",
   "pos": "RB",
   "team": "Nova",
   "price": 23
  },
  {
   "player": "Rome Odunze",
   "pos": "WR",
   "team": "Crisp",
   "price": 16
  },
  {
   "player": "Chris Olave",
   "pos": "WR",
   "team": "Byrd",
   "price": 1
  },
  {
   "player": "Keon Coleman",
   "pos": "WR",
   "team": "Crisp",
   "price": 7
  },
  {
   "player": "Jayden Reed",
   "pos": "WR",
   "team": "Byrd",
   "price": 1
  },
  {
   "player": "Rashid Shaheed",
   "pos": "WR",
   "team": "Omar",
   "price": 1
  },
  {
   "player": "Rashee Rice",
   "pos": "WR",
   "team": "Farmer",
   "price": 10
  },
  {
   "player": "J.J. McCarthy",
   "pos": "QB",
   "team": "Link",
   "price": 1
  },
  {
   "player": "Cam Skattebo",
   "pos": "RB",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "Jacory Croskey-Merritt",
   "pos": "RB",
   "team": "Omar",
   "price": 23
  },
  {
   "player": "Stefon Diggs",
   "pos": "WR",
   "team": "Link",
   "price": 7
  },
  {
   "player": "Trey Benson",
   "pos": "RB",
   "team": "Crisp",
   "price": 9
  },
  {
   "player": "Nick Chubb",
   "pos": "RB",
   "team": "Singer",
   "price": 1
  },
  {
   "player": "Ricky Pearsall",
   "pos": "WR",
   "team": "Nova",
   "price": 29
  },
  {
   "player": "Jordan Addison",
   "pos": "WR",
   "team": "Lesesne",
   "price": 7
  },
  {
   "player": "Evan Engram",
   "pos": "TE",
   "team": "Byrd",
   "price": 1
  },
  {
   "player": "Caleb Williams",
   "pos": "QB",
   "team": "Singer",
   "price": 1
  },
  {
   "player": "Brian Robinson Jr.",
   "pos": "RB",
   "team": "Link",
   "price": 5
  },
  {
   "player": "Jaylen Wright",
   "pos": "RB",
   "team": "Farmer",
   "price": 1
  },
  {
   "player": "Buffalo Bills",
   "pos": "DST",
   "team": "Farmer",
   "price": 2
  },
  {
   "player": "Denver Broncos",
   "pos": "DST",
   "team": "Singer",
   "price": 4
  },
  {
   "player": "Philadelphia Eagles",
   "pos": "DST",
   "team": "Link",
   "price": 2
  },
  {
   "player": "Houston Texans",
   "pos": "DST",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "Baltimore Ravens",
   "pos": "DST",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Dallas Cowboys",
   "pos": "DST",
   "team": "Crisp",
   "price": 1
  },
  {
   "player": "Tyler Allgeier",
   "pos": "RB",
   "team": "Byrd",
   "price": 1
  },
  {
   "player": "Chris Godwin",
   "pos": "WR",
   "team": "Byrd",
   "price": 1
  },
  {
   "player": "Pittsburgh Steelers",
   "pos": "DST",
   "team": "Rob",
   "price": 3
  },
  {
   "player": "Green Bay Packers",
   "pos": "DST",
   "team": "Farmer",
   "price": 1
  },
  {
   "player": "Minnesota Vikings",
   "pos": "DST",
   "team": "Lesesne",
   "price": 1
  },
  {
   "player": "New York Giants",
   "pos": "DST",
   "team": "Omar",
   "price": 1
  },
  {
   "player": "Brandon Aubrey",
   "pos": "K",
   "team": "Rob",
   "price": 3
  },
  {
   "player": "Matt Gay",
   "pos": "K",
   "team": "Omar",
   "price": 1
  },
  {
   "player": "Chase McLaughlin",
   "pos": "K",
   "team": "Singer",
   "price": 2
  },
  {
   "player": "Jake Elliott",
   "pos": "K",
   "team": "Link",
   "price": 1
  },
  {
   "player": "Jason Sanders",
   "pos": "K",
   "team": "Farmer",
   "price": 1
  },
  {
   "player": "Tyler Bass",
   "pos": "K",
   "team": "Crisp",
   "price": 1
  },
  {
   "player": "Cameron Dicker",
   "pos": "K",
   "team": "Lesesne",
   "price": 2
  },
  {
   "player": "Evan McPherson",
   "pos": "K",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "Jake Bates",
   "pos": "K",
   "team": "Ned",
   "price": 4
  },
  {
   "player": "Emeka Egbuka",
   "pos": "WR",
   "team": "Ned",
   "price": 10
  },
  {
   "player": "Jaydon Blue",
   "pos": "RB",
   "team": "Rob",
   "price": 6
  },
  {
   "player": "Wil Lutz",
   "pos": "K",
   "team": "Byrd",
   "price": 1
  },
  {
   "player": "Khalil Shakir",
   "pos": "WR",
   "team": "Farmer",
   "price": 2
  },
  {
   "player": "Arizona Cardinals",
   "pos": "DST",
   "team": "Byrd",
   "price": 1
  },
  {
   "player": "Drake Maye",
   "pos": "QB",
   "team": "Ned",
   "price": 6
  },
  {
   "player": "Braelon Allen",
   "pos": "RB",
   "team": "Byrd",
   "price": 1
  },
  {
   "player": "Bhayshul Tuten",
   "pos": "RB",
   "team": "Nova",
   "price": 5
  },
  {
   "player": "Jayden Higgins",
   "pos": "WR",
   "team": "Link",
   "price": 1
  },
  {
   "player": "Ollie Gordon II",
   "pos": "RB",
   "team": "Link",
   "price": 1
  },
  {
   "player": "Kyle Monangai",
   "pos": "RB",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Jarquez Hunter",
   "pos": "RB",
   "team": "Rob",
   "price": 5
  },
  {
   "player": "Romeo Doubs",
   "pos": "WR",
   "team": "Farmer",
   "price": 1
  },
  {
   "player": "Will Shipley",
   "pos": "RB",
   "team": "Lesesne",
   "price": 1
  },
  {
   "player": "Jordan James",
   "pos": "RB",
   "team": "Rob",
   "price": 1
  },
  {
   "player": "Dyami Brown",
   "pos": "WR",
   "team": "Lesesne",
   "price": 1
  },
  {
   "player": "Thornton",
   "pos": "WR",
   "team": "Crisp",
   "price": 1
  }
 ],
 "2021": [
  {
   "player": "Christian McCaffrey",
   "pos": "RB",
   "team": "Link",
   "price": 175
  },
  {
   "player": "Dalvin Cook",
   "pos": "RB",
   "team": "Omar",
   "price": 192
  },
  {
   "player": "Derrick Henry",
   "pos": "RB",
   "team": "Singer",
   "price": 192
  },
  {
   "player": "Alvin Kamara",
   "pos": "RB",
   "team": "Omar",
   "price": 160
  },
  {
   "player": "Ezekiel Elliott",
   "pos": "RB",
   "team": "Ned",
   "price": 143
  },
  {
   "player": "Nick Chubb",
   "pos": "RB",
   "team": "Crisp",
   "price": 130
  },
  {
   "player": "Aaron Jones",
   "pos": "RB",
   "team": "Rob",
   "price": 33
  },
  {
   "player": "Jonathan Taylor",
   "pos": "RB",
   "team": "Nova",
   "price": 121
  },
  {
   "player": "Saquon Barkley",
   "pos": "RB",
   "team": "Lesesne",
   "price": 145
  },
  {
   "player": "Davante Adams",
   "pos": "WR",
   "team": "Farmer",
   "price": 137
  },
  {
   "player": "Tyreek Hill",
   "pos": "WR",
   "team": "Byrd",
   "price": 145
  },
  {
   "player": "Stefon Diggs",
   "pos": "WR",
   "team": "Singer",
   "price": 68
  },
  {
   "player": "Calvin Ridley",
   "pos": "WR",
   "team": "Crisp",
   "price": 73
  },
  {
   "player": "Antonio Gibson",
   "pos": "RB",
   "team": "Byrd",
   "price": 35
  },
  {
   "player": "Travis Kelce",
   "pos": "TE",
   "team": "Ned",
   "price": 113
  },
  {
   "player": "Najee Harris",
   "pos": "RB",
   "team": "Ned",
   "price": 131
  },
  {
   "player": "DeAndre Hopkins",
   "pos": "WR",
   "team": "Link",
   "price": 48
  },
  {
   "player": "Joe Mixon",
   "pos": "RB",
   "team": "Rob",
   "price": 105
  },
  {
   "player": "D.K. Metcalf",
   "pos": "WR",
   "team": "Nova",
   "price": 50
  },
  {
   "player": "A.J. Brown",
   "pos": "WR",
   "team": "Farmer",
   "price": 80
  },
  {
   "player": "Austin Ekeler",
   "pos": "RB",
   "team": "Nova",
   "price": 92
  },
  {
   "player": "Darren Waller",
   "pos": "TE",
   "team": "Singer",
   "price": 38
  },
  {
   "player": "Justin Jefferson",
   "pos": "WR",
   "team": "Ned",
   "price": 30
  },
  {
   "player": "Patrick Mahomes II",
   "pos": "QB",
   "team": "Nova",
   "price": 30
  },
  {
   "player": "George Kittle",
   "pos": "TE",
   "team": "Byrd",
   "price": 76
  },
  {
   "player": "Terry McLaurin",
   "pos": "WR",
   "team": "Ned",
   "price": 60
  },
  {
   "player": "J.K. Dobbins",
   "pos": "RB",
   "team": "Ned",
   "price": 50
  },
  {
   "player": "Clyde Edwards-Helaire",
   "pos": "RB",
   "team": "Farmer",
   "price": 100
  },
  {
   "player": "Allen Robinson II",
   "pos": "WR",
   "team": "Omar",
   "price": 39
  },
  {
   "player": "Mike Evans",
   "pos": "WR",
   "team": "Rob",
   "price": 57
  },
  {
   "player": "CeeDee Lamb",
   "pos": "WR",
   "team": "Byrd",
   "price": 52
  },
  {
   "player": "Chris Carson",
   "pos": "RB",
   "team": "Omar",
   "price": 50
  },
  {
   "player": "Keenan Allen",
   "pos": "WR",
   "team": "Link",
   "price": 48
  },
  {
   "player": "David Montgomery",
   "pos": "RB",
   "team": "Crisp",
   "price": 60
  },
  {
   "player": "Chris Godwin",
   "pos": "WR",
   "team": "Lesesne",
   "price": 41
  },
  {
   "player": "Amari Cooper",
   "pos": "WR",
   "team": "Rob",
   "price": 50
  },
  {
   "player": "Robert Woods",
   "pos": "WR",
   "team": "Crisp",
   "price": 42
  },
  {
   "player": "Julio Jones",
   "pos": "WR",
   "team": "Lesesne",
   "price": 44
  },
  {
   "player": "D.J. Moore",
   "pos": "WR",
   "team": "Nova",
   "price": 37
  },
  {
   "player": "Josh Allen",
   "pos": "QB",
   "team": "Byrd",
   "price": 30
  },
  {
   "player": "D'Andre Swift",
   "pos": "RB",
   "team": "Crisp",
   "price": 68
  },
  {
   "player": "James Robinson",
   "pos": "RB",
   "team": "Byrd",
   "price": 68
  },
  {
   "player": "Miles Sanders",
   "pos": "RB",
   "team": "Singer",
   "price": 66
  },
  {
   "player": "Josh Jacobs",
   "pos": "RB",
   "team": "Lesesne",
   "price": 81
  },
  {
   "player": "Adam Thielen",
   "pos": "WR",
   "team": "Lesesne",
   "price": 31
  },
  {
   "player": "Cooper Kupp",
   "pos": "WR",
   "team": "Singer",
   "price": 28
  },
  {
   "player": "Tyler Lockett",
   "pos": "WR",
   "team": "Rob",
   "price": 27
  },
  {
   "player": "Darrell Henderson",
   "pos": "RB",
   "team": "Lesesne",
   "price": 45
  },
  {
   "player": "Brandon Aiyuk",
   "pos": "WR",
   "team": "Nova",
   "price": 33
  },
  {
   "player": "Kyler Murray",
   "pos": "QB",
   "team": "Singer",
   "price": 60
  },
  {
   "player": "Mark Andrews",
   "pos": "TE",
   "team": "Rob",
   "price": 32
  },
  {
   "player": "Lamar Jackson",
   "pos": "QB",
   "team": "Link",
   "price": 51
  },
  {
   "player": "Tee Higgins",
   "pos": "WR",
   "team": "Farmer",
   "price": 25
  },
  {
   "player": "Kenny Golladay",
   "pos": "WR",
   "team": "Link",
   "price": 10
  },
  {
   "player": "Diontae Johnson",
   "pos": "WR",
   "team": "Byrd",
   "price": 26
  },
  {
   "player": "T.J. Hockenson",
   "pos": "TE",
   "team": "Link",
   "price": 17
  },
  {
   "player": "Kyle Pitts",
   "pos": "TE",
   "team": "Lesesne",
   "price": 46
  },
  {
   "player": "Mike Davis",
   "pos": "RB",
   "team": "Farmer",
   "price": 40
  },
  {
   "player": "Odell Beckham Jr.",
   "pos": "WR",
   "team": "Farmer",
   "price": 40
  },
  {
   "player": "Kareem Hunt",
   "pos": "RB",
   "team": "Rob",
   "price": 37
  },
  {
   "player": "Chase Claypool",
   "pos": "WR",
   "team": "Singer",
   "price": 21
  },
  {
   "player": "Dak Prescott",
   "pos": "QB",
   "team": "Rob",
   "price": 9
  },
  {
   "player": "Myles Gaskin",
   "pos": "RB",
   "team": "Crisp",
   "price": 46
  },
  {
   "player": "Ja'Marr Chase",
   "pos": "WR",
   "team": "Rob",
   "price": 27
  },
  {
   "player": "Courtland Sutton",
   "pos": "WR",
   "team": "Farmer",
   "price": 11
  },
  {
   "player": "Russell Wilson",
   "pos": "QB",
   "team": "Omar",
   "price": 10
  },
  {
   "player": "Jerry Jeudy",
   "pos": "WR",
   "team": "Rob",
   "price": 16
  },
  {
   "player": "Damien Harris",
   "pos": "RB",
   "team": "Ned",
   "price": 37
  },
  {
   "player": "Aaron Rodgers",
   "pos": "QB",
   "team": "Lesesne",
   "price": 26
  },
  {
   "player": "Javonte Williams",
   "pos": "RB",
   "team": "Farmer",
   "price": 42
  },
  {
   "player": "Justin Herbert",
   "pos": "QB",
   "team": "Link",
   "price": 15
  },
  {
   "player": "JuJu Smith-Schuster",
   "pos": "WR",
   "team": "Rob",
   "price": 10
  },
  {
   "player": "Chase Edmonds",
   "pos": "RB",
   "team": "Link",
   "price": 46
  },
  {
   "player": "Robby Anderson",
   "pos": "WR",
   "team": "Omar",
   "price": 18
  },
  {
   "player": "Raheem Mostert",
   "pos": "RB",
   "team": "Crisp",
   "price": 19
  },
  {
   "player": "Ronald Jones II",
   "pos": "RB",
   "team": "Nova",
   "price": 10
  },
  {
   "player": "Brandin Cooks",
   "pos": "WR",
   "team": "Omar",
   "price": 4
  },
  {
   "player": "Melvin Gordon III",
   "pos": "RB",
   "team": "Crisp",
   "price": 12
  },
  {
   "player": "D.J. Chark Jr.",
   "pos": "WR",
   "team": "Crisp",
   "price": 13
  },
  {
   "player": "Deebo Samuel",
   "pos": "WR",
   "team": "Crisp",
   "price": 6
  },
  {
   "player": "Tyler Boyd",
   "pos": "WR",
   "team": "Ned",
   "price": 3
  },
  {
   "player": "Noah Fant",
   "pos": "TE",
   "team": "Farmer",
   "price": 1
  },
  {
   "player": "Will Fuller V",
   "pos": "WR",
   "team": "Byrd",
   "price": 16
  },
  {
   "player": "Ryan Tannehill",
   "pos": "QB",
   "team": "Crisp",
   "price": 3
  },
  {
   "player": "Tom Brady",
   "pos": "QB",
   "team": "Rob",
   "price": 5
  },
  {
   "player": "Trey Sermon",
   "pos": "RB",
   "team": "Byrd",
   "price": 18
  },
  {
   "player": "DeVonta Smith",
   "pos": "WR",
   "team": "Lesesne",
   "price": 16
  },
  {
   "player": "Robert Tonyan",
   "pos": "TE",
   "team": "Crisp",
   "price": 1
  },
  {
   "player": "Logan Thomas",
   "pos": "TE",
   "team": "Omar",
   "price": 1
  },
  {
   "player": "Jalen Hurts",
   "pos": "QB",
   "team": "Farmer",
   "price": 5
  },
  {
   "player": "Dallas Goedert",
   "pos": "TE",
   "team": "Omar",
   "price": 8
  },
  {
   "player": "Antonio Brown",
   "pos": "WR",
   "team": "Nova",
   "price": 9
  },
  {
   "player": "Corey Davis",
   "pos": "WR",
   "team": "Singer",
   "price": 5
  },
  {
   "player": "Matthew Stafford",
   "pos": "QB",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Mike Williams",
   "pos": "WR",
   "team": "Ned",
   "price": 4
  },
  {
   "player": "Michael Carter",
   "pos": "RB",
   "team": "Byrd",
   "price": 8
  },
  {
   "player": "James Conner",
   "pos": "RB",
   "team": "Link",
   "price": 5
  },
  {
   "player": "Zack Moss",
   "pos": "RB",
   "team": "Rob",
   "price": 10
  },
  {
   "player": "Michael Gallup",
   "pos": "WR",
   "team": "Singer",
   "price": 1
  },
  {
   "player": "Gus Edwards",
   "pos": "RB",
   "team": "Link",
   "price": 45
  },
  {
   "player": "Jarvis Landry",
   "pos": "WR",
   "team": "Farmer",
   "price": 3
  },
  {
   "player": "Laviska Shenault Jr.",
   "pos": "WR",
   "team": "Nova",
   "price": 3
  },
  {
   "player": "Leonard Fournette",
   "pos": "RB",
   "team": "Link",
   "price": 8
  },
  {
   "player": "Tyler Higbee",
   "pos": "TE",
   "team": "Nova",
   "price": 8
  },
  {
   "player": "AJ Dillon",
   "pos": "RB",
   "team": "Link",
   "price": 19
  },
  {
   "player": "Kenyan Drake",
   "pos": "RB",
   "team": "Singer",
   "price": 12
  },
  {
   "player": "Jamaal Williams",
   "pos": "RB",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "Marquise Brown",
   "pos": "WR",
   "team": "Link",
   "price": 10
  },
  {
   "player": "Michael Thomas",
   "pos": "WR",
   "team": "Byrd",
   "price": 20
  },
  {
   "player": "Devin Singletary",
   "pos": "RB",
   "team": "Singer",
   "price": 3
  },
  {
   "player": "David Johnson",
   "pos": "RB",
   "team": "Lesesne",
   "price": 1
  },
  {
   "player": "Jaylen Waddle",
   "pos": "WR",
   "team": "Crisp",
   "price": 10
  },
  {
   "player": "Trevor Lawrence",
   "pos": "QB",
   "team": "Lesesne",
   "price": 1
  },
  {
   "player": "Michael Pittman Jr.",
   "pos": "WR",
   "team": "Ned",
   "price": 3
  },
  {
   "player": "Tony Pollard",
   "pos": "RB",
   "team": "Byrd",
   "price": 5
  },
  {
   "player": "Latavius Murray",
   "pos": "RB",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "Henry Ruggs III",
   "pos": "WR",
   "team": "Omar",
   "price": 7
  },
  {
   "player": "Alexander Mattison",
   "pos": "RB",
   "team": "Byrd",
   "price": 5
  },
  {
   "player": "Justin Fields",
   "pos": "QB",
   "team": "Omar",
   "price": 6
  },
  {
   "player": "Los Angeles Rams",
   "pos": "DST",
   "team": "Farmer",
   "price": 7
  },
  {
   "player": "Elijah Moore",
   "pos": "WR",
   "team": "Singer",
   "price": 1
  },
  {
   "player": "Tevin Coleman",
   "pos": "RB",
   "team": "Farmer",
   "price": 1
  },
  {
   "player": "Pittsburgh Steelers",
   "pos": "DST",
   "team": "Lesesne",
   "price": 2
  },
  {
   "player": "Russell Gage",
   "pos": "WR",
   "team": "Farmer",
   "price": 2
  },
  {
   "player": "Rashaad Penny",
   "pos": "RB",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "Baltimore Ravens",
   "pos": "DST",
   "team": "Byrd",
   "price": 2
  },
  {
   "player": "Trey Lance",
   "pos": "QB",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Sony Michel",
   "pos": "RB",
   "team": "Lesesne",
   "price": 7
  },
  {
   "player": "Washington Football Team",
   "pos": "DST",
   "team": "Crisp",
   "price": 8
  },
  {
   "player": "San Francisco 49ers",
   "pos": "DST",
   "team": "Omar",
   "price": 2
  },
  {
   "player": "Tampa Bay Buccaneers",
   "pos": "DST",
   "team": "Rob",
   "price": 20
  },
  {
   "player": "Justin Tucker",
   "pos": "K",
   "team": "Rob",
   "price": 62
  },
  {
   "player": "Emmanuel Sanders",
   "pos": "WR",
   "team": "Omar",
   "price": 1
  },
  {
   "player": "Indianapolis Colts",
   "pos": "DST",
   "team": "Nova",
   "price": 2
  },
  {
   "player": "Harrison Butker",
   "pos": "K",
   "team": "Byrd",
   "price": 4
  },
  {
   "player": "Younghoe Koo",
   "pos": "K",
   "team": "Singer",
   "price": 2
  },
  {
   "player": "Buffalo Bills",
   "pos": "DST",
   "team": "Link",
   "price": 1
  },
  {
   "player": "New England Patriots",
   "pos": "DST",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Tarik Cohen",
   "pos": "RB",
   "team": "Omar",
   "price": 1
  },
  {
   "player": "Greg Zuerlein",
   "pos": "K",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "New Orleans Saints",
   "pos": "DST",
   "team": "Singer",
   "price": 1
  },
  {
   "player": "Jason Sanders",
   "pos": "K",
   "team": "Omar",
   "price": 1
  },
  {
   "player": "Darrynton Evans",
   "pos": "RB",
   "team": "Singer",
   "price": 1
  },
  {
   "player": "Marquez Callaway",
   "pos": "WR",
   "team": "Ned",
   "price": 2
  },
  {
   "player": "Rodrigo Blankenship",
   "pos": "K",
   "team": "Crisp",
   "price": 8
  },
  {
   "player": "Matt Prater",
   "pos": "K",
   "team": "Lesesne",
   "price": 1
  },
  {
   "player": "Tyler Bass",
   "pos": "K",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "Sammy Watkins",
   "pos": "WR",
   "team": "Lesesne",
   "price": 1
  },
  {
   "player": "Ryan Succop",
   "pos": "K",
   "team": "Farmer",
   "price": 1
  }
 ],
 "2022": [
  {
   "player": "Jonathan Taylor",
   "pos": "RB",
   "team": "Nova",
   "price": 146
  },
  {
   "player": "Christian McCaffrey",
   "pos": "RB",
   "team": "Lesesne",
   "price": 150
  },
  {
   "player": "Derrick Henry",
   "pos": "RB",
   "team": "Crisp",
   "price": 159
  },
  {
   "player": "Dalvin Cook",
   "pos": "RB",
   "team": "Singer",
   "price": 162
  },
  {
   "player": "Austin Ekeler",
   "pos": "RB",
   "team": "Farmer",
   "price": 117
  },
  {
   "player": "Joe Mixon",
   "pos": "RB",
   "team": "Ned",
   "price": 122
  },
  {
   "player": "Najee Harris",
   "pos": "RB",
   "team": "Link",
   "price": 157
  },
  {
   "player": "Justin Jefferson",
   "pos": "WR",
   "team": "Ned",
   "price": 55
  },
  {
   "player": "Nick Chubb",
   "pos": "RB",
   "team": "Omar",
   "price": 98
  },
  {
   "player": "Cooper Kupp",
   "pos": "WR",
   "team": "Singer",
   "price": 53
  },
  {
   "player": "Ja'Marr Chase",
   "pos": "WR",
   "team": "Rob",
   "price": 52
  },
  {
   "player": "Mark Andrews",
   "pos": "TE",
   "team": "Byrd",
   "price": 95
  },
  {
   "player": "Alvin Kamara",
   "pos": "RB",
   "team": "Ned",
   "price": 130
  },
  {
   "player": "Saquon Barkley",
   "pos": "RB",
   "team": "Nova",
   "price": 91
  },
  {
   "player": "D'Andre Swift",
   "pos": "RB",
   "team": "Byrd",
   "price": 106
  },
  {
   "player": "Travis Kelce",
   "pos": "TE",
   "team": "Link",
   "price": 104
  },
  {
   "player": "Stefon Diggs",
   "pos": "WR",
   "team": "Crisp",
   "price": 115
  },
  {
   "player": "Davante Adams",
   "pos": "WR",
   "team": "Crisp",
   "price": 79
  },
  {
   "player": "Deebo Samuel",
   "pos": "WR",
   "team": "Crisp",
   "price": 31
  },
  {
   "player": "Aaron Jones",
   "pos": "RB",
   "team": "Rob",
   "price": 58
  },
  {
   "player": "CeeDee Lamb",
   "pos": "WR",
   "team": "Byrd",
   "price": 77
  },
  {
   "player": "Javonte Williams",
   "pos": "RB",
   "team": "Lesesne",
   "price": 109
  },
  {
   "player": "Leonard Fournette",
   "pos": "RB",
   "team": "Link",
   "price": 33
  },
  {
   "player": "Mike Evans",
   "pos": "WR",
   "team": "Farmer",
   "price": 78
  },
  {
   "player": "Tyreek Hill",
   "pos": "WR",
   "team": "Omar",
   "price": 72
  },
  {
   "player": "James Conner",
   "pos": "RB",
   "team": "Singer",
   "price": 30
  },
  {
   "player": "A.J. Brown",
   "pos": "WR",
   "team": "Nova",
   "price": 75
  },
  {
   "player": "Kyle Pitts",
   "pos": "TE",
   "team": "Rob",
   "price": 42
  },
  {
   "player": "Tee Higgins",
   "pos": "WR",
   "team": "Nova",
   "price": 64
  },
  {
   "player": "Ezekiel Elliott",
   "pos": "RB",
   "team": "Lesesne",
   "price": 90
  },
  {
   "player": "Michael Pittman Jr.",
   "pos": "WR",
   "team": "Link",
   "price": 28
  },
  {
   "player": "Josh Allen",
   "pos": "QB",
   "team": "Byrd",
   "price": 55
  },
  {
   "player": "Keenan Allen",
   "pos": "WR",
   "team": "Nova",
   "price": 53
  },
  {
   "player": "DJ Moore",
   "pos": "WR",
   "team": "Rob",
   "price": 41
  },
  {
   "player": "Mike Williams",
   "pos": "WR",
   "team": "Singer",
   "price": 57
  },
  {
   "player": "Courtland Sutton",
   "pos": "WR",
   "team": "Byrd",
   "price": 60
  },
  {
   "player": "Breece Hall",
   "pos": "RB",
   "team": "Farmer",
   "price": 86
  },
  {
   "player": "Cam Akers",
   "pos": "RB",
   "team": "Ned",
   "price": 67
  },
  {
   "player": "Terry McLaurin",
   "pos": "WR",
   "team": "Farmer",
   "price": 49
  },
  {
   "player": "Justin Herbert",
   "pos": "QB",
   "team": "Ned",
   "price": 36
  },
  {
   "player": "David Montgomery",
   "pos": "RB",
   "team": "Rob",
   "price": 48
  },
  {
   "player": "Elijah Mitchell",
   "pos": "RB",
   "team": "Crisp",
   "price": 45
  },
  {
   "player": "Jaylen Waddle",
   "pos": "WR",
   "team": "Singer",
   "price": 32
  },
  {
   "player": "Travis Etienne Jr.",
   "pos": "RB",
   "team": "Singer",
   "price": 51
  },
  {
   "player": "DK Metcalf",
   "pos": "WR",
   "team": "Farmer",
   "price": 43
  },
  {
   "player": "George Kittle",
   "pos": "TE",
   "team": "Singer",
   "price": 28
  },
  {
   "player": "J.K. Dobbins",
   "pos": "RB",
   "team": "Rob",
   "price": 60
  },
  {
   "player": "Brandin Cooks",
   "pos": "WR",
   "team": "Link",
   "price": 32
  },
  {
   "player": "Diontae Johnson",
   "pos": "WR",
   "team": "Rob",
   "price": 23
  },
  {
   "player": "Gabriel Davis",
   "pos": "WR",
   "team": "Link",
   "price": 43
  },
  {
   "player": "Darren Waller",
   "pos": "TE",
   "team": "Lesesne",
   "price": 44
  },
  {
   "player": "Patrick Mahomes II",
   "pos": "QB",
   "team": "Nova",
   "price": 55
  },
  {
   "player": "Allen Robinson II",
   "pos": "WR",
   "team": "Ned",
   "price": 37
  },
  {
   "player": "Lamar Jackson",
   "pos": "QB",
   "team": "Omar",
   "price": 26
  },
  {
   "player": "AJ Dillon",
   "pos": "RB",
   "team": "Byrd",
   "price": 56
  },
  {
   "player": "Marquise Brown",
   "pos": "WR",
   "team": "Byrd",
   "price": 19
  },
  {
   "player": "Josh Jacobs",
   "pos": "RB",
   "team": "Omar",
   "price": 45
  },
  {
   "player": "Jerry Jeudy",
   "pos": "WR",
   "team": "Omar",
   "price": 40
  },
  {
   "player": "Darnell Mooney",
   "pos": "WR",
   "team": "Byrd",
   "price": 5
  },
  {
   "player": "Kyler Murray",
   "pos": "QB",
   "team": "Singer",
   "price": 20
  },
  {
   "player": "Rashod Bateman",
   "pos": "WR",
   "team": "Nova",
   "price": 28
  },
  {
   "player": "Dalton Schultz",
   "pos": "TE",
   "team": "Omar",
   "price": 10
  },
  {
   "player": "Jalen Hurts",
   "pos": "QB",
   "team": "Farmer",
   "price": 20
  },
  {
   "player": "Damien Harris",
   "pos": "RB",
   "team": "Rob",
   "price": 49
  },
  {
   "player": "Amari Cooper",
   "pos": "WR",
   "team": "Farmer",
   "price": 12
  },
  {
   "player": "Elijah Moore",
   "pos": "WR",
   "team": "Crisp",
   "price": 4
  },
  {
   "player": "Chris Godwin",
   "pos": "WR",
   "team": "Byrd",
   "price": 8
  },
  {
   "player": "Michael Thomas",
   "pos": "WR",
   "team": "Lesesne",
   "price": 28
  },
  {
   "player": "JuJu Smith-Schuster",
   "pos": "WR",
   "team": "Omar",
   "price": 38
  },
  {
   "player": "Amon-Ra St. Brown",
   "pos": "WR",
   "team": "Ned",
   "price": 20
  },
  {
   "player": "Miles Sanders",
   "pos": "RB",
   "team": "Omar",
   "price": 20
  },
  {
   "player": "Dallas Goedert",
   "pos": "TE",
   "team": "Farmer",
   "price": 9
  },
  {
   "player": "Rashaad Penny",
   "pos": "RB",
   "team": "Farmer",
   "price": 14
  },
  {
   "player": "Clyde Edwards-Helaire",
   "pos": "RB",
   "team": "Lesesne",
   "price": 35
  },
  {
   "player": "Joe Burrow",
   "pos": "QB",
   "team": "Rob",
   "price": 25
  },
  {
   "player": "Antonio Gibson",
   "pos": "RB",
   "team": "Rob",
   "price": 26
  },
  {
   "player": "Adam Thielen",
   "pos": "WR",
   "team": "Rob",
   "price": 37
  },
  {
   "player": "Brandon Aiyuk",
   "pos": "WR",
   "team": "Link",
   "price": 11
  },
  {
   "player": "T.J. Hockenson",
   "pos": "TE",
   "team": "Ned",
   "price": 5
  },
  {
   "player": "Chase Edmonds",
   "pos": "RB",
   "team": "Crisp",
   "price": 22
  },
  {
   "player": "DeVonta Smith",
   "pos": "WR",
   "team": "Singer",
   "price": 11
  },
  {
   "player": "Allen Lazard",
   "pos": "WR",
   "team": "Omar",
   "price": 37
  },
  {
   "player": "Tom Brady",
   "pos": "QB",
   "team": "Singer",
   "price": 5
  },
  {
   "player": "Russell Wilson",
   "pos": "QB",
   "team": "Farmer",
   "price": 1
  },
  {
   "player": "Rhamondre Stevenson",
   "pos": "RB",
   "team": "Farmer",
   "price": 27
  },
  {
   "player": "Kareem Hunt",
   "pos": "RB",
   "team": "Crisp",
   "price": 17
  },
  {
   "player": "Tony Pollard",
   "pos": "RB",
   "team": "Omar",
   "price": 27
  },
  {
   "player": "Tyler Lockett",
   "pos": "WR",
   "team": "Link",
   "price": 11
  },
  {
   "player": "Dak Prescott",
   "pos": "QB",
   "team": "Omar",
   "price": 6
  },
  {
   "player": "Drake London",
   "pos": "WR",
   "team": "Ned",
   "price": 2
  },
  {
   "player": "Devin Singletary",
   "pos": "RB",
   "team": "Omar",
   "price": 37
  },
  {
   "player": "Dawson Knox",
   "pos": "TE",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "Trey Lance",
   "pos": "QB",
   "team": "Link",
   "price": 15
  },
  {
   "player": "Melvin Gordon III",
   "pos": "RB",
   "team": "Nova",
   "price": 10
  },
  {
   "player": "Christian Kirk",
   "pos": "WR",
   "team": "Ned",
   "price": 5
  },
  {
   "player": "DeAndre Hopkins",
   "pos": "WR",
   "team": "Lesesne",
   "price": 15
  },
  {
   "player": "Dameon Pierce",
   "pos": "RB",
   "team": "Link",
   "price": 22
  },
  {
   "player": "Cordarrelle Patterson",
   "pos": "RB",
   "team": "Link",
   "price": 12
  },
  {
   "player": "Zach Ertz",
   "pos": "TE",
   "team": "Omar",
   "price": 7
  },
  {
   "player": "Hunter Renfrow",
   "pos": "WR",
   "team": "Singer",
   "price": 14
  },
  {
   "player": "Ken Walker III",
   "pos": "RB",
   "team": "Ned",
   "price": 7
  },
  {
   "player": "Robert Woods",
   "pos": "WR",
   "team": "Lesesne",
   "price": 1
  },
  {
   "player": "Matthew Stafford",
   "pos": "QB",
   "team": "Crisp",
   "price": 5
  },
  {
   "player": "Aaron Rodgers",
   "pos": "QB",
   "team": "Lesesne",
   "price": 16
  },
  {
   "player": "Kadarius Toney",
   "pos": "WR",
   "team": "Byrd",
   "price": 1
  },
  {
   "player": "Chris Olave",
   "pos": "WR",
   "team": "Nova",
   "price": 2
  },
  {
   "player": "Chase Claypool",
   "pos": "WR",
   "team": "Crisp",
   "price": 7
  },
  {
   "player": "James Cook",
   "pos": "RB",
   "team": "Link",
   "price": 21
  },
  {
   "player": "Hunter Henry",
   "pos": "TE",
   "team": "Crisp",
   "price": 1
  },
  {
   "player": "Darrell Henderson Jr.",
   "pos": "RB",
   "team": "Crisp",
   "price": 9
  },
  {
   "player": "Michael Carter",
   "pos": "RB",
   "team": "Byrd",
   "price": 6
  },
  {
   "player": "James Robinson",
   "pos": "RB",
   "team": "Ned",
   "price": 6
  },
  {
   "player": "Garrett Wilson",
   "pos": "WR",
   "team": "Farmer",
   "price": 1
  },
  {
   "player": "Skyy Moore",
   "pos": "WR",
   "team": "Nova",
   "price": 4
  },
  {
   "player": "Alexander Mattison",
   "pos": "RB",
   "team": "Singer",
   "price": 5
  },
  {
   "player": "Marquez Valdes-Scantling",
   "pos": "WR",
   "team": "Lesesne",
   "price": 1
  },
  {
   "player": "Brian Robinson Jr.",
   "pos": "RB",
   "team": "Link",
   "price": 13
  },
  {
   "player": "Khalil Herbert",
   "pos": "RB",
   "team": "Singer",
   "price": 1
  },
  {
   "player": "Tyler Allgeier",
   "pos": "RB",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Raheem Mostert",
   "pos": "RB",
   "team": "Crisp",
   "price": 1
  },
  {
   "player": "Isaiah Spiller",
   "pos": "RB",
   "team": "Nova",
   "price": 2
  },
  {
   "player": "Rachaad White",
   "pos": "RB",
   "team": "Farmer",
   "price": 1
  },
  {
   "player": "Buffalo Bills",
   "pos": "DST",
   "team": "Omar",
   "price": 8
  },
  {
   "player": "Julio Jones",
   "pos": "WR",
   "team": "Lesesne",
   "price": 3
  },
  {
   "player": "Tampa Bay Buccaneers",
   "pos": "DST",
   "team": "Rob",
   "price": 3
  },
  {
   "player": "Jahan Dotson",
   "pos": "WR",
   "team": "Rob",
   "price": 2
  },
  {
   "player": "San Francisco 49ers",
   "pos": "DST",
   "team": "Singer",
   "price": 5
  },
  {
   "player": "Zamir White",
   "pos": "RB",
   "team": "Nova",
   "price": 2
  },
  {
   "player": "Indianapolis Colts",
   "pos": "DST",
   "team": "Byrd",
   "price": 1
  },
  {
   "player": "Justin Tucker",
   "pos": "K",
   "team": "Rob",
   "price": 10
  },
  {
   "player": "New Orleans Saints",
   "pos": "DST",
   "team": "Farmer",
   "price": 1
  },
  {
   "player": "New England Patriots",
   "pos": "DST",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "Los Angeles Rams",
   "pos": "DST",
   "team": "Crisp",
   "price": 1
  },
  {
   "player": "Jameson Williams",
   "pos": "WR",
   "team": "Rob",
   "price": 8
  },
  {
   "player": "Tyler Bass",
   "pos": "K",
   "team": "Link",
   "price": 2
  },
  {
   "player": "Darrel Williams",
   "pos": "RB",
   "team": "Byrd",
   "price": 2
  },
  {
   "player": "Matt Gay",
   "pos": "K",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Ronald Jones II",
   "pos": "RB",
   "team": "Lesesne",
   "price": 4
  },
  {
   "player": "Isiah Pacheco",
   "pos": "RB",
   "team": "Byrd",
   "price": 2
  },
  {
   "player": "Evan McPherson",
   "pos": "K",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "Daniel Carlson",
   "pos": "K",
   "team": "Singer",
   "price": 1
  },
  {
   "player": "Miami Dolphins",
   "pos": "DST",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Green Bay Packers",
   "pos": "DST",
   "team": "Link",
   "price": 1
  },
  {
   "player": "Harrison Butker",
   "pos": "K",
   "team": "Omar",
   "price": 4
  },
  {
   "player": "Ryan Succop",
   "pos": "K",
   "team": "Lesesne",
   "price": 1
  },
  {
   "player": "Matt Prater",
   "pos": "K",
   "team": "Farmer",
   "price": 2
  },
  {
   "player": "Pittsburgh Steelers",
   "pos": "DST",
   "team": "Lesesne",
   "price": 2
  },
  {
   "player": "Rodrigo Blankenship",
   "pos": "K",
   "team": "Byrd",
   "price": 1
  }
 ],
 "2023": [
  {
   "player": "Christian McCaffrey",
   "pos": "RB",
   "team": "Lesesne",
   "price": 165
  },
  {
   "player": "Ja'Marr Chase",
   "pos": "WR",
   "team": "Lesesne",
   "price": 150
  },
  {
   "player": "Nick Chubb",
   "pos": "RB",
   "team": "Singer",
   "price": 148
  },
  {
   "player": "Travis Kelce",
   "pos": "TE",
   "team": "Byrd",
   "price": 143
  },
  {
   "player": "Tyreek Hill",
   "pos": "WR",
   "team": "Omar",
   "price": 97
  },
  {
   "player": "Austin Ekeler",
   "pos": "RB",
   "team": "Farmer",
   "price": 142
  },
  {
   "player": "Cooper Kupp",
   "pos": "WR",
   "team": "Singer",
   "price": 78
  },
  {
   "player": "Derrick Henry",
   "pos": "RB",
   "team": "Lesesne",
   "price": 145
  },
  {
   "player": "Bijan Robinson",
   "pos": "RB",
   "team": "Link",
   "price": 199
  },
  {
   "player": "Stefon Diggs",
   "pos": "WR",
   "team": "Byrd",
   "price": 104
  },
  {
   "player": "A.J. Brown",
   "pos": "WR",
   "team": "Farmer",
   "price": 93
  },
  {
   "player": "CeeDee Lamb",
   "pos": "WR",
   "team": "Rob",
   "price": 100
  },
  {
   "player": "Tony Pollard",
   "pos": "RB",
   "team": "Rob",
   "price": 120
  },
  {
   "player": "Saquon Barkley",
   "pos": "RB",
   "team": "Nova",
   "price": 116
  },
  {
   "player": "Davante Adams",
   "pos": "WR",
   "team": "Crisp",
   "price": 77
  },
  {
   "player": "Jonathan Taylor",
   "pos": "RB",
   "team": "Ned",
   "price": 90
  },
  {
   "player": "Amon-Ra St. Brown",
   "pos": "WR",
   "team": "Nova",
   "price": 70
  },
  {
   "player": "Garrett Wilson",
   "pos": "WR",
   "team": "Byrd",
   "price": 73
  },
  {
   "player": "Josh Jacobs",
   "pos": "RB",
   "team": "Omar",
   "price": 70
  },
  {
   "player": "Jaylen Waddle",
   "pos": "WR",
   "team": "Singer",
   "price": 85
  },
  {
   "player": "Patrick Mahomes II",
   "pos": "QB",
   "team": "Omar",
   "price": 70
  },
  {
   "player": "Chris Olave",
   "pos": "WR",
   "team": "Nova",
   "price": 27
  },
  {
   "player": "Jalen Hurts",
   "pos": "QB",
   "team": "Link",
   "price": 45
  },
  {
   "player": "Josh Allen",
   "pos": "QB",
   "team": "Byrd",
   "price": 66
  },
  {
   "player": "Tee Higgins",
   "pos": "WR",
   "team": "Omar",
   "price": 58
  },
  {
   "player": "Najee Harris",
   "pos": "RB",
   "team": "Crisp",
   "price": 72
  },
  {
   "player": "Joe Mixon",
   "pos": "RB",
   "team": "Farmer",
   "price": 106
  },
  {
   "player": "Travis Etienne Jr.",
   "pos": "RB",
   "team": "Ned",
   "price": 85
  },
  {
   "player": "Rhamondre Stevenson",
   "pos": "RB",
   "team": "Farmer",
   "price": 46
  },
  {
   "player": "Amari Cooper",
   "pos": "WR",
   "team": "Link",
   "price": 37
  },
  {
   "player": "DeVonta Smith",
   "pos": "WR",
   "team": "Link",
   "price": 56
  },
  {
   "player": "Deebo Samuel",
   "pos": "WR",
   "team": "Crisp",
   "price": 56
  },
  {
   "player": "Mark Andrews",
   "pos": "TE",
   "team": "Rob",
   "price": 64
  },
  {
   "player": "DK Metcalf",
   "pos": "WR",
   "team": "Ned",
   "price": 43
  },
  {
   "player": "Lamar Jackson",
   "pos": "QB",
   "team": "Rob",
   "price": 52
  },
  {
   "player": "Jahmyr Gibbs",
   "pos": "RB",
   "team": "Link",
   "price": 65
  },
  {
   "player": "Calvin Ridley",
   "pos": "WR",
   "team": "Byrd",
   "price": 53
  },
  {
   "player": "Aaron Jones",
   "pos": "RB",
   "team": "Crisp",
   "price": 68
  },
  {
   "player": "Kenneth Walker III",
   "pos": "RB",
   "team": "Nova",
   "price": 49
  },
  {
   "player": "Joe Burrow",
   "pos": "QB",
   "team": "Lesesne",
   "price": 20
  },
  {
   "player": "DJ Moore",
   "pos": "WR",
   "team": "Singer",
   "price": 32
  },
  {
   "player": "Breece Hall",
   "pos": "RB",
   "team": "Farmer",
   "price": 41
  },
  {
   "player": "Justin Fields",
   "pos": "QB",
   "team": "Singer",
   "price": 44
  },
  {
   "player": "Miles Sanders",
   "pos": "RB",
   "team": "Rob",
   "price": 40
  },
  {
   "player": "Christian Watson",
   "pos": "WR",
   "team": "Link",
   "price": 35
  },
  {
   "player": "Justin Herbert",
   "pos": "QB",
   "team": "Nova",
   "price": 18
  },
  {
   "player": "Jerry Jeudy",
   "pos": "WR",
   "team": "Omar",
   "price": 32
  },
  {
   "player": "Keenan Allen",
   "pos": "WR",
   "team": "Nova",
   "price": 19
  },
  {
   "player": "J.K. Dobbins",
   "pos": "RB",
   "team": "Crisp",
   "price": 38
  },
  {
   "player": "Cam Akers",
   "pos": "RB",
   "team": "Rob",
   "price": 34
  },
  {
   "player": "Terry McLaurin",
   "pos": "WR",
   "team": "Farmer",
   "price": 28
  },
  {
   "player": "Alexander Mattison",
   "pos": "RB",
   "team": "Singer",
   "price": 30
  },
  {
   "player": "Dameon Pierce",
   "pos": "RB",
   "team": "Omar",
   "price": 44
  },
  {
   "player": "DeAndre Hopkins",
   "pos": "WR",
   "team": "Farmer",
   "price": 19
  },
  {
   "player": "Brandon Aiyuk",
   "pos": "WR",
   "team": "Singer",
   "price": 18
  },
  {
   "player": "Drake London",
   "pos": "WR",
   "team": "Omar",
   "price": 16
  },
  {
   "player": "Mike Williams",
   "pos": "WR",
   "team": "Crisp",
   "price": 29
  },
  {
   "player": "James Conner",
   "pos": "RB",
   "team": "Omar",
   "price": 28
  },
  {
   "player": "Trevor Lawrence",
   "pos": "QB",
   "team": "Ned",
   "price": 13
  },
  {
   "player": "T.J. Hockenson",
   "pos": "TE",
   "team": "Nova",
   "price": 22
  },
  {
   "player": "Tyler Lockett",
   "pos": "WR",
   "team": "Omar",
   "price": 9
  },
  {
   "player": "Christian Kirk",
   "pos": "WR",
   "team": "Nova",
   "price": 3
  },
  {
   "player": "Mike Evans",
   "pos": "WR",
   "team": "Omar",
   "price": 13
  },
  {
   "player": "David Montgomery",
   "pos": "RB",
   "team": "Rob",
   "price": 15
  },
  {
   "player": "Chris Godwin",
   "pos": "WR",
   "team": "Rob",
   "price": 5
  },
  {
   "player": "Isiah Pacheco",
   "pos": "RB",
   "team": "Byrd",
   "price": 27
  },
  {
   "player": "Rachaad White",
   "pos": "RB",
   "team": "Omar",
   "price": 26
  },
  {
   "player": "Javonte Williams",
   "pos": "RB",
   "team": "Ned",
   "price": 25
  },
  {
   "player": "James Cook",
   "pos": "RB",
   "team": "Nova",
   "price": 52
  },
  {
   "player": "Diontae Johnson",
   "pos": "WR",
   "team": "Ned",
   "price": 25
  },
  {
   "player": "Alvin Kamara",
   "pos": "RB",
   "team": "Byrd",
   "price": 39
  },
  {
   "player": "George Kittle",
   "pos": "TE",
   "team": "Ned",
   "price": 19
  },
  {
   "player": "Marquise Brown",
   "pos": "WR",
   "team": "Byrd",
   "price": 3
  },
  {
   "player": "Darren Waller",
   "pos": "TE",
   "team": "Singer",
   "price": 28
  },
  {
   "player": "Jahan Dotson",
   "pos": "WR",
   "team": "Rob",
   "price": 24
  },
  {
   "player": "Dalvin Cook",
   "pos": "RB",
   "team": "Lesesne",
   "price": 21
  },
  {
   "player": "George Pickens",
   "pos": "WR",
   "team": "Crisp",
   "price": 24
  },
  {
   "player": "Michael Pittman Jr.",
   "pos": "WR",
   "team": "Singer",
   "price": 9
  },
  {
   "player": "D'Andre Swift",
   "pos": "RB",
   "team": "Lesesne",
   "price": 36
  },
  {
   "player": "Gabe Davis",
   "pos": "WR",
   "team": "Link",
   "price": 9
  },
  {
   "player": "Khalil Herbert",
   "pos": "RB",
   "team": "Byrd",
   "price": 31
  },
  {
   "player": "Kyle Pitts",
   "pos": "TE",
   "team": "Lesesne",
   "price": 22
  },
  {
   "player": "Brian Robinson Jr.",
   "pos": "RB",
   "team": "Farmer",
   "price": 16
  },
  {
   "player": "Deshaun Watson",
   "pos": "QB",
   "team": "Farmer",
   "price": 3
  },
  {
   "player": "Jordan Addison",
   "pos": "WR",
   "team": "Ned",
   "price": 10
  },
  {
   "player": "AJ Dillon",
   "pos": "RB",
   "team": "Rob",
   "price": 10
  },
  {
   "player": "Dallas Goedert",
   "pos": "TE",
   "team": "Farmer",
   "price": 31
  },
  {
   "player": "Jaxon Smith-Njigba",
   "pos": "WR",
   "team": "Byrd",
   "price": 11
  },
  {
   "player": "Brandin Cooks",
   "pos": "WR",
   "team": "Singer",
   "price": 1
  },
  {
   "player": "Tua Tagovailoa",
   "pos": "QB",
   "team": "Farmer",
   "price": 6
  },
  {
   "player": "Courtland Sutton",
   "pos": "WR",
   "team": "Byrd",
   "price": 6
  },
  {
   "player": "Antonio Gibson",
   "pos": "RB",
   "team": "Byrd",
   "price": 29
  },
  {
   "player": "Rashaad Penny",
   "pos": "RB",
   "team": "Rob",
   "price": 7
  },
  {
   "player": "Kirk Cousins",
   "pos": "QB",
   "team": "Crisp",
   "price": 1
  },
  {
   "player": "Geno Smith",
   "pos": "QB",
   "team": "Crisp",
   "price": 1
  },
  {
   "player": "Jamaal Williams",
   "pos": "RB",
   "team": "Nova",
   "price": 15
  },
  {
   "player": "Zay Flowers",
   "pos": "WR",
   "team": "Crisp",
   "price": 14
  },
  {
   "player": "Samaje Perine",
   "pos": "RB",
   "team": "Crisp",
   "price": 6
  },
  {
   "player": "Zach Charbonnet",
   "pos": "RB",
   "team": "Omar",
   "price": 14
  },
  {
   "player": "Michael Thomas",
   "pos": "WR",
   "team": "Lesesne",
   "price": 5
  },
  {
   "player": "Pat Freiermuth",
   "pos": "TE",
   "team": "Crisp",
   "price": 9
  },
  {
   "player": "Kadarius Toney",
   "pos": "WR",
   "team": "Lesesne",
   "price": 14
  },
  {
   "player": "Anthony Richardson",
   "pos": "QB",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Elijah Mitchell",
   "pos": "RB",
   "team": "Lesesne",
   "price": 8
  },
  {
   "player": "Evan Engram",
   "pos": "TE",
   "team": "Omar",
   "price": 5
  },
  {
   "player": "Skyy Moore",
   "pos": "WR",
   "team": "Link",
   "price": 12
  },
  {
   "player": "JuJu Smith-Schuster",
   "pos": "WR",
   "team": "Lesesne",
   "price": 1
  },
  {
   "player": "Aaron Rodgers",
   "pos": "QB",
   "team": "Rob",
   "price": 8
  },
  {
   "player": "Tyler Allgeier",
   "pos": "RB",
   "team": "Link",
   "price": 10
  },
  {
   "player": "Jeff Wilson Jr.",
   "pos": "RB",
   "team": "Nova",
   "price": 3
  },
  {
   "player": "Raheem Mostert",
   "pos": "RB",
   "team": "Singer",
   "price": 2
  },
  {
   "player": "De'Von Achane",
   "pos": "RB",
   "team": "Byrd",
   "price": 9
  },
  {
   "player": "Jameson Williams",
   "pos": "WR",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Odell Beckham Jr.",
   "pos": "WR",
   "team": "Lesesne",
   "price": 8
  },
  {
   "player": "Jerick McKinnon",
   "pos": "RB",
   "team": "Link",
   "price": 5
  },
  {
   "player": "Ezekiel Elliott",
   "pos": "RB",
   "team": "Farmer",
   "price": 2
  },
  {
   "player": "Jaylen Warren",
   "pos": "RB",
   "team": "Singer",
   "price": 13
  },
  {
   "player": "DJ Chark Jr.",
   "pos": "WR",
   "team": "Singer",
   "price": 1
  },
  {
   "player": "Romeo Doubs",
   "pos": "WR",
   "team": "Farmer",
   "price": 7
  },
  {
   "player": "Tank Bigsby",
   "pos": "RB",
   "team": "Rob",
   "price": 5
  },
  {
   "player": "Adam Thielen",
   "pos": "WR",
   "team": "Lesesne",
   "price": 1
  },
  {
   "player": "Gus Edwards",
   "pos": "RB",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "San Francisco 49ers",
   "pos": "DST",
   "team": "Farmer",
   "price": 24
  },
  {
   "player": "Dallas Cowboys",
   "pos": "DST",
   "team": "Singer",
   "price": 2
  },
  {
   "player": "Philadelphia Eagles",
   "pos": "DST",
   "team": "Lesesne",
   "price": 2
  },
  {
   "player": "Justin Tucker",
   "pos": "K",
   "team": "Omar",
   "price": 4
  },
  {
   "player": "Buffalo Bills",
   "pos": "DST",
   "team": "Omar",
   "price": 10
  },
  {
   "player": "Marquez Valdes-Scantling",
   "pos": "WR",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "Tyler Bass",
   "pos": "K",
   "team": "Farmer",
   "price": 2
  },
  {
   "player": "New England Patriots",
   "pos": "DST",
   "team": "Link",
   "price": 2
  },
  {
   "player": "Jonathan Mingo",
   "pos": "WR",
   "team": "Crisp",
   "price": 3
  },
  {
   "player": "New York Jets",
   "pos": "DST",
   "team": "Link",
   "price": 2
  },
  {
   "player": "Harrison Butker",
   "pos": "K",
   "team": "Singer",
   "price": 2
  },
  {
   "player": "Evan McPherson",
   "pos": "K",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Tyjae Spears",
   "pos": "RB",
   "team": "Link",
   "price": 1
  },
  {
   "player": "Baltimore Ravens",
   "pos": "DST",
   "team": "Nova",
   "price": 2
  },
  {
   "player": "Daniel Carlson",
   "pos": "K",
   "team": "Lesesne",
   "price": 2
  },
  {
   "player": "John Metchie III",
   "pos": "WR",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Denver Broncos",
   "pos": "DST",
   "team": "Ned",
   "price": 1
  },
  {
   "player": "Pittsburgh Steelers",
   "pos": "DST",
   "team": "Byrd",
   "price": 2
  },
  {
   "player": "Younghoe Koo",
   "pos": "K",
   "team": "Rob",
   "price": 14
  },
  {
   "player": "Jason Sanders",
   "pos": "K",
   "team": "Byrd",
   "price": 4
  },
  {
   "player": "Brandon McManus",
   "pos": "K",
   "team": "Nova",
   "price": 1
  },
  {
   "player": "Jake Elliott",
   "pos": "K",
   "team": "Link",
   "price": 10
  },
  {
   "player": "Cleveland Browns",
   "pos": "DST",
   "team": "Rob",
   "price": 2
  },
  {
   "player": "Greg Joseph",
   "pos": "K",
   "team": "Crisp",
   "price": 1
  },
  {
   "player": "Indianapolis Colts",
   "pos": "DST",
   "team": "Crisp",
   "price": 1
  },
  {
   "player": "Luke Musgrave",
   "pos": "TE",
   "team": "Link",
   "price": 1
  }
 ],
 "2024": [
  {
   "player": "Christian McCaffrey",
   "pos": "RB",
   "team": "Lesesne",
   "price": 190,
   "keeper": True
  },
  {
   "player": "Bijan Robinson",
   "pos": "RB",
   "team": "Byrd",
   "price": 183
  },
  {
   "player": "Saquon Barkley",
   "pos": "RB",
   "team": "Nova",
   "price": 141,
   "keeper": True
  },
  {
   "player": "Jonathan Taylor",
   "pos": "RB",
   "team": "Link",
   "price": 130
  },
  {
   "player": "Ja'Marr Chase",
   "pos": "WR",
   "team": "Omar",
   "price": 126
  },
  {
   "player": "CeeDee Lamb",
   "pos": "WR",
   "team": "Rob",
   "price": 125,
   "keeper": True
  },
  {
   "player": "Tyreek Hill",
   "pos": "WR",
   "team": "Ned",
   "price": 122,
   "keeper": True
  },
  {
   "player": "Kyren Williams",
   "pos": "RB",
   "team": "Crisp",
   "price": 120
  },
  {
   "player": "A.J. Brown",
   "pos": "WR",
   "team": "Farmer",
   "price": 118,
   "keeper": True
  },
  {
   "player": "Justin Jefferson",
   "pos": "WR",
   "team": "Lesesne",
   "price": 105,
   "keeper": True
  },
  {
   "player": "Garrett Wilson",
   "pos": "WR",
   "team": "Ned",
   "price": 105
  },
  {
   "player": "Isiah Pacheco",
   "pos": "RB",
   "team": "Crisp",
   "price": 105
  },
  {
   "player": "Travis Etienne Jr.",
   "pos": "RB",
   "team": "Omar",
   "price": 96
  },
  {
   "player": "Amon-Ra St. Brown",
   "pos": "WR",
   "team": "Nova",
   "price": 95,
   "keeper": True
  },
  {
   "player": "Marvin Harrison Jr.",
   "pos": "WR",
   "team": "Crisp",
   "price": 92
  },
  {
   "player": "Derrick Henry",
   "pos": "RB",
   "team": "Singer",
   "price": 90
  },
  {
   "player": "Jahmyr Gibbs",
   "pos": "RB",
   "team": "Link",
   "price": 90,
   "keeper": True
  },
  {
   "player": "Deebo Samuel Sr.",
   "pos": "WR",
   "team": "Crisp",
   "price": 81,
   "keeper": True
  },
  {
   "player": "Drake London",
   "pos": "WR",
   "team": "Byrd",
   "price": 81
  },
  {
   "player": "Travis Kelce",
   "pos": "TE",
   "team": "Link",
   "price": 75
  },
  {
   "player": "James Cook",
   "pos": "RB",
   "team": "Rob",
   "price": 75
  },
  {
   "player": "Puka Nacua",
   "pos": "WR",
   "team": "Omar",
   "price": 73
  },
  {
   "player": "Joe Mixon",
   "pos": "RB",
   "team": "Link",
   "price": 73
  },
  {
   "player": "Josh Jacobs",
   "pos": "RB",
   "team": "Singer",
   "price": 71
  },
  {
   "player": "Breece Hall",
   "pos": "RB",
   "team": "Farmer",
   "price": 66,
   "keeper": True
  },
  {
   "player": "Cooper Kupp",
   "pos": "WR",
   "team": "Ned",
   "price": 65
  },
  {
   "player": "Kenneth Walker III",
   "pos": "RB",
   "team": "Ned",
   "price": 65
  },
  {
   "player": "Josh Allen",
   "pos": "QB",
   "team": "Byrd",
   "price": 61
  },
  {
   "player": "Nico Collins",
   "pos": "WR",
   "team": "Singer",
   "price": 60
  },
  {
   "player": "Malik Nabers",
   "pos": "WR",
   "team": "Lesesne",
   "price": 60
  },
  {
   "player": "Jalen Hurts",
   "pos": "QB",
   "team": "Rob",
   "price": 55
  },
  {
   "player": "Sam LaPorta",
   "pos": "TE",
   "team": "Omar",
   "price": 55
  },
  {
   "player": "Tee Higgins",
   "pos": "WR",
   "team": "Rob",
   "price": 55
  },
  {
   "player": "Trey McBride",
   "pos": "TE",
   "team": "Byrd",
   "price": 55
  },
  {
   "player": "Chris Olave",
   "pos": "WR",
   "team": "Link",
   "price": 52,
   "keeper": True
  },
  {
   "player": "Rachaad White",
   "pos": "RB",
   "team": "Omar",
   "price": 51,
   "keeper": True
  },
  {
   "player": "DK Metcalf",
   "pos": "WR",
   "team": "Omar",
   "price": 50
  },
  {
   "player": "Jaylen Waddle",
   "pos": "WR",
   "team": "Farmer",
   "price": 50
  },
  {
   "player": "Brian Robinson Jr.",
   "pos": "RB",
   "team": "Farmer",
   "price": 50
  },
  {
   "player": "DJ Moore",
   "pos": "WR",
   "team": "Farmer",
   "price": 45
  },
  {
   "player": "Mark Andrews",
   "pos": "TE",
   "team": "Rob",
   "price": 45
  },
  {
   "player": "Michael Pittman Jr.",
   "pos": "WR",
   "team": "Singer",
   "price": 45
  },
  {
   "player": "Brandon Aiyuk",
   "pos": "WR",
   "team": "Singer",
   "price": 43,
   "keeper": True
  },
  {
   "player": "Zamir White",
   "pos": "RB",
   "team": "Nova",
   "price": 43
  },
  {
   "player": "Davante Adams",
   "pos": "WR",
   "team": "Nova",
   "price": 41
  },
  {
   "player": "Rashee Rice",
   "pos": "WR",
   "team": "Farmer",
   "price": 41
  },
  {
   "player": "James Conner",
   "pos": "RB",
   "team": "Ned",
   "price": 40
  },
  {
   "player": "Aaron Jones",
   "pos": "RB",
   "team": "Crisp",
   "price": 40
  },
  {
   "player": "Dalton Kincaid",
   "pos": "TE",
   "team": "Singer",
   "price": 39
  },
  {
   "player": "Mike Evans",
   "pos": "WR",
   "team": "Omar",
   "price": 38,
   "keeper": True
  },
  {
   "player": "Alvin Kamara",
   "pos": "RB",
   "team": "Farmer",
   "price": 37
  },
  {
   "player": "George Pickens",
   "pos": "WR",
   "team": "Rob",
   "price": 35
  },
  {
   "player": "Patrick Mahomes II",
   "pos": "QB",
   "team": "Singer",
   "price": 34
  },
  {
   "player": "De'Von Achane",
   "pos": "RB",
   "team": "Byrd",
   "price": 34,
   "keeper": True
  },
  {
   "player": "DeVonta Smith",
   "pos": "WR",
   "team": "Byrd",
   "price": 34
  },
  {
   "player": "Najee Harris",
   "pos": "RB",
   "team": "Omar",
   "price": 33
  },
  {
   "player": "Lamar Jackson",
   "pos": "QB",
   "team": "Byrd",
   "price": 30
  },
  {
   "player": "Zay Flowers",
   "pos": "WR",
   "team": "Rob",
   "price": 30
  },
  {
   "player": "Tony Pollard",
   "pos": "RB",
   "team": "Link",
   "price": 30
  },
  {
   "player": "David Montgomery",
   "pos": "RB",
   "team": "Link",
   "price": 28
  },
  {
   "player": "Amari Cooper",
   "pos": "WR",
   "team": "Crisp",
   "price": 27
  },
  {
   "player": "Raheem Mostert",
   "pos": "RB",
   "team": "Singer",
   "price": 27,
   "keeper": True
  },
  {
   "player": "Anthony Richardson",
   "pos": "QB",
   "team": "Ned",
   "price": 26,
   "keeper": True
  },
  {
   "player": "Javonte Williams",
   "pos": "RB",
   "team": "Singer",
   "price": 26
  },
  {
   "player": "Chase Brown",
   "pos": "RB",
   "team": "Nova",
   "price": 25
  },
  {
   "player": "C.J. Stroud",
   "pos": "QB",
   "team": "Nova",
   "price": 23
  },
  {
   "player": "D'Andre Swift",
   "pos": "RB",
   "team": "Rob",
   "price": 22
  },
  {
   "player": "Zack Moss",
   "pos": "RB",
   "team": "Rob",
   "price": 22
  },
  {
   "player": "Xavier Worthy",
   "pos": "WR",
   "team": "Singer",
   "price": 21
  },
  {
   "player": "Terry McLaurin",
   "pos": "WR",
   "team": "Omar",
   "price": 20
  },
  {
   "player": "Jordan Love",
   "pos": "QB",
   "team": "Link",
   "price": 20
  },
  {
   "player": "George Kittle",
   "pos": "TE",
   "team": "Omar",
   "price": 20
  },
  {
   "player": "Jonathon Brooks",
   "pos": "RB",
   "team": "Link",
   "price": 20
  },
  {
   "player": "Nick Chubb",
   "pos": "RB",
   "team": "Ned",
   "price": 20
  },
  {
   "player": "Tank Dell",
   "pos": "WR",
   "team": "Farmer",
   "price": 18
  },
  {
   "player": "Rhamondre Stevenson",
   "pos": "RB",
   "team": "Omar",
   "price": 18
  },
  {
   "player": "Calvin Ridley",
   "pos": "WR",
   "team": "Singer",
   "price": 18
  },
  {
   "player": "Brock Bowers",
   "pos": "TE",
   "team": "Ned",
   "price": 17
  },
  {
   "player": "Stefon Diggs",
   "pos": "WR",
   "team": "Byrd",
   "price": 15
  },
  {
   "player": "Christian Watson",
   "pos": "WR",
   "team": "Nova",
   "price": 14
  },
  {
   "player": "Devin Singletary",
   "pos": "RB",
   "team": "Nova",
   "price": 14
  },
  {
   "player": "Keon Coleman",
   "pos": "WR",
   "team": "Nova",
   "price": 14
  },
  {
   "player": "Jayden Daniels",
   "pos": "QB",
   "team": "Lesesne",
   "price": 13
  },
  {
   "player": "Younghoe Koo",
   "pos": "K",
   "team": "Rob",
   "price": 13
  },
  {
   "player": "Kyler Murray",
   "pos": "QB",
   "team": "Crisp",
   "price": 12
  },
  {
   "player": "Diontae Johnson",
   "pos": "WR",
   "team": "Nova",
   "price": 12
  },
  {
   "player": "Jake Ferguson",
   "pos": "TE",
   "team": "Farmer",
   "price": 12
  },
  {
   "player": "Jerome Ford",
   "pos": "RB",
   "team": "Ned",
   "price": 12
  },
  {
   "player": "J.K. Dobbins",
   "pos": "RB",
   "team": "Ned",
   "price": 12
  },
  {
   "player": "Joe Burrow",
   "pos": "QB",
   "team": "Omar",
   "price": 11
  },
  {
   "player": "Kyle Pitts",
   "pos": "TE",
   "team": "Farmer",
   "price": 11
  },
  {
   "player": "Jayden Reed",
   "pos": "WR",
   "team": "Link",
   "price": 10
  },
  {
   "player": "Jaylen Warren",
   "pos": "RB",
   "team": "Lesesne",
   "price": 10
  },
  {
   "player": "Gus Edwards",
   "pos": "RB",
   "team": "Crisp",
   "price": 10
  },
  {
   "player": "Ezekiel Elliott",
   "pos": "RB",
   "team": "Farmer",
   "price": 10
  },
  {
   "player": "Trey Benson",
   "pos": "RB",
   "team": "Nova",
   "price": 10
  },
  {
   "player": "Rico Dowdle",
   "pos": "RB",
   "team": "Singer",
   "price": 9
  },
  {
   "player": "Christian Kirk",
   "pos": "WR",
   "team": "Byrd",
   "price": 8
  },
  {
   "player": "Rome Odunze",
   "pos": "WR",
   "team": "Link",
   "price": 8
  },
  {
   "player": "Tyjae Spears",
   "pos": "RB",
   "team": "Lesesne",
   "price": 8
  },
  {
   "player": "Blake Corum",
   "pos": "RB",
   "team": "Byrd",
   "price": 7
  },
  {
   "player": "Keenan Allen",
   "pos": "WR",
   "team": "Nova",
   "price": 5
  },
  {
   "player": "DeAndre Hopkins",
   "pos": "WR",
   "team": "Ned",
   "price": 5
  },
  {
   "player": "Jaxon Smith-Njigba",
   "pos": "WR",
   "team": "Link",
   "price": 5
  },
  {
   "player": "Brian Thomas Jr.",
   "pos": "WR",
   "team": "Rob",
   "price": 5
  },
  {
   "player": "Houston Texans",
   "pos": "DST",
   "team": "Rob",
   "price": 5
  },
  {
   "player": "Chris Godwin",
   "pos": "WR",
   "team": "Link",
   "price": 4
  },
  {
   "player": "Evan Engram",
   "pos": "TE",
   "team": "Nova",
   "price": 4
  },
  {
   "player": "Ladd McConkey",
   "pos": "WR",
   "team": "Lesesne",
   "price": 4
  },
  {
   "player": "Baltimore Ravens",
   "pos": "DST",
   "team": "Farmer",
   "price": 4
  },
  {
   "player": "Ray Davis",
   "pos": "RB",
   "team": "Crisp",
   "price": 4
  },
  {
   "player": "Caleb Williams",
   "pos": "QB",
   "team": "Omar",
   "price": 3
  },
  {
   "player": "Trevor Lawrence",
   "pos": "QB",
   "team": "Rob",
   "price": 3
  },
  {
   "player": "David Njoku",
   "pos": "TE",
   "team": "Singer",
   "price": 3
  },
  {
   "player": "Jaleel McLaughlin",
   "pos": "RB",
   "team": "Crisp",
   "price": 3
  },
  {
   "player": "MarShawn Lloyd",
   "pos": "RB",
   "team": "Byrd",
   "price": 3
  },
  {
   "player": "Elijah Mitchell",
   "pos": "RB",
   "team": "Ned",
   "price": 3
  },
  {
   "player": "Justin Tucker",
   "pos": "K",
   "team": "Link",
   "price": 3
  },
  {
   "player": "Brandon Aubrey",
   "pos": "K",
   "team": "Farmer",
   "price": 3
  },
  {
   "player": "Harrison Butker",
   "pos": "K",
   "team": "Omar",
   "price": 3
  },
  {
   "player": "Chicago Bears",
   "pos": "DST",
   "team": "Omar",
   "price": 3
  },
  {
   "player": "Dak Prescott",
   "pos": "QB",
   "team": "Farmer",
   "price": 2
  },
  {
   "player": "Tua Tagovailoa",
   "pos": "QB",
   "team": "Farmer",
   "price": 2
  },
  {
   "player": "Hollywood Brown",
   "pos": "WR",
   "team": "Rob",
   "price": 2
  },
  {
   "player": "Jameson Williams",
   "pos": "WR",
   "team": "Lesesne",
   "price": 2
  },
  {
   "player": "San Francisco 49ers",
   "pos": "DST",
   "team": "Lesesne",
   "price": 2
  },
  {
   "player": "New York Jets",
   "pos": "DST",
   "team": "Link",
   "price": 2
  },
  {
   "player": "Dallas Cowboys",
   "pos": "DST",
   "team": "Singer",
   "price": 2
  },
  {
   "player": "Cleveland Browns",
   "pos": "DST",
   "team": "Nova",
   "price": 2
  },
  {
   "player": "Jake Moody",
   "pos": "K",
   "team": "Nova",
   "price": 2
  },
  {
   "player": "Brock Purdy",
   "pos": "QB",
   "team": "Lesesne",
   "price": 9
  },
  {
   "player": "Courtland Sutton",
   "pos": "WR",
   "team": "Lesesne",
   "price": 17
  },
  {
   "player": "Dallas Goedert",
   "pos": "TE",
   "team": "Crisp",
   "price": 5
  },
  {
   "player": "Austin Ekeler",
   "pos": "RB",
   "team": "Lesesne",
   "price": 3
  },
  {
   "player": "Dalton Schultz",
   "pos": "TE",
   "team": "Lesesne",
   "price": 26
  },
  {
   "player": "Joshua Palmer",
   "pos": "WR",
   "team": "Ned",
   "price": 5
  },
  {
   "player": "Brandin Cooks",
   "pos": "WR",
   "team": "Lesesne",
   "price": 7
  },
  {
   "player": "Zach Charbonnet",
   "pos": "RB",
   "team": "Byrd",
   "price": 10
  },
  {
   "player": "Tyler Allgeier",
   "pos": "RB",
   "team": "Byrd",
   "price": 12
  },
  {
   "player": "Jerry Jeudy",
   "pos": "WR",
   "team": "Rob",
   "price": 24
  },
  {
   "player": "Jaylen Wright",
   "pos": "RB",
   "team": "Crisp",
   "price": 6
  },
  {
   "player": "Kansas City Chiefs",
   "pos": "DST",
   "team": "Crisp",
   "price": 6
  },
  {
   "player": "Pittsburgh Steelers",
   "pos": "DST",
   "team": "Ned",
   "price": 72
  },
  {
   "player": "Philadelphia Eagles",
   "pos": "DST",
   "team": "Byrd",
   "price": 64
  },
  {
   "player": "Ricky Pearsall",
   "pos": "WR",
   "team": "Crisp",
   "price": 9
  },
  {
   "player": "Jason Sanders",
   "pos": "K",
   "team": "Byrd",
   "price": 6
  },
  {
   "player": "Ka'imi Fairbairn",
   "pos": "K",
   "team": "Ned",
   "price": 14
  },
  {
   "player": "Jake Elliott",
   "pos": "K",
   "team": "Crisp",
   "price": 33
  },
  {
   "player": "Tyler Bass",
   "pos": "K",
   "team": "Singer",
   "price": 12
  },
  {
   "player": "Cameron Dicker",
   "pos": "K",
   "team": "Lesesne",
   "price": 5
  }
 ]
}
