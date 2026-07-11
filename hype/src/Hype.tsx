import React from "react";
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

export const FPS = 30;
export const HYPE_DURATION = 1080; // 36s

const GOLD = "#e8c15a";
const GOLD_DIM = "#a8842e";
const BG = "#07080c";
const WHITE = "#f2f4f8";
const RED = "#d94f4f";

const MANAGERS = [
  "SINGER", "FARMER", "LINK", "CRISP", "NOVA",
  "OMAR", "ROB", "LESESNE", "NED", "BYRD",
];

const TEAMS = [
  "DRUG RUNNER. CORP.",
  "ALLEN FACE ONE",
  "POOP SHOOT",
  "PEACHES, INC.",
  "POWER FADE",
  "SLAYING ASIANS",
  "SINGER'S SECRET SAUCE",
  "GRRRRRREAT EXPECTATIONS",
  "THE VERY VERY SHARP HARPOONS",
  "ANGRY BYRDS",
];

const HISTORY = [
  { name: "DERRICK HENRY", price: 159, year: 2022 },
  { name: "CHRISTIAN McCAFFREY", price: 150, year: 2022 },
  { name: "JONATHAN TAYLOR", price: 146, year: 2022 },
];

const font: React.CSSProperties = {
  fontFamily: "Arial, 'DejaVu Sans', sans-serif",
  fontWeight: 900,
  color: WHITE,
  textAlign: "center",
};

const Vignette: React.FC = () => (
  <AbsoluteFill
    style={{
      background:
        "radial-gradient(ellipse at center, rgba(0,0,0,0) 45%, rgba(0,0,0,.72) 100%)",
    }}
  />
);

const Grain: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <AbsoluteFill
      style={{
        opacity: 0.05,
        backgroundImage:
          "repeating-linear-gradient(0deg, #fff 0px, transparent 1px, transparent 3px)",
        transform: `translateY(${(frame % 3) - 1}px)`,
      }}
    />
  );
};

/* Scene 1 — TWENTY YEARS */
const Opening: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const punch = spring({ frame, fps, config: { damping: 11, stiffness: 160 } });
  const sub = spring({ frame: frame - 28, fps, config: { damping: 14 } });
  const flash = interpolate(frame, [0, 6], [1, 0], { extrapolateRight: "clamp" });
  return (
    <AbsoluteFill style={{ background: BG, justifyContent: "center", alignItems: "center" }}>
      <div
        style={{
          ...font,
          fontSize: 230,
          letterSpacing: 8,
          color: GOLD,
          transform: `scale(${0.6 + punch * 0.4})`,
          textShadow: "0 0 90px rgba(232,193,90,.45)",
        }}
      >
        TWENTY
        <br />
        YEARS
      </div>
      <div
        style={{
          ...font,
          fontSize: 44,
          letterSpacing: 26,
          marginTop: 50,
          color: WHITE,
          opacity: sub,
        }}
      >
        LEAGUE UNC&nbsp;&nbsp;·&nbsp;&nbsp;EST. 2007
      </div>
      <AbsoluteFill style={{ background: "#fff", opacity: flash * 0.9 }} />
    </AbsoluteFill>
  );
};

