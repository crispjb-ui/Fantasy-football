import React from "react";
import {
  AbsoluteFill,
  Audio,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { MapCountdown, MAP_EMBED_DURATION, MAP_PREAMBLE_START, MAP_VEGAS_AT } from "./MapCountdown";
import { Plaque, PLAQUE_DURATION, PlaqueFinale, PLAQUE_FINALE_DURATION } from "./Plaque";
import { ALL_TIME, NAME_HISTORY, STANDINGS } from "./data";

/* The full 20th-anniversary film, UNC palette throughout. */

const NAVY = "#0d1f3c";
const NAVY_DEEP = "#081527";
const CAROLINA = "#4B9CD3";
const CAROLINA_LIGHT = "#7BAFD4";
const WHITE = "#f4f8fc";
const RED = "#d94f4f";

export const FILM_FPS = 30;

const OPEN_LEN = 150;
const FACE_NAMES = NAME_HISTORY.Farmer; // the whole saga, 2007 -> Allen Face One
const FACE_LEN = 90 + FACE_NAMES.length * 13 + 90;
const PER_RECORD = 80;
const RECORDS_LEN = 40 + 6 * PER_RECORD;
const LASTYEAR_LEN = 460;
const LEDGER_LEN = 560;
const STAKES_LEN = 130;
const FHO_LEN = 200;
const CLOSER_LEN = 240;
const PER_TICK = 32; // frames per number in the final 10..1 countdown
const TICKS_LEN = 60 + 10 * PER_TICK;

const T_MAP = OPEN_LEN;
const T_PLAQUE = T_MAP + MAP_EMBED_DURATION;
const T_FACE = T_PLAQUE + PLAQUE_DURATION;
const T_RECORDS = T_FACE + FACE_LEN;
const T_LASTYEAR = T_RECORDS + RECORDS_LEN;
const T_LEDGER = T_LASTYEAR + LASTYEAR_LEN;
const T_STAKES = T_LEDGER + LEDGER_LEN;
const T_FHO = T_STAKES + STAKES_LEN;
const T_CLOSER = T_FHO + FHO_LEN;
const T_TICKS = T_CLOSER + CLOSER_LEN;
const T_FINALE = T_TICKS + TICKS_LEN;
export const FILM_DURATION = T_FINALE + PLAQUE_FINALE_DURATION;

/* ---- Soundtrack: six league tracks as a DJ-set medley --------------------
   Five sit at ~123.5 BPM (seamless crossfades); At Night (~112.5) opens, so
   the tempo LIFTS when the rankings kick in. Each track enters at its
   hottest section (offsets from energy analysis). Crossfades are centered
   on scene boundaries. Files: hype/public/music/ (committed to the repo). */
const FADE = 45; // 1.5s each side of a boundary

const MEDLEY = [
  // moody build: cold open + Chapel Hill + arcs + the Yahoo-era journey legs
  { src: "music/at_night.mp3", from: 0, to: T_MAP + MAP_VEGAS_AT, offset: 0 },
  // rave drops in the moment the league first hits Vegas (2011), rides the journey home
  { src: "music/rave_generator.mp3", from: T_MAP + MAP_VEGAS_AT, to: T_MAP + MAP_PREAMBLE_START, offset: 70 * FILM_FPS },
  // crowd pick #1: methodology breakdown, then the rankings countdown on its drops
  { src: "music/candy.mp3", from: T_MAP + MAP_PREAMBLE_START, to: T_PLAQUE, offset: 80 * FILM_FPS },
  // plaque story + Face saga + record cards ride Running's build/drop cycles
  { src: "music/running.mp3", from: T_PLAQUE, to: T_LASTYEAR, offset: 35 * FILM_FPS },
  // trash-talk block: 2025 recap, trade ledger, stakes, #FHO
  { src: "music/sexyback.mp3", from: T_LASTYEAR, to: T_CLOSER, offset: 58 * FILM_FPS },
  // crowd pick #2: the riff everyone knows = the 10..1 slam into the plaque
  { src: "music/teen_spirit.mp3", from: T_CLOSER, to: FILM_DURATION, offset: 32 * FILM_FPS },
];

const Soundtrack: React.FC = () => (
  <>
    {MEDLEY.map((t, i) => {
      const start = Math.max(0, t.from - FADE);
      const len = Math.min(t.to + FADE, FILM_DURATION) - start;
      const fadeIn = i === 0 ? 20 : 2 * FADE;
      const fadeOut = i === MEDLEY.length - 1 ? 40 : 2 * FADE;
      return (
        <Sequence key={t.src} from={start} durationInFrames={len}>
          <Audio
            src={staticFile(t.src)}
            startFrom={t.offset}
            volume={(f) =>
              interpolate(f, [0, fadeIn, len - fadeOut, len], [0, 0.9, 0.9, 0], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              })
            }
          />
        </Sequence>
      );
    })}
  </>
);

