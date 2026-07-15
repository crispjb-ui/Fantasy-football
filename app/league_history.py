"""League UNC complete history (2006-2025), bundled for the copilot.
Transcribed from ESPN final-standings screenshots; champions verified against
the physical Champions Club plaque. Final rank = post-playoff placement."""

FORMULA = 'score = 2 x (10 - avg finish) + 3 x titles + 0.5 x top-3 finishes. Computed independently by Claude (AI) from the 2007-2025 ESPN final standings plus the plaque-confirmed 2006 title; no manager input. Avg finish is the spine (sustained quality, 19 seasons); titles weigh 3 because they are what the league plays for; top-3s reward contention. 2006 counts as a title but has no standings, so it cannot feed avg finish.'

FOUNDED = 2006

STANDINGS = {
 "2007": [
  {
   "rank": 1,
   "team": "Charm City Smash",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "7-4-2",
   "pf": 1231,
   "pa": 1243
  },
  {
   "rank": 2,
   "team": "Dirty Jerz",
   "manager": "Timothy Martin",
   "key": "Martin",
   "rec": "8-4-1",
   "pf": 1346,
   "pa": 1125
  },
  {
   "rank": 3,
   "team": "THE FORMER CHAMP",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "7-6",
   "pf": 1174,
   "pa": 1239
  },
  {
   "rank": 4,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "8-5",
   "pf": 1310,
   "pa": 1148
  },
  {
   "rank": 5,
   "team": "Sydney Swishas",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "6-7",
   "pf": 1119,
   "pa": 1074
  },
  {
   "rank": 6,
   "team": "QC Pacman's Posse",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "7-6",
   "pf": 1270,
   "pa": 1182
  },
  {
   "rank": 7,
   "team": "Team nagji",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "8-5",
   "pf": 1211,
   "pa": 1165
  },
  {
   "rank": 8,
   "team": "Team McCants",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "4-8-1",
   "pf": 998,
   "pa": 1119
  },
  {
   "rank": 9,
   "team": "Middle Age Mom Affair",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "3-9-1",
   "pf": 1032,
   "pa": 1266
  },
  {
   "rank": 10,
   "team": "The Big Nizzles",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "4-8-1",
   "pf": 1159,
   "pa": 1289
  }
 ],
 "2008": [
  {
   "rank": 1,
   "team": "Bronco Bound",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "7-5-1",
   "pf": 1161,
   "pa": 1098
  },
  {
   "rank": 2,
   "team": "Pee In Your Anus",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "11-2",
   "pf": 1335,
   "pa": 1096
  },
  {
   "rank": 3,
   "team": "Kent Street Cartel",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "6-6-1",
   "pf": 1299,
   "pa": 1184
  },
  {
   "rank": 4,
   "team": "The Ral-Dawgs",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "8-5",
   "pf": 1146,
   "pa": 1086
  },
  {
   "rank": 5,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "7-5-1",
   "pf": 1109,
   "pa": 1137
  },
  {
   "rank": 6,
   "team": "Curry's Sauce",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "6-6-1",
   "pf": 1151,
   "pa": 1184
  },
  {
   "rank": 7,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "6-7",
   "pf": 1086,
   "pa": 1110
  },
  {
   "rank": 8,
   "team": "The Big Nizzles",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "4-9",
   "pf": 1047,
   "pa": 1102
  },
  {
   "rank": 9,
   "team": "Attila's Huns",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "5-8",
   "pf": 1107,
   "pa": 1196
  },
  {
   "rank": 10,
   "team": "C-BUStin' Nuts",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "3-10",
   "pf": 1076,
   "pa": 1324
  }
 ],
 "2009": [
  {
   "rank": 1,
   "team": "Living Legends",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "10-3",
   "pf": 1389.3,
   "pa": 1290.5
  },
  {
   "rank": 2,
   "team": "Ben RapedHerBerger",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "9-4",
   "pf": 1303.1,
   "pa": 1236.6
  },
  {
   "rank": 3,
   "team": "Dirty Sanchez",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "6-7",
   "pf": 1328.2,
   "pa": 1404.1
  },
  {
   "rank": 4,
   "team": "Oops I Came In Yia Yia",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "8-5",
   "pf": 1210.1,
   "pa": 1182.0
  },
  {
   "rank": 5,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "6-7",
   "pf": 1403.9,
   "pa": 1348.4
  },
  {
   "rank": 6,
   "team": "I Got You A Dental Dam",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "8-5",
   "pf": 1419.5,
   "pa": 1260.1
  },
  {
   "rank": 7,
   "team": "The XXX Champs",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "6-7",
   "pf": 1278.5,
   "pa": 1293.0
  },
  {
   "rank": 8,
   "team": "El Poopo Squado",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "5-8",
   "pf": 1309.9,
   "pa": 1330.1
  },
  {
   "rank": 9,
   "team": "Replace Nizzle After Fueling",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "2-11",
   "pf": 1222.3,
   "pa": 1353.2
  },
  {
   "rank": 10,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "5-8",
   "pf": 1122.7,
   "pa": 1289.5
  }
 ],
 "2010": [
  {
   "rank": 1,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "8-5",
   "pf": 1270.7,
   "pa": 1254.7
  },
  {
   "rank": 2,
   "team": "Leon Lett me see that mirror",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "9-4",
   "pf": 1542.4,
   "pa": 1287.0
  },
  {
   "rank": 3,
   "team": "The C.R.E.A.M. Team",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "7-6",
   "pf": 1275.5,
   "pa": 1242.5
  },
  {
   "rank": 4,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "9-4",
   "pf": 1334.3,
   "pa": 1131.0
  },
  {
   "rank": 5,
   "team": "Ben RapedHerBerger",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "8-5",
   "pf": 1209.7,
   "pa": 1101.1
  },
  {
   "rank": 6,
   "team": "Oops I Came In Yia Yia",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "7-6",
   "pf": 1216.2,
   "pa": 1362.7
  },
  {
   "rank": 7,
   "team": "Touch Down There",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "4-9",
   "pf": 1234.1,
   "pa": 1347.2
  },
  {
   "rank": 8,
   "team": "Brees Nuts",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "3-10",
   "pf": 1194.1,
   "pa": 1341.0
  },
  {
   "rank": 9,
   "team": "The Dirty Peaches",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "7-6",
   "pf": 1170.4,
   "pa": 1182.3
  },
  {
   "rank": 10,
   "team": "The Frozen Cockwarts",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "3-10",
   "pf": 1090.5,
   "pa": 1288.4
  }
 ],
 "2011": [
  {
   "rank": 1,
   "team": "The Face of The Franchise",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "8-5",
   "pf": 1332.6,
   "pa": 1305.9
  },
  {
   "rank": 2,
   "team": "Green Bowl Packers",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "9-4",
   "pf": 1548.1,
   "pa": 1325.5
  },
  {
   "rank": 3,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "6-7",
   "pf": 1320.1,
   "pa": 1277.4
  },
  {
   "rank": 4,
   "team": "LT's Peach Juice",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "7-6",
   "pf": 1324.1,
   "pa": 1243.2
  },
  {
   "rank": 5,
   "team": "Champions In Wait",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "7-6",
   "pf": 1339.8,
   "pa": 1421.4
  },
  {
   "rank": 6,
   "team": "Ben RapedHerBerger",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "8-5",
   "pf": 1144.3,
   "pa": 1148.3
  },
  {
   "rank": 7,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "6-7",
   "pf": 1282.1,
   "pa": 1275.0
  },
  {
   "rank": 8,
   "team": "The Frozen Cockwarts",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "5-8",
   "pf": 1212.8,
   "pa": 1311.2
  },
  {
   "rank": 9,
   "team": "The Bach (1 of 2)",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "4-9",
   "pf": 1222.1,
   "pa": 1315.4
  },
  {
   "rank": 10,
   "team": "Oops I Blank In Yia Yia",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "5-8",
   "pf": 1265.5,
   "pa": 1368.2
  }
 ],
 "2012": [
  {
   "rank": 1,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "8-5",
   "pf": 1383.2,
   "pa": 1379.3
  },
  {
   "rank": 2,
   "team": "Sloppy Seconds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "9-4",
   "pf": 1351.5,
   "pa": 1206.7
  },
  {
   "rank": 3,
   "team": "The Two-Timing Face",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "9-4",
   "pf": 1325.7,
   "pa": 1199.4
  },
  {
   "rank": 4,
   "team": "The Frozen Cockwarts",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "7-6",
   "pf": 1268.1,
   "pa": 1298.6
  },
  {
   "rank": 5,
   "team": "Power Fade",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "7-6",
   "pf": 1307.0,
   "pa": 1218.2
  },
  {
   "rank": 6,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "7-6",
   "pf": 1247.9,
   "pa": 1197.1
  },
  {
   "rank": 7,
   "team": "Grrrrrreat Disappointments",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "6-7",
   "pf": 1351.1,
   "pa": 1143.3
  },
  {
   "rank": 8,
   "team": "Beat My Johnson",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "2-11",
   "pf": 1083.0,
   "pa": 1492.7
  },
  {
   "rank": 9,
   "team": "Edward Forte Hands",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "4-9",
   "pf": 1122.5,
   "pa": 1335.0
  },
  {
   "rank": 10,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "6-7",
   "pf": 1349.6,
   "pa": 1319.3
  }
 ],
 "2013": [
  {
   "rank": 1,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "7-6",
   "pf": 1141.5,
   "pa": 1204.1
  },
  {
   "rank": 2,
   "team": "Face Mode",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "11-2",
   "pf": 1505.3,
   "pa": 1222.5
  },
  {
   "rank": 3,
   "team": "Sloppy Seconds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "8-5",
   "pf": 1374.2,
   "pa": 1318.1
  },
  {
   "rank": 4,
   "team": "Power Fade",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "7-6",
   "pf": 1376.3,
   "pa": 1296.3
  },
  {
   "rank": 5,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "8-5",
   "pf": 1358.6,
   "pa": 1292.8
  },
  {
   "rank": 6,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "7-6",
   "pf": 1271.5,
   "pa": 1238.4
  },
  {
   "rank": 7,
   "team": "The Rusty Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "5-8",
   "pf": 1342.8,
   "pa": 1400.2
  },
  {
   "rank": 8,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "4-9",
   "pf": 1175.6,
   "pa": 1252.7
  },
  {
   "rank": 9,
   "team": "10 Seed",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "2-11",
   "pf": 1022.3,
   "pa": 1321.1
  },
  {
   "rank": 10,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "6-7",
   "pf": 1251.4,
   "pa": 1273.3
  }
 ],
 "2014": [
  {
   "rank": 1,
   "team": "Face Capital",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "8-5",
   "pf": 1322.9,
   "pa": 1251.0
  },
  {
   "rank": 2,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "7-6",
   "pf": 1291.5,
   "pa": 1207.3
  },
  {
   "rank": 3,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "9-4",
   "pf": 1288.5,
   "pa": 1219.1
  },
  {
   "rank": 4,
   "team": "The Rusty Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "9-4",
   "pf": 1480.7,
   "pa": 1154.9
  },
  {
   "rank": 5,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "8-5",
   "pf": 1475.8,
   "pa": 1213.6
  },
  {
   "rank": 6,
   "team": "Sloppy Seconds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "8-5",
   "pf": 1307.2,
   "pa": 1344.6
  },
  {
   "rank": 7,
   "team": "Young Blood",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "2-11",
   "pf": 1033.9,
   "pa": 1387.7
  },
  {
   "rank": 8,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "6-7",
   "pf": 1320.7,
   "pa": 1398.8
  },
  {
   "rank": 9,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "4-9",
   "pf": 1075.4,
   "pa": 1262.3
  },
  {
   "rank": 10,
   "team": "Power Fade",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "4-9",
   "pf": 1248.3,
   "pa": 1405.6
  }
 ],
 "2015": [
  {
   "rank": 1,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "8-5",
   "pf": 1342.9,
   "pa": 1241.2
  },
  {
   "rank": 2,
   "team": "Angry Byrds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "7-6",
   "pf": 1368.1,
   "pa": 1238.6
  },
  {
   "rank": 3,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "6-7",
   "pf": 1330.7,
   "pa": 1386.0
  },
  {
   "rank": 4,
   "team": "Drug Runner. Corp.",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "8-5",
   "pf": 1368.8,
   "pa": 1371.9
  },
  {
   "rank": 5,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "8-5",
   "pf": 1281.9,
   "pa": 1173.6
  },
  {
   "rank": 6,
   "team": "Power Fade",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "7-6",
   "pf": 1341.0,
   "pa": 1286.4
  },
  {
   "rank": 7,
   "team": "The Rusty Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "6-7",
   "pf": 1263.2,
   "pa": 1331.7
  },
  {
   "rank": 8,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "6-7",
   "pf": 1145.6,
   "pa": 1302.2
  },
  {
   "rank": 9,
   "team": "Face Treble",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "3-10",
   "pf": 1086.8,
   "pa": 1265.3
  },
  {
   "rank": 10,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "6-7",
   "pf": 1292.8,
   "pa": 1224.9
  }
 ],
 "2016": [
  {
   "rank": 1,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "8-5",
   "pf": 1442.5,
   "pa": 1254.9
  },
  {
   "rank": 2,
   "team": "The Rusty Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "11-2",
   "pf": 1404.8,
   "pa": 1283.2
  },
  {
   "rank": 3,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "9-4",
   "pf": 1341.6,
   "pa": 1210.1
  },
  {
   "rank": 4,
   "team": "Angry Byrds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "8-5",
   "pf": 1414.5,
   "pa": 1236.6
  },
  {
   "rank": 5,
   "team": "Drug Runner. Corp.",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "8-5",
   "pf": 1241.3,
   "pa": 1223.6
  },
  {
   "rank": 6,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "6-7",
   "pf": 1284.6,
   "pa": 1273.0
  },
  {
   "rank": 7,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "5-8",
   "pf": 1162.8,
   "pa": 1325.0
  },
  {
   "rank": 8,
   "team": "Power Fade",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "2-11",
   "pf": 1090.9,
   "pa": 1354.9
  },
  {
   "rank": 9,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "4-9",
   "pf": 1252.4,
   "pa": 1421.1
  },
  {
   "rank": 10,
   "team": "FF Face Genesis",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "4-9",
   "pf": 1270.0,
   "pa": 1323.0
  }
 ],
 "2017": [
  {
   "rank": 1,
   "team": "Drug Runner. Corp.",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "9-4",
   "pf": 1384.9,
   "pa": 1103.3
  },
  {
   "rank": 2,
   "team": "Angry Byrds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "8-5",
   "pf": 1362.9,
   "pa": 1254.7
  },
  {
   "rank": 3,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "6-7",
   "pf": 1081.9,
   "pa": 1204.8
  },
  {
   "rank": 4,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "8-5",
   "pf": 1157.0,
   "pa": 1281.1
  },
  {
   "rank": 5,
   "team": "The Rusty Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "8-5",
   "pf": 1239.7,
   "pa": 1050.6
  },
  {
   "rank": 6,
   "team": "Power Fade",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "7-6",
   "pf": 1240.6,
   "pa": 1206.8
  },
  {
   "rank": 7,
   "team": "Shit On Your Face",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "5-8",
   "pf": 1188.7,
   "pa": 1266.5
  },
  {
   "rank": 8,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "5-8",
   "pf": 1093.5,
   "pa": 1116.2
  },
  {
   "rank": 9,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "4-9",
   "pf": 999.3,
   "pa": 1217.2
  },
  {
   "rank": 10,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "5-8",
   "pf": 1197.9,
   "pa": 1245.2
  }
 ],
 "2018": [
  {
   "rank": 1,
   "team": "Face Savage",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "9-4",
   "pf": 1383.2,
   "pa": 1359.8
  },
  {
   "rank": 2,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "10-3",
   "pf": 1623.7,
   "pa": 1346.5
  },
  {
   "rank": 3,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "8-5",
   "pf": 1589.7,
   "pa": 1384.6
  },
  {
   "rank": 4,
   "team": "The Rusty Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "10-3",
   "pf": 1450.6,
   "pa": 1189.2
  },
  {
   "rank": 5,
   "team": "Angry Byrds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "7-6",
   "pf": 1446.7,
   "pa": 1373.5
  },
  {
   "rank": 6,
   "team": "Drug Runner. Corp.",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "8-5",
   "pf": 1456.8,
   "pa": 1224.7
  },
  {
   "rank": 7,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "1-12",
   "pf": 1106.6,
   "pa": 1505.9
  },
  {
   "rank": 8,
   "team": "Power Fade",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "6-7",
   "pf": 1359.2,
   "pa": 1453.8
  },
  {
   "rank": 9,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "2-11",
   "pf": 1063.5,
   "pa": 1556.7
  },
  {
   "rank": 10,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "4-9",
   "pf": 1274.9,
   "pa": 1360.2
  }
 ],
 "2019": [
  {
   "rank": 1,
   "team": "The Rusty Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "11-2",
   "pf": 1420.6,
   "pa": 1252.2
  },
  {
   "rank": 2,
   "team": "Face Cuatro",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "9-4",
   "pf": 1465.2,
   "pa": 1264.6
  },
  {
   "rank": 3,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "10-3",
   "pf": 1490.8,
   "pa": 1234.3
  },
  {
   "rank": 4,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "8-5",
   "pf": 1354.3,
   "pa": 1279.6
  },
  {
   "rank": 5,
   "team": "Angry Byrds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "8-5",
   "pf": 1320.7,
   "pa": 1243.7
  },
  {
   "rank": 6,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "5-8",
   "pf": 1341.5,
   "pa": 1413.8
  },
  {
   "rank": 7,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "5-8",
   "pf": 1207.4,
   "pa": 1227.8
  },
  {
   "rank": 8,
   "team": "Power Fade",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "1-12",
   "pf": 1097.0,
   "pa": 1356.9
  },
  {
   "rank": 9,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "4-9",
   "pf": 1142.3,
   "pa": 1311.1
  },
  {
   "rank": 10,
   "team": "Drug Runner. Corp.",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "4-9",
   "pf": 1097.0,
   "pa": 1352.8
  }
 ],
 "2020": [
  {
   "rank": 1,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "12-0-1",
   "pf": 1610.2,
   "pa": 1204.8
  },
  {
   "rank": 2,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "8-5",
   "pf": 1334.0,
   "pa": 1232.7
  },
  {
   "rank": 3,
   "team": "Angry Byrds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "7-6",
   "pf": 1390.7,
   "pa": 1368.2
  },
  {
   "rank": 4,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "9-3-1",
   "pf": 1411.4,
   "pa": 1161.8
  },
  {
   "rank": 5,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "6-7",
   "pf": 1376.6,
   "pa": 1302.6
  },
  {
   "rank": 6,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "7-6",
   "pf": 1253.5,
   "pa": 1303.9
  },
  {
   "rank": 7,
   "team": "Power Fade",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "6-7",
   "pf": 1335.3,
   "pa": 1383.3
  },
  {
   "rank": 8,
   "team": "Face Mask",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "1-12",
   "pf": 943.5,
   "pa": 1327.9
  },
  {
   "rank": 9,
   "team": "The Rusty Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "4-9",
   "pf": 1280.4,
   "pa": 1433.4
  },
  {
   "rank": 10,
   "team": "Drug Runner. Corp.",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "4-9",
   "pf": 1082.2,
   "pa": 1299.2
  }
 ],
 "2021": [
  {
   "rank": 1,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "11-3",
   "pf": 1532.7,
   "pa": 1347.2
  },
  {
   "rank": 2,
   "team": "Drug Runner. Corp.",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "10-4",
   "pf": 1485.7,
   "pa": 1478.6
  },
  {
   "rank": 3,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "7-7",
   "pf": 1428.4,
   "pa": 1414.3
  },
  {
   "rank": 4,
   "team": "Angry Byrds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "7-7",
   "pf": 1448.6,
   "pa": 1380.5
  },
  {
   "rank": 5,
   "team": "P F D",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "8-6",
   "pf": 1474.9,
   "pa": 1464.8
  },
  {
   "rank": 6,
   "team": "The Rusty Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "8-6",
   "pf": 1452.2,
   "pa": 1372.6
  },
  {
   "rank": 7,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "6-8",
   "pf": 1534.7,
   "pa": 1393.5
  },
  {
   "rank": 8,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "7-7",
   "pf": 1248.5,
   "pa": 1361.9
  },
  {
   "rank": 9,
   "team": "Face Mask",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "3-11",
   "pf": 1185.5,
   "pa": 1414.4
  },
  {
   "rank": 10,
   "team": "\\ asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "3-11",
   "pf": 1170.2,
   "pa": 1333.6
  }
 ],
 "2022": [
  {
   "rank": 1,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "11-3",
   "pf": 1399.1,
   "pa": 1299.6
  },
  {
   "rank": 2,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "7-7",
   "pf": 1447.3,
   "pa": 1428.6
  },
  {
   "rank": 3,
   "team": "Angry Byrds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "7-7",
   "pf": 1325.3,
   "pa": 1301.2
  },
  {
   "rank": 4,
   "team": "\\ asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "11-3",
   "pf": 1612.0,
   "pa": 1287.5
  },
  {
   "rank": 5,
   "team": "Drug Runner. Corp.",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "7-7",
   "pf": 1475.6,
   "pa": 1474.8
  },
  {
   "rank": 6,
   "team": "The Rusty Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "9-5",
   "pf": 1477.6,
   "pa": 1362.2
  },
  {
   "rank": 7,
   "team": "P F D",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "6-8",
   "pf": 1334.1,
   "pa": 1374.8
  },
  {
   "rank": 8,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "4-10",
   "pf": 1258.6,
   "pa": 1339.1
  },
  {
   "rank": 9,
   "team": "Face The Music",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "5-9",
   "pf": 1393.7,
   "pa": 1511.6
  },
  {
   "rank": 10,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "3-11",
   "pf": 1082.5,
   "pa": 1426.4
  }
 ],
 "2023": [
  {
   "rank": 1,
   "team": "Face G.O.A.T.",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "7-7",
   "pf": 1305.1,
   "pa": 1383.3
  },
  {
   "rank": 2,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "7-7",
   "pf": 1455.2,
   "pa": 1382.0
  },
  {
   "rank": 3,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "10-4",
   "pf": 1457.5,
   "pa": 1183.0
  },
  {
   "rank": 4,
   "team": "The Rusty Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "10-4",
   "pf": 1456.4,
   "pa": 1324.5
  },
  {
   "rank": 5,
   "team": "\\ asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "7-7",
   "pf": 1371.3,
   "pa": 1293.2
  },
  {
   "rank": 6,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "8-6",
   "pf": 1431.8,
   "pa": 1280.5
  },
  {
   "rank": 7,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "6-8",
   "pf": 1265.2,
   "pa": 1385.0
  },
  {
   "rank": 8,
   "team": "P F D",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "4-10",
   "pf": 1244.2,
   "pa": 1555.7
  },
  {
   "rank": 9,
   "team": "Drug Runner. Corp.",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "5-9",
   "pf": 1173.0,
   "pa": 1404.8
  },
  {
   "rank": 10,
   "team": "Angry Byrds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "6-8",
   "pf": 1461.4,
   "pa": 1429.1
  }
 ],
 "2024": [
  {
   "rank": 1,
   "team": "The Very Sharp Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "8-6",
   "pf": 1386.5,
   "pa": 1296.6
  },
  {
   "rank": 2,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "7-7",
   "pf": 1416.9,
   "pa": 1372.0
  },
  {
   "rank": 3,
   "team": "\\ asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "10-4",
   "pf": 1441.6,
   "pa": 1408.0
  },
  {
   "rank": 4,
   "team": "Angry Byrds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "9-5",
   "pf": 1475.5,
   "pa": 1281.5
  },
  {
   "rank": 5,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "9-5",
   "pf": 1472.4,
   "pa": 1403.4
  },
  {
   "rank": 6,
   "team": "Power Fade",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "7-7",
   "pf": 1473.0,
   "pa": 1467.9
  },
  {
   "rank": 7,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "4-10",
   "pf": 1233.5,
   "pa": 1356.7
  },
  {
   "rank": 8,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "6-8",
   "pf": 1340.9,
   "pa": 1365.9
  },
  {
   "rank": 9,
   "team": "Drug Runner. Corp.",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "5-9",
   "pf": 1275.1,
   "pa": 1394.4
  },
  {
   "rank": 10,
   "team": "Face Card",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "5-9",
   "pf": 1396.9,
   "pa": 1565.9
  }
 ],
 "2025": [
  {
   "rank": 1,
   "team": "Allen Face One",
   "manager": "James Farmer",
   "key": "Farmer",
   "rec": "10-4",
   "pf": 1534.9,
   "pa": 1311.2
  },
  {
   "rank": 2,
   "team": "Power Fade",
   "manager": "Brett Link",
   "key": "Link",
   "rec": "11-3",
   "pf": 1547.5,
   "pa": 1327.7
  },
  {
   "rank": 3,
   "team": "Angry Byrds",
   "manager": "Brian Byrd",
   "key": "Byrd",
   "rec": "9-5",
   "pf": 1453.8,
   "pa": 1289.3
  },
  {
   "rank": 4,
   "team": "Singer's Secret Sauce",
   "manager": "Justin Singer",
   "key": "Singer",
   "rec": "10-4",
   "pf": 1442.7,
   "pa": 1293.3
  },
  {
   "rank": 5,
   "team": "slaying asians",
   "manager": "Omar Nagji",
   "key": "Omar",
   "rec": "8-6",
   "pf": 1356.6,
   "pa": 1366.8
  },
  {
   "rank": 6,
   "team": "Drug Runner. Corp.",
   "manager": "Brett Crisp",
   "key": "Crisp",
   "rec": "7-7",
   "pf": 1376.6,
   "pa": 1347.8
  },
  {
   "rank": 7,
   "team": "Grrrrrreat Expectations",
   "manager": "Rob Parker",
   "key": "Rob",
   "rec": "3-11",
   "pf": 1253.6,
   "pa": 1463.7
  },
  {
   "rank": 8,
   "team": "poop shoot",
   "manager": "Kevin Criscitiello",
   "key": "Kevin",
   "rec": "6-8",
   "pf": 1285.1,
   "pa": 1352.6
  },
  {
   "rank": 9,
   "team": "The Very Sharp Harpoons",
   "manager": "Ned Wellman",
   "key": "Ned",
   "rec": "2-12",
   "pf": 1193.1,
   "pa": 1524.4
  },
  {
   "rank": 10,
   "team": "Peaches, Inc.",
   "manager": "Brian Lesesne",
   "key": "Lesesne",
   "rec": "4-10",
   "pf": 1311.7,
   "pa": 1478.8
  }
 ]
}