/* Scene 2 — the managers */
const Managers: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const head = spring({ frame, fps, config: { damping: 13 } });
  return (
    <AbsoluteFill style={{ background: BG, justifyContent: "center", alignItems: "center" }}>
      <div style={{ ...font, fontSize: 66, letterSpacing: 14, color: GOLD, opacity: head, marginBottom: 70 }}>
        TEN MANAGERS. ONE TITLE.
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(5, 320px)",
          gap: "38px 28px",
          justifyContent: "center",
        }}
      >
        {MANAGERS.map((m, i) => {
          const s = spring({ frame: frame - 12 - i * 6, fps, config: { damping: 12, stiffness: 140 } });
          return (
            <div
              key={m}
              style={{
                ...font,
                fontSize: 54,
                letterSpacing: 4,
                padding: "22px 0",
                border: `3px solid ${GOLD_DIM}`,
                borderRadius: 10,
                background: "rgba(232,193,90,.06)",
                opacity: s,
                transform: `translateY(${(1 - s) * 60}px)`,
              }}
            >
              {m}
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

/* Scene 3 — team names rapid fire */
const TeamCards: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const PER = 24;
  const idx = Math.min(Math.floor(frame / PER), TEAMS.length - 1);
  const local = frame - idx * PER;
  const s = spring({ frame: local, fps, config: { damping: 12, stiffness: 200 } });
  const hue = idx % 2 === 0 ? GOLD : WHITE;
  return (
    <AbsoluteFill style={{ background: BG, justifyContent: "center", alignItems: "center" }}>
      <div style={{ ...font, fontSize: 34, letterSpacing: 18, color: GOLD_DIM, position: "absolute", top: 120 }}>
        THE COMBATANTS
      </div>
      <div
        style={{
          ...font,
          fontSize: TEAMS[idx].length > 20 ? 96 : 140,
          letterSpacing: 4,
          color: hue,
          maxWidth: 1700,
          transform: `scale(${0.8 + s * 0.2}) rotate(${(1 - s) * (idx % 2 ? 2 : -2)}deg)`,
          opacity: Math.min(1, s * 1.4),
          textShadow: `0 0 60px ${hue}44`,
        }}
      >
        {TEAMS[idx]}
      </div>
      <div style={{ ...font, fontSize: 30, letterSpacing: 10, color: GOLD_DIM, position: "absolute", bottom: 110 }}>
        {String(idx + 1).padStart(2, "0")} / 10
      </div>
    </AbsoluteFill>
  );
};

/* Scene 4 — legends are bought */
const Legends: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const head = spring({ frame, fps, config: { damping: 13 } });
  return (
    <AbsoluteFill style={{ background: BG, justifyContent: "center", alignItems: "center" }}>
      <div style={{ ...font, fontSize: 84, letterSpacing: 6, color: WHITE, opacity: head, marginBottom: 80 }}>
        LEGENDS ARE <span style={{ color: GOLD }}>BOUGHT</span>, NOT BORN.
      </div>
      {HISTORY.map((h, i) => {
        const s = spring({ frame: frame - 25 - i * 14, fps, config: { damping: 13 } });
        const counted = Math.round(h.price * Math.min(1, Math.max(0, (frame - 25 - i * 14) / 30)));
        return (
          <div
            key={h.name}
            style={{
              display: "flex",
              width: 1250,
              justifyContent: "space-between",
              alignItems: "baseline",
              opacity: s,
              transform: `translateX(${(1 - s) * -80}px)`,
              borderBottom: `2px solid ${GOLD_DIM}55`,
              padding: "18px 10px",
            }}
          >
            <span style={{ ...font, fontSize: 56, letterSpacing: 3, textAlign: "left" }}>{h.name}</span>
            <span style={{ ...font, fontSize: 34, color: GOLD_DIM }}>{h.year}</span>
            <span style={{ ...font, fontSize: 72, color: GOLD, minWidth: 260, textAlign: "right" }}>
              ${counted}
            </span>
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/* Scene 5 — the stakes */
const Stakes: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const items = ["$500.", "15 SPOTS.", "NO MERCY."];
  return (
    <AbsoluteFill
      style={{ background: BG, justifyContent: "center", alignItems: "center", flexDirection: "row", gap: 90 }}
    >
      {items.map((t, i) => {
        const s = spring({ frame: frame - i * 16, fps, config: { damping: 10, stiffness: 190 } });
        return (
          <div
            key={t}
            style={{
              ...font,
              fontSize: 120,
              letterSpacing: 2,
              color: i === 2 ? RED : WHITE,
              opacity: s,
              transform: `scale(${0.5 + s * 0.5})`,
              textShadow: i === 2 ? "0 0 70px rgba(217,79,79,.5)" : "none",
            }}
          >
            {t}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};

/* Scene 6 — draft night closer */
const Closer: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s1 = spring({ frame, fps, config: { damping: 12 } });
  const s2 = spring({ frame: frame - 25, fps, config: { damping: 13 } });
  const s3 = spring({ frame: frame - 110, fps, config: { damping: 12 } });
  const shine = interpolate(frame % 90, [0, 90], [-1200, 2400]);
  return (
    <AbsoluteFill style={{ background: BG, justifyContent: "center", alignItems: "center" }}>
      <div style={{ ...font, fontSize: 46, letterSpacing: 24, color: GOLD_DIM, opacity: s1 }}>
        20TH ANNIVERSARY DRAFT
      </div>
      <div style={{ position: "relative", overflow: "hidden", padding: "10px 40px" }}>
        <div
          style={{
            ...font,
            fontSize: 200,
            letterSpacing: 6,
            color: GOLD,
            opacity: s2,
            transform: `translateY(${(1 - s2) * 80}px)`,
            textShadow: "0 0 110px rgba(232,193,90,.4)",
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
            background:
              "linear-gradient(105deg, transparent 0%, rgba(255,255,255,.35) 50%, transparent 100%)",
          }}
        />
      </div>
      <div style={{ ...font, fontSize: 54, letterSpacing: 8, color: WHITE, opacity: s3, marginTop: 40 }}>
        SOMEBODY'S GOTTA PAY.
      </div>
    </AbsoluteFill>
  );
};

export const Hype: React.FC = () => (
  <AbsoluteFill style={{ background: BG }}>
    <Sequence from={0} durationInFrames={120}>
      <Opening />
    </Sequence>
    <Sequence from={120} durationInFrames={150}>
      <Managers />
    </Sequence>
    <Sequence from={270} durationInFrames={240}>
      <TeamCards />
    </Sequence>
    <Sequence from={510} durationInFrames={180}>
      <Legends />
    </Sequence>
    <Sequence from={690} durationInFrames={120}>
      <Stakes />
    </Sequence>
    <Sequence from={810} durationInFrames={270}>
      <Closer />
    </Sequence>
    <Vignette />
    <Grain />
  </AbsoluteFill>
);