const font: React.CSSProperties = {
  fontFamily: "Arial, 'DejaVu Sans', sans-serif",
  fontWeight: 900,
  color: WHITE,
  textAlign: "center",
};

/* Scene 1 — TWENTY YEARS */
const Opening: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const punch = spring({ frame, fps, config: { damping: 11, stiffness: 160 } });
  const sub = spring({ frame: frame - 30, fps, config: { damping: 14 } });
  const flash = interpolate(frame, [0, 6], [1, 0], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: NAVY_DEEP, justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          ...font,
          fontSize: 220,
          letterSpacing: 8,
          color: CAROLINA_LIGHT,
          transform: `scale(${0.6 + punch * 0.4})`,
          textShadow: `0 0 90px ${CAROLINA}77`,
        }}
      >
        TWENTY
        <br />
        YEARS
      </div>
      <div style={{ ...font, fontSize: 42, letterSpacing: 26, marginTop: 46, opacity: sub }}>
        LEAGUE UNC&nbsp;&nbsp;·&nbsp;&nbsp;EST. 2006
      </div>
      <AbsoluteFill style={{ background: "#fff", opacity: flash * 0.9, pointerEvents: "none" }} />
    </AbsoluteFill>
  );
};

/* Scene 4 — the Face saga */
const FaceSaga: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const head = spring({ frame, fps, config: { damping: 13 } });
  const FLIP_START = 80;
  const PER = 13;
  const idx = Math.min(Math.floor(Math.max(0, frame - FLIP_START) / PER), FACE_NAMES.length - 1);
  const item = FACE_NAMES[idx];
  const last = idx === FACE_NAMES.length - 1;
  const lastS = spring({
    frame: frame - (FLIP_START + (FACE_NAMES.length - 1) * PER),
    fps,
    config: { damping: 11, stiffness: 170 },
  });
  return (
    <AbsoluteFill style={{ background: NAVY_DEEP, justifyContent: "center", alignItems: "center" }}>
      <div style={{ ...font, fontSize: 40, letterSpacing: 12, color: CAROLINA_LIGHT, opacity: head, position: "absolute", top: 130 }}>
        ONE MANAGER. SIX RINGS. EIGHTEEN NAMES.
      </div>
      {frame >= FLIP_START && (
        <>
          <div style={{ ...font, fontSize: 34, letterSpacing: 10, color: CAROLINA, marginBottom: 26 }}>
            {item.year}
          </div>
          <div
            style={{
              ...font,
              fontSize: item.name.length > 18 ? 84 : 110,
              letterSpacing: 3,
              maxWidth: 1700,
              color: last ? CAROLINA_LIGHT : WHITE,
              transform: last ? `scale(${0.9 + lastS * 0.25})` : undefined,
              textShadow: last ? `0 0 80px ${CAROLINA}aa` : "none",
            }}
          >
            {item.name.toUpperCase()}
          </div>
          {last && (
            <div style={{ ...font, fontSize: 40, letterSpacing: 8, marginTop: 44, color: WHITE, opacity: lastS }}>
              JAMES FARMER · DEFENDING CHAMPION
            </div>
          )}
        </>
      )}
    </AbsoluteFill>
  );
};

/* Scene 4.5 — 20 years of numbers */
const RECORDS = [
  { num: "12-0-1", label: "THE PERFECT SEASON", sub: "SINGER'S SECRET SAUCE · 2020" },
  { num: "1,623.7", label: "MOST POINTS EVER — AND NO RING", sub: "SINGER · 2018 · LOST THE FINAL" },
  { num: "943.5", label: "FEWEST POINTS EVER", sub: "FACE MASK · 2020 · WENT 1-12" },
  { num: "1,097.0", label: "TWIN SEASON TOTALS, TO THE DECIMAL", sub: "LINK & CRISP · 2019" },
  { num: "5", label: "RUNNER-UPS. ZERO RINGS.", sub: "ANGRY BYRDS · ALL-TIME" },
  { num: "19", label: "YEARS OF “POOP SHOOT”", sub: "KEVIN · NEVER ONCE CHANGED IT" },
];