CHAMPIONS = [
 {
  "year": 2006,
  "team": "LaSizzle",
  "manager": "Brian Lesesne",
  "key": "Lesesne"
 },
 {
  "year": 2007,
  "team": "Charm City Smash",
  "manager": "James Farmer",
  "key": "Farmer"
 },
 {
  "year": 2008,
  "team": "Bronco Bound",
  "manager": "Justin Singer",
  "key": "Singer"
 },
 {
  "year": 2009,
  "team": "Living Legends",
  "manager": "Brett Link",
  "key": "Link"
 },
 {
  "year": 2010,
  "team": "poop shoot",
  "manager": "Kevin Criscitiello",
  "key": "Kevin"
 },
 {
  "year": 2011,
  "team": "The Face of The Franchise",
  "manager": "James Farmer",
  "key": "Farmer"
 },
 {
  "year": 2012,
  "team": "Peaches, Inc.",
  "manager": "Brian Lesesne",
  "key": "Lesesne"
 },
 {
  "year": 2013,
  "team": "slaying asians",
  "manager": "Omar Nagji",
  "key": "Omar"
 },
 {
  "year": 2014,
  "team": "Face Capital",
  "manager": "James Farmer",
  "key": "Farmer"
 },
 {
  "year": 2015,
  "team": "slaying asians",
  "manager": "Omar Nagji",
  "key": "Omar"
 },
 {
  "year": 2016,
  "team": "Peaches, Inc.",
  "manager": "Brian Lesesne",
  "key": "Lesesne"
 },
 {
  "year": 2017,
  "team": "Drug Runner. Corp.",
  "manager": "Brett Crisp",
  "key": "Crisp"
 },
 {
  "year": 2018,
  "team": "Face Savage",
  "manager": "James Farmer",
  "key": "Farmer"
 },
 {
  "year": 2019,
  "team": "The Rusty Harpoons",
  "manager": "Ned Wellman",
  "key": "Ned"
 },
 {
  "year": 2020,
  "team": "Singer's Secret Sauce",
  "manager": "Justin Singer",
  "key": "Singer"
 },
 {
  "year": 2021,
  "team": "Grrrrrreat Expectations",
  "manager": "Rob Parker",
  "key": "Rob"
 },
 {
  "year": 2022,
  "team": "poop shoot",
  "manager": "Kevin Criscitiello",
  "key": "Kevin"
 },
 {
  "year": 2023,
  "team": "Face G.O.A.T.",
  "manager": "James Farmer",
  "key": "Farmer"
 },
 {
  "year": 2024,
  "team": "The Very Sharp Harpoons",
  "manager": "Ned Wellman",
  "key": "Ned"
 },
 {
  "year": 2025,
  "team": "Allen Face One",
  "manager": "James Farmer",
  "key": "Farmer"
 }
]

