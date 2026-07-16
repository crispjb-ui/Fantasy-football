"""League UNC ending rosters, 2025 season (post-week-17), bundled with the
copilot. Transcribed from ESPN team pages supplied by Brett (July 2026).

Why bundled: ESPN's API returns empty rosters in the offseason, which starves
the keeper-eligibility scrub (drafted AND rostered all year). Loading these
fills the rosters table with the season-ending state. Keys are sheet aliases;
IR players included — they count as rostered for keeper eligibility.
"""

ROSTERS = {
 "Crisp": [
  "Joe Burrow", "James Cook", "Breece Hall", "Justin Jefferson", "A.J. Brown",
  "Dallas Goedert", "Courtland Sutton", "Seahawks D/ST", "Harrison Mevis",
  "Mark Andrews", "Jordan Mason", "Rome Odunze", "Jayden Reed", "Blake Corum",
  "Isaiah Davis", "Trey Benson",
 ],
 "Farmer": [
  "Josh Allen", "Ashton Jeanty", "De'Von Achane", "Amon-Ra St. Brown",
  "Ladd McConkey", "Juwan Johnson", "D'Andre Swift", "Chargers D/ST",
  "Cam Little", "Tyler Warren", "Kyle Monangai", "Emanuel Wilson",
  "Michael Carter", "Alec Pierce", "Jacoby Brissett", "Rashee Rice",
 ],
 "Link": [
  "Dak Prescott", "Jahmyr Gibbs", "Jonathan Taylor", "Parker Washington",
  "Luther Burden III", "Taysom Hill", "Saquon Barkley", "Lions D/ST",
  "Ka'imi Fairbairn", "David Montgomery", "Christian Watson", "Davante Adams",
  "Tank Bigsby", "Ricky Pearsall", "Kyle Williams", "Tucker Kraft",
 ],
 "Byrd": [
  "Bo Nix", "Bijan Robinson", "TreVeyon Henderson", "Jaxon Smith-Njigba",
  "Ja'Marr Chase", "Jake Ferguson", "Rico Dowdle", "Broncos D/ST",
  "Cameron Dicker", "Lamar Jackson", "Deebo Samuel", "Tyler Allgeier",
  "Michael Wilson", "Dalton Schultz", "Kenneth Gainwell", "Bhayshul Tuten",
 ],
 "Singer": [
  "Trevor Lawrence", "Bucky Irving", "Javonte Williams", "Nico Collins",
  "George Pickens", "Trey McBride", "Josh Jacobs", "Steelers D/ST",
  "Eddy Pineiro", "Jalen Hurts", "Marvin Harrison Jr.", "Jameson Williams",
  "Zach Charbonnet", "Texans D/ST", "Malik Davis",
 ],
 "Omar": [
  "Matthew Stafford", "Woody Marks", "Derrick Henry", "Puka Nacua",
  "Stefon Diggs", "Theo Johnson", "Christian McCaffrey", "Patriots D/ST",
  "Jason Myers", "Travis Kelce", "RJ Harvey", "DeVonta Smith",
  "Jacory Croskey-Merritt", "Drake Maye", "Chase McLaughlin", "Travis Hunter",
 ],
 "Rob": [
  "Caleb Williams", "Kyren Williams", "Chase Brown", "Brian Thomas Jr.",
  "Zay Flowers", "Harold Fannin Jr.", "Tony Pollard", "Panthers D/ST",
  "Brandon Aubrey", "Terry McLaurin", "Chuba Hubbard", "Patrick Mahomes",
  "Romeo Doubs", "Nick Chubb", "Darius Slayton", "Sam LaPorta",
 ],
 "Nova": [
  "Brock Purdy", "Jaylen Warren", "Quinshon Judkins", "CeeDee Lamb",
  "Chris Olave", "Hunter Henry", "Omarion Hampton", "Bills D/ST",
  "Cairo Santos", "Drake London", "Alvin Kamara", "Cam Skattebo",
  "Kareem Hunt", "Khalil Shakir", "Jakobi Meyers", "Malik Nabers",
 ],
 "Ned": [
  "Justin Herbert", "Kenneth Walker III", "Aaron Jones", "Mike Evans",
  "Tetairoa McMillan", "Brock Bowers", "DJ Moore", "Giants D/ST",
  "Jake Bates", "Emeka Egbuka", "Colts D/ST", "Jauan Jennings",
  "Devin Singletary", "Chris Godwin", "Chris Rodriguez Jr.",
 ],
 "Lesesne": [
  "Jared Goff", "Travis Etienne Jr.", "Zonovan Knight", "Jaylen Waddle",
  "Wan'Dale Robinson", "George Kittle", "Rhamondre Stevenson", "Jaguars D/ST",
  "Jake Elliott", "Tee Higgins", "Baker Mayfield", "Keenan Allen",
  "Tyrone Tracy Jr.", "Xavier Worthy", "Kyle Pitts", "J.K. Dobbins",
 ],
}