const Records: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const head = spring({ frame, fps, config: { damping: 13 } });
  const START = 40;
  if (frame < START) {
    return (
      <AbsoluteFill style={{ background: NAVY_DEEP, justifyContent: "center", alignItems: "center" }}>
        <div style={{ ...font, fontSize: 60, letterSpacing: 18, color: CAROLINA_LIGHT, opacity: head }}>
          20 YEARS OF NUMBERS
        </div>
      </AbsoluteFill>
    );
  }
  const idx = Math.min(Math.floor((frame - START) / PER_RECORD), RECORDS.length - 1);
  const r = RECORDS[idx];
  const local = (frame - START) % PER_RECORD;
  const s = spring({ frame: local, fps, config: { damping: 10, stiffness: 190 } });
  return (
    <AbsoluteFill style={{ background: NAVY_DEEP, justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          ...font,
          fontSize: r.num.length > 5 ? 250 : 330,
          lineHeight: 1,
          color: CAROLINA_LIGHT,
          transform: `scale(${0.7 + s * 0.3})`,
          opacity: Math.min(1, s * 1.4),
          textShadow: `0 0 120px ${CAROLINA}66`,
        }}
      >
        {r.num}
      </div>
      <div style={{ ...font, fontSize: 54, letterSpacing: 4, marginTop: 40, opacity: s }}>{r.label}</div>
      <div style={{ ...font, fontSize: 28, letterSpacing: 8, marginTop: 20, color: CAROLINA, opacity: s }}>
        {r.sub}
      </div>
    </AbsoluteFill>
  );
};