ALL_TIME = [
 {
  "rank": 1,
  "key": "Farmer",
  "manager": "James Farmer",
  "record": "116-133-3",
  "win_pct": 0.466,
  "avg_finish": 5.11,
  "pf_per_game": 97.1,
  "titles": [
   2007,
   2011,
   2014,
   2018,
   2023,
   2025
  ],
  "runner_ups": [
   2013,
   2019
  ],
  "last_places": [
   2016,
   2024
  ],
  "top3": 9,
  "score": 32.3
 },
 {
  "rank": 2,
  "key": "Singer",
  "manager": "Justin Singer",
  "record": "127-123-2",
  "win_pct": 0.508,
  "avg_finish": 4.68,
  "pf_per_game": 100.5,
  "titles": [
   2008,
   2020
  ],
  "runner_ups": [
   2018,
   2022,
   2024
  ],
  "last_places": [],
  "top3": 9,
  "score": 21.1
 },
 {
  "rank": 3,
  "key": "Lesesne",
  "manager": "Brian Lesesne",
  "record": "115-137",
  "win_pct": 0.456,
  "avg_finish": 6.26,
  "pf_per_game": 95.7,
  "titles": [
   2006,
   2012,
   2016
  ],
  "runner_ups": [
   2014,
   2023
  ],
  "last_places": [
   2017,
   2018,
   2022,
   2025
  ],
  "top3": 5,
  "score": 19.0
 },
 {
  "rank": 4,
  "key": "Kevin",
  "manager": "Kevin Criscitiello",
  "record": "131-120-1",
  "win_pct": 0.522,
  "avg_finish": 5.58,
  "pf_per_game": 98.6,
  "titles": [
   2010,
   2022
  ],
  "runner_ups": [],
  "last_places": [
   2013,
   2015
  ],
  "top3": 6,
  "score": 17.8
 },
 {
  "rank": 5,
  "key": "Omar",
  "manager": "Omar Nagji",
  "record": "131-120-1",
  "win_pct": 0.522,
  "avg_finish": 5.47,
  "pf_per_game": 95.9,
  "titles": [
   2013,
   2015
  ],
  "runner_ups": [
   2020
  ],
  "last_places": [
   2009,
   2012,
   2021
  ],
  "top3": 5,
  "score": 17.6
 },
 {
  "rank": 6,
  "key": "Byrd",
  "manager": "Brian Byrd",
  "record": "142-97",
  "win_pct": 0.594,
  "avg_finish": 3.89,
  "pf_per_game": 105.3,
  "titles": [],
  "runner_ups": [
   2010,
   2011,
   2012,
   2015,
   2017
  ],
  "last_places": [
   2023
  ],
  "top3": 9,
  "score": 16.7
 },
 {
  "rank": 7,
  "key": "Ned",
  "manager": "Ned Wellman",
  "record": "129-122-1",
  "win_pct": 0.514,
  "avg_finish": 5.95,
  "pf_per_game": 99.0,
  "titles": [
   2019,
   2024
  ],
  "runner_ups": [
   2016
  ],
  "last_places": [
   2007,
   2010
  ],
  "top3": 3,
  "score": 15.6
 },
 {
  "rank": 8,
  "key": "Link",
  "manager": "Brett Link",
  "record": "119-132-1",
  "win_pct": 0.474,
  "avg_finish": 5.63,
  "pf_per_game": 98.8,
  "titles": [
   2009
  ],
  "runner_ups": [
   2025
  ],
  "last_places": [
   2014
  ],
  "top3": 4,
  "score": 13.7
 },
 {
  "rank": 9,
  "key": "Rob",
  "manager": "Rob Parker",
  "record": "121-130-1",
  "win_pct": 0.482,
  "avg_finish": 6.05,
  "pf_per_game": 96.0,
  "titles": [
   2021
  ],
  "runner_ups": [
   2008
  ],
  "last_places": [
   2011
  ],
  "top3": 3,
  "score": 12.4
 },
 {
  "rank": 10,
  "key": "Crisp",
  "manager": "Brett Crisp",
  "record": "115-136-1",
  "win_pct": 0.458,
  "avg_finish": 6.47,
  "pf_per_game": 92.6,
  "titles": [
   2017
  ],
  "runner_ups": [
   2009,
   2021
  ],
  "last_places": [
   2008,
   2019,
   2020
  ],
  "top3": 3,
  "score": 11.6
 }
]
