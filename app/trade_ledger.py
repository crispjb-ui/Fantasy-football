"""League UNC trade ledger, 2016-2025, as kept by the league (verbatim-ish).

Notable mechanics: draft picks traded (2016-2020 era), then keeper RIGHTS and
DRAFT DOLLARS (2023-), e.g. "$100 2025 Draft Dollars" adjusts that team's
auction budget. Net 2026 budget adjustments (2025-season trades plus the
Aug 2026 Taylor rights sale): Lesesne +82, Link -82, Crisp +60, Byrd -60,
Ned +45, Omar -35, Farmer -10 (everyone else $500 base). Enter/adjust in
Data & Setup before draft night.
"""

TRADES = {
 2016: [
  "Crisp gets Mark Ingram + Byrd's 15th; Byrd gets Zach Miller + Crisp's 5th",
  "Farmer gets Alfred Morris, Antoine Smith + Rob's 5th; Rob gets Marshawn Lynch, Thomas Rawls + Farmer's 13th",
  "Farmer gets Delanie Walker, Antonio Andrews + Singer's 4th; Singer gets Tyler Eifert, Lamar Miller + Farmer's 10th",
  "Farmer gets John Brown + Byrd's 7th; Byrd gets Dez Bryant + Farmer's 9th",
  "Link gets Todd Gurley + Byrd's 14th; (Byrd) gets Link's 6th",
  "Farmer gets Doug Martin + Singer's 15th; Singer gets Farmer's 7th",
  "Nova gets Matt Jones + Byrd's 11th; Byrd gets Nova's 8th",
 ],
 2017: [
  "Farmer gets Rishard Matthews + 5th; Link gets Brandin Cooks + 2017 13th",
  "Ned gets TY Hilton + 15th; Link gets 5th + Jeremy Maclin",
  "Farmer gets 2017 1st, S. Shepherd & M. Asiata; Lesesne gets Zeke & Marvin Jones + 2017 15th",
  "Farmer gets 2017 2nd; Crisp gets Melvin Gordon + 2017 14th",
  "Singer gets Jay Ajayi + 2017 14th; Link gets 2017 8th + Wendell Smallwood",
  "Rob gets 2017 3rd; Kevin gets DeMarco Murray & Dez Bryant + 2017 15th",
  "Lesesne gets Link's 2017 2nd; Link gets Ezekiel Elliott + Lesesne's 15th",
  "Link gets Omar's 2017 1st; Omar: see 2018",
  "Ned gets Curry's 2017 5th; Curry gets Ned's 15th + Carlos Hyde",
 ],
 2018: [
  "Farmer gets Lesesne's 4th (Zeke deal); Lesesne gets Farmer's 15th",
  "Farmer gets Rob's 7th + Fozzy Whitaker; Rob gets Farmer's 14th + Latavius Murray",
  "Farmer gets Crisp's 5th (MGIII deal); Crisp gets Farmer's 13th",
  "Rob gets Nova's 2018 8th; Nova gets Rob's 15th (Dez & DeMarco deal)",
  "Link gets 2018 4th; Lesesne gets Link's 15th (2016 Gurley trade)",
  "Omar gets Link's 2018 2nd + first 4th; Link gets Omar's 14th & 15th",
  "Byrd gets Hunter Henry/Joe Mixon + Lesesne's 6th; Lesesne gets Cam Newton/Gronk + Byrd's 15th",
  "Lesesne gets 2018 2nd, Chiefs D & Gore; Ned gets Ingram, Gronk + Lesesne's 2nd 15th",
  "Crisp gets AB + Nova's 15th; Nova gets Crisp's 2018 2nd",
  "Crisp gets Jerick McKinnon; Lesesne gets Crisp's 2018 4th",
  "Link gets DeMarco Murray + Nova's 14th; Nova gets Link's 6th",
  "Farmer gets Melvin Gordon, Crisp final '18 + final '19 pick, swap 1sts; Crisp gets '18 4th, '19 5th, swap 1sts",
  "Byrd gets Nova's 6th & 7th; Nova gets Byrd's 8th & 9th + rights to Z. Ertz & S. Diggs",
 ],
 2019: [
  "Farmer gets 5th from poop shoot; Kevin gets 15th from Face (Doug Martin trade)",
  "Crisp gets Shoot's 15th; Kevin gets Crisp's 3rd (2017 AB trade)",
  "Byrd gets Lesesne's 3rd; Lesesne gets 15th (Gronk trade 2018)",
  "Farmer gets Crisp's final pick; Crisp gets Face's 5th (Melvin Gordon trade)",
  "Byrd gets Ned's 2nd; Ned gets Antonio Brown + Byrd's 14th",
  "Byrd gets Nova's 3rd; Kevin gets Tevin Coleman/Tarik Cohen + Byrd's 12th",
  "Crisp gets Lesesne's last (15th); Lesesne gets Crisp's 2nd (D. Cook, JuJu)",
  "Crisp gets Omar's last (14th); Omar gets Crisp's 5th",
  "Omar gets Nova's 2nd; Nova gets Omar's final pick (Mahomes trade)",
  "Byrd gets Julio Jones + Ned's 13th; Ned gets Byrd's 4th",
  "Lesesne gets Face's 2nd; Face gets Lesesne's 15th (J. Conner trade)",
  "Byrd gets Lesesne's 6th; Lesesne gets rights to J. Gordon + Byrd's 13th",
  "Crisp gets Ned's 4th; Ned gets rights to M. Evans + Crisp's last pick",
  "Byrd gets Rob's 6th; Rob gets rights to A. Jones + Byrd's 13th",
 ],
 2020: [
  "Crisp gets Omar's last (15th); Omar gets Crisp's 2nd & 4th (Fournette trade)",
  "Nova gets Ned's 2020 2nd; Ned gets Shoot's 2020 15th",
  "Nova gets Ned's 2020 5th; Ned gets Shoot's 2020 14th",
  "Lesesne gets Scuppers' 2020 1st (D. Adams & Fournette); Ned gets Lesesne's 2020 15th",
  "Link gets Rob's 4th; Rob gets Link's 13th (Thielen)",
  "Link gets Face's 2nd & 4th; Face gets Link's 14th & 15th (Zeke)",
  "Byrd gets Ned's 2020 6th; Ned gets Byrd's 15th (David Johnson)",
  "Lesesne gets Ned's 15th (Mike Evans); Ned gets Lesesne's 2020 6th",
 ],
 2023: [
  "Face gets Sam LaPorta (-$15); Byrd gets $15 + Goedert",
  "Face gets Jalen Hurts (-$15); Link gets $15 + Lockett",
  "Poop gets Bijan Robinson (-$50); Link gets $50 + McKinnon",
  "Peaches gets Tyreek (-$100); asians gets $100 + Michael Thomas",
  "Poop gets $10; Link gets rights to draft Olave (-$10)",
  "Peaches gets rights to Tyreek Hill; Ned gets rights to Justin Jefferson",
 ],
 2024: [
  "asians gets CMC (on IR) + A. Lazard; Peaches gets Rhamondre Stevenson + George Kittle",
  "poop gets $100 2025 draft dollars; Peaches gets Saquon Barkley + Kmet (-$100)",
  "Singer gets $100 2025 draft dollars + Chase Brown; Harpoons get Derrick Henry (-$100)",
  "Crisp gets $100 2025 draft dollars + Tony Pollard & Pittman; Link gets Kyren Williams + Deebo Samuel (-$100)",
  "Face gets $75 2025 draft dollars + Shakir; Byrd gets Alvin Kamara + AJ Brown (-$75)",
  "Face gets $20 2025 draft dollars + Etienne & Hunter Henry; asians get Brian Robinson Jr + Brock Purdy (-$20)",
 ],
 2026: [
  "PRE-DRAFT: Link gets $18 2026 draft dollars; Peaches gets rights to keep Jonathan Taylor (-$18)",
 ],
 2025: [
  "PRE-DRAFT: Byrd gets $50 2025 draft dollars; Face gets D. Achane (-$50)",
  "PRE-DRAFT: Peaches gets $30 2025 draft dollars; shoot gets Jayden Daniels + M. Nabers",
  "PRE-DRAFT: Poop gets $6 2025 draft dollars; Face gets Amon-Ra St. Brown (-$6)",
  "IN-SEASON: poop gets Chris Olave; Byrd gets B. Tuten",
  "IN-SEASON: Link gets Saquon Barkley + Davante Adams; Lesesne gets $100 2026 draft dollars + X. Worthy/Shaheed",
  "IN-SEASON: Byrd gets Ja'Marr Chase; Crisp gets $60 2026 draft dollars + AJ Brown",
  "IN-SEASON: asians get Derrick Henry; Ned gets $35 2026 draft dollars + Bills D",
  "IN-SEASON: Face gets K. Monangai; Ned gets $10 2026 draft dollars + D. Schultz",
 ],
}

# Net 2026 auction-budget adjustments implied by the trades above: the
# 2025-season dollars (Lesesne +100, Link -100, Crisp +60, Byrd -60, Ned +45,
# Omar -35, Farmer -10) plus the Aug 2026 pre-draft Taylor rights sale
# (Lesesne -18, Link +18).
BUDGET_2026 = {"Lesesne": 82, "Link": -82, "Crisp": 60, "Byrd": -60,
               "Ned": 45, "Omar": -35, "Farmer": -10}

# Keeper RIGHTS that legitimately moved via 2025 trades (player -> new owner
# alias). Keeper rule: drafted AND rostered all year — drops/waiver adds are
# ineligible — so cross-team eligibility exists ONLY through these trades.
RIGHTS_MOVES_2025 = {
    "Chris Olave": "Nova",
    "Bhayshul Tuten": "Byrd",
    "Saquon Barkley": "Link",
    "Davante Adams": "Link",
    "Xavier Worthy": "Lesesne",
    "Rashid Shaheed": "Lesesne",
    "Ja'Marr Chase": "Byrd",
    "A.J. Brown": "Crisp",
    "Derrick Henry": "Omar",
    "Kyle Monangai": "Farmer",
}