/* Scene 4.75 — last season, the setup for revenge */
const LastYear: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const head = spring({ frame, fps, config: { damping: 13 } });
  const rows = STANDINGS[2025];
  const caption =
    frame < 160
      ? "FARMER WINS TITLE NUMBER SIX."
      : frame < 310
        ? "LINK: 11-3. MOST POINTS IN THE LEAGUE. SECOND. AGAIN."
        : "2026: EVERYBODY WANTS BLOOD.";
  const capColor = frame < 160 ? CAROLINA_LIGHT : frame < 310 ? RED : WHITE;
  return (
    <AbsoluteFill style={{ background: NAVY_DEEP, justifyContent: "center", alignItems: "center" }}>
      <div style={{ ...font, fontSize: 44, letterSpacing: 16, color: CAROLINA_LIGHT, opacity: head, position: "absolute", top: 64 }}>
        LAST SEASON · 2025
      </div>
      <div style={{ width: 1080, marginTop: 30 }}>
        {rows.map((r, i) => {
          const s = spring({ frame: frame - 20 - i * 7, fps, config: { damping: 13, stiffness: 160 } });
          const gold = r.rank === 1;
          const silver = r.rank === 2;
          return (
            <div
              key={r.rank}
              style={{
                display: "flex",
                alignItems: "baseline",
                gap: 24,
                padding: "9px 26px",
                marginBottom: 6,
                borderRadius: 8,
                background: gold
                  ? "linear-gradient(90deg, rgba(232,193,90,.28), rgba(232,193,90,.06))"
                  : silver
                    ? "linear-gradient(90deg, rgba(217,79,79,.25), rgba(217,79,79,.05))"
                    : "rgba(75,156,211,.07)",
                border: `1px solid ${gold ? "#e8c15a88" : silver ? `${RED}66` : `${CAROLINA}33`}`,
                opacity: s,
                transform: `translateX(${(1 - s) * -60}px)`,
              }}
            >
              <span style={{ ...font, fontSize: 26, color: gold ? "#e8c15a" : CAROLINA_LIGHT, width: 44, textAlign: "left" }}>
                {r.rank}
              </span>
              <span style={{ ...font, fontSize: 30, textAlign: "left", flex: 1 }}>{r.team.toUpperCase()}</span>
              <span style={{ ...font, fontSize: 24, color: CAROLINA_LIGHT }}>{r.manager.toUpperCase()}</span>
              <span style={{ ...font, fontSize: 26, width: 110, textAlign: "right" }}>{r.rec}</span>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", bottom: 40, width: "100%", textAlign: "center" }}>
        <div
          style={{
            ...font,
            display: "inline-block",
            padding: "14px 44px",
            borderRadius: 14,
            background: "rgba(4, 9, 18, 0.85)",
            border: `2px solid ${capColor === WHITE ? CAROLINA : capColor}66`,
            fontSize: 42,
            letterSpacing: 5,
            color: capColor,
          }}
        >
          {caption}
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* Scene 4.8 — the ledger: trades, and the 2026 board already in motion */
const BUDGET_MOVES: [string, number][] = [
  ["LESESNE", 100], ["CRISP", 60], ["NED", 45],
  ["FARMER", -10], ["OMAR", -35], ["BYRD", -60], ["LINK", -100],
];

const Ledger: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const head = spring({ frame, fps, config: { damping: 13 } });
  const GOLD = "#e8c15a";
  if (frame < 170) {
    const s1 = spring({ frame: frame - 25, fps, config: { damping: 12 } });
    const s2 = spring({ frame: frame - 80, fps, config: { damping: 12 } });
    return (
      <AbsoluteFill style={{ background: NAVY_DEEP, justifyContent: "center", alignItems: "center" }}>
        <div style={{ ...font, fontSize: 60, letterSpacing: 18, color: CAROLINA_LIGHT, opacity: head }}>
          THE LEDGER
        </div>
        <div style={{ ...font, fontSize: 110, letterSpacing: 4, color: GOLD, marginTop: 50, opacity: s1, transform: `scale(${0.7 + s1 * 0.3})` }}>
          71 TRADES
        </div>
        <div style={{ ...font, fontSize: 32, letterSpacing: 8, marginTop: 24, color: WHITE, opacity: s1 }}>
          LOGGED SINCE 2016
        </div>
        <div style={{ ...font, fontSize: 30, letterSpacing: 4, marginTop: 44, color: CAROLINA_LIGHT, opacity: s2, lineHeight: 1.7 }}>
          MOST: <span style={{ color: WHITE }}>FARMER · 23</span>
          &nbsp;&nbsp;&nbsp;FEWEST: <span style={{ color: WHITE }}>SINGER &amp; OMAR · 4</span>
          <br />
          <span style={{ fontSize: 26, color: CAROLINA }}>THE QUIET ONES HOLD FOUR RINGS.</span>
        </div>
      </AbsoluteFill>
    );
  }
  const local = frame - 170;
  const h2 = spring({ frame: local, fps, config: { damping: 13 } });
  return (
    <AbsoluteFill style={{ background: NAVY_DEEP, justifyContent: "center", alignItems: "center" }}>
      <div style={{ ...font, fontSize: 48, letterSpacing: 12, color: CAROLINA_LIGHT, opacity: h2, position: "absolute", top: 90 }}>
        2026 IS ALREADY IN MOTION
      </div>
      <div style={{ width: 900, marginTop: 20 }}>
        {BUDGET_MOVES.map(([who, amt], i) => {
          const s = spring({ frame: local - 25 - i * 12, fps, config: { damping: 13, stiffness: 160 } });
          const pos = amt > 0;
          return (
            <div
              key={who}
              style={{
                display: "flex",
                alignItems: "baseline",
                padding: "12px 30px",
                marginBottom: 8,
                borderRadius: 10,
                background: pos ? "rgba(93,190,120,.10)" : "rgba(217,79,79,.10)",
                border: `1px solid ${pos ? "#5dbe7866" : `${RED}55`}`,
                opacity: s,
                transform: `translateX(${(1 - s) * (pos ? -60 : 60)}px)`,
              }}
            >
              <span style={{ ...font, fontSize: 34, textAlign: "left", flex: 1 }}>{who}</span>
              <span style={{ ...font, fontSize: 38, color: pos ? "#5dbe78" : RED }}>
                {pos ? "+" : "−"}${Math.abs(amt)} DRAFT DOLLARS
              </span>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", bottom: 42, width: "100%", textAlign: "center" }}>
        <div
          style={{
            ...font,
            display: "inline-block",
            padding: "14px 44px",
            borderRadius: 14,
            background: "rgba(4, 9, 18, 0.85)",
            border: `2px solid ${CAROLINA}55`,
            fontSize: 30,
            letterSpacing: 3,
            color: WHITE,
            opacity: spring({ frame: local - 130, fps, config: { damping: 13 } }),
          }}
        >
          SAQUON, CHASE &amp; HENRY ALREADY MOVED. THE BOARD IS RIGGED BEFORE PICK ONE.
        </div>
      </div>
    </AbsoluteFill>
  );
};

/* Scene 5.5 — #FHO */
const FHO: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s1 = spring({ frame, fps, config: { damping: 10, stiffness: 180 } });
  const s2 = spring({ frame: frame - 40, fps, config: { damping: 13 } });
  const s3 = spring({ frame: frame - 95, fps, config: { damping: 12 } });
  return (
    <AbsoluteFill style={{ background: NAVY_DEEP, justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          ...font,
          fontSize: 170,
          letterSpacing: 10,
          color: "#e8c15a",
          opacity: s1,
          transform: `scale(${0.6 + s1 * 0.4})`,
          textShadow: "0 0 100px rgba(232,193,90,.5)",
        }}
      >
        #FHO
      </div>
      <div style={{ ...font, fontSize: 40, letterSpacing: 10, marginTop: 30, opacity: s2 }}>
        FAT HITS ONLY — ONE PARLAY. TEN LEGS. EVERYBODY IN.
      </div>
      <div style={{ ...font, fontSize: 30, letterSpacing: 5, marginTop: 26, color: CAROLINA_LIGHT, opacity: s3 }}>
        BEST EVER: 8 OF 10. THE SEARCH FOR THE FIRST HIT CONTINUES.
      </div>
    </AbsoluteFill>
  );
};

/* Scene 5 — the stakes */
const Stakes: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const items = ["$650 BUY-IN.", "$3,000 FOR FIRST.", "NO MERCY."];
  return (
    <AbsoluteFill
      style={{ background: NAVY_DEEP, justifyContent: "center", alignItems: "center", flexDirection: "row", gap: 90 }}
    >
      {items.map((t, i) => {
        const s = spring({ frame: frame - i * 16, fps, config: { damping: 10, stiffness: 190 } });
        return (
          <div
            key={t}
            style={{
              ...font,
              fontSize: 118,
              color: i === 2 ? RED : WHITE,
              opacity: s,
              transform: `scale(${0.5 + s * 0.5})`,
              textShadow: i === 2 ? "0 0 70px rgba(217,79,79,.5)" : `0 0 40px ${CAROLINA}44`,
            }}
          >
            {t}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/* Scene 6 — closer */
const Closer: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s1 = spring({ frame, fps, config: { damping: 12 } });
  const s2 = spring({ frame: frame - 25, fps, config: { damping: 13 } });
  const s3 = spring({ frame: frame - 120, fps, config: { damping: 12 } });
  const shine = interpolate(frame % 90, [0, 90], [-1200, 2400]);
  return (
    <AbsoluteFill style={{ background: NAVY_DEEP, justifyContent: "center", alignItems: "center" }}>
      <div style={{ ...font, fontSize: 44, letterSpacing: 24, color: CAROLINA, opacity: s1 }}>
        20TH ANNIVERSARY AUCTION
      </div>
      <div style={{ position: "relative", overflow: "hidden", padding: "10px 40px" }}>
        <div
          style={{
            ...font,
            fontSize: 190,
            letterSpacing: 6,
            color: CAROLINA_LIGHT,
            opacity: s2,
            transform: `translateY(${(1 - s2) * 80}px)`,
            textShadow: `0 0 110px ${CAROLINA}66`,
          }}
        >
          DRAFT NIGHT
          <br />
          2026
        </div>
        <div
          style={{
            position: "absolute",
            top: 0,
            bottom: 0,
            width: 220,
            left: shine,
            background: "linear-gradient(105deg, transparent 0%, rgba(255,255,255,.3) 50%, transparent 100%)",
          }}
        />
      </div>
      <div style={{ ...font, fontSize: 52, letterSpacing: 8, opacity: s3, marginTop: 36 }}>
        SOMEBODY'S GOTTA PAY.
      </div>
      <div style={{ ...font, fontSize: 30, letterSpacing: 12, opacity: s3, marginTop: 26, color: CAROLINA_LIGHT }}>
        AUGUST 28 · THE CHAMP'S HOUSE · LOTHIAN, MD
      </div>
    </AbsoluteFill>
  );
};

/* Scene 7 — the final countdown: 10..1, each number wearing a team's logo,
   in all-time order so 1 lands on the defending champ. */
const FinalCountdown: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const head = spring({ frame, fps, config: { damping: 13 } });
  const START = 60;
  if (frame < START) {
    return (
      <AbsoluteFill style={{ background: NAVY_DEEP, justifyContent: "center", alignItems: "center" }}>
        <div style={{ ...font, fontSize: 60, letterSpacing: 18, color: CAROLINA_LIGHT, opacity: head }}>
          THE 20TH AUCTION BEGINS IN…
        </div>
      </AbsoluteFill>
    );
  }
  const idx = Math.min(Math.floor((frame - START) / PER_TICK), 9); // 0..9 -> numbers 10..1
  const num = 10 - idx;
  const row = ALL_TIME[num - 1]; // all-time rank == displayed number
  const local = (frame - START) % PER_TICK;
  const s = spring({ frame: local, fps, config: { damping: 9, stiffness: 210 } });
  const isOne = num === 1;
  return (
    <AbsoluteFill style={{ background: NAVY_DEEP, justifyContent: "center", alignItems: "center" }}>
      <Img
        src={staticFile(`logos/${row.key.toLowerCase()}.png`)}
        style={{
          position: "absolute",
          width: 560,
          height: 560,
          borderRadius: "50%",
          opacity: 0.16,
          filter: "saturate(1.2)",
        }}
      />
      <div
        style={{
          ...font,
          fontSize: 560,
          lineHeight: 1,
          color: isOne ? CAROLINA_LIGHT : WHITE,
          transform: `scale(${0.6 + s * 0.4})`,
          opacity: Math.min(1, s * 1.5),
          textShadow: `0 0 140px ${isOne ? CAROLINA : "#000"}aa`,
        }}
      >
        {num}
      </div>
      <div style={{ position: "absolute", bottom: 80, width: "100%", textAlign: "center", opacity: s }}>
        <div
          style={{
            ...font,
            display: "inline-block",
            padding: "12px 40px",
            borderRadius: 12,
            background: "rgba(4, 9, 18, 0.85)",
            border: `2px solid ${CAROLINA}55`,
            fontSize: 36,
            letterSpacing: 8,
            color: CAROLINA_LIGHT,
          }}
        >
          {row.manager.toUpperCase()} · ALL-TIME #{num}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const Film: React.FC = () => (
  <AbsoluteFill style={{ background: NAVY_DEEP }}>
    {/* six-track league medley — see MEDLEY above */}
    <Soundtrack />
    <Sequence from={0} durationInFrames={OPEN_LEN}>
      <Opening />
    </Sequence>
    <Sequence from={T_MAP} durationInFrames={MAP_EMBED_DURATION}>
      <MapCountdown standalone={false} />
    </Sequence>
    <Sequence from={T_PLAQUE} durationInFrames={PLAQUE_DURATION}>
      <Plaque />
    </Sequence>
    <Sequence from={T_FACE} durationInFrames={FACE_LEN}>
      <FaceSaga />
    </Sequence>
    <Sequence from={T_RECORDS} durationInFrames={RECORDS_LEN}>
      <Records />
    </Sequence>
    <Sequence from={T_LASTYEAR} durationInFrames={LASTYEAR_LEN}>
      <LastYear />
    </Sequence>
    <Sequence from={T_LEDGER} durationInFrames={LEDGER_LEN}>
      <Ledger />
    </Sequence>
    <Sequence from={T_STAKES} durationInFrames={STAKES_LEN}>
      <Stakes />
    </Sequence>
    <Sequence from={T_FHO} durationInFrames={FHO_LEN}>
      <FHO />
    </Sequence>
    <Sequence from={T_CLOSER} durationInFrames={CLOSER_LEN}>
      <Closer />
    </Sequence>
    <Sequence from={T_TICKS} durationInFrames={TICKS_LEN}>
      <FinalCountdown />
    </Sequence>
    <Sequence from={T_FINALE} durationInFrames={PLAQUE_FINALE_DURATION}>
      <PlaqueFinale />
    </Sequence>
  </AbsoluteFill>
);
