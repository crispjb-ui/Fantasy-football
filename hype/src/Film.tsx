import React from "react";
import {
  AbsoluteFill,
  Audio,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { MapCountdown, MAP_EMBED_DURATION } from "./MapCountdown";
import { Plaque, PLAQUE_DURATION } from "./Plaque";
import { NAME_HISTORY } from "./data";

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
const STAKES_LEN = 130;
const CLOSER_LEN = 300;

const T_MAP = OPEN_LEN;
const T_PLAQUE = T_MAP + MAP_EMBED_DURATION;
const T_FACE = T_PLAQUE + PLAQUE_DURATION;
const T_STAKES = T_FACE + FACE_LEN;
const T_CLOSER = T_STAKES + STAKES_LEN;
export const FILM_DURATION = T_CLOSER + CLOSER_LEN;

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

/* Scene 5 — the stakes */
const Stakes: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const items = ["$500.", "15 SPOTS.", "NO MERCY."];
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
    </AbsoluteFill>
  );
};

export const Film: React.FC = () => (
  <AbsoluteFill style={{ background: NAVY_DEEP }}>
    {/* placeholder score synthesized locally — swap for public/music.mp3 when Brett sends one */}
    <Audio src={staticFile("score.wav")} />
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
    <Sequence from={T_STAKES} durationInFrames={STAKES_LEN}>
      <Stakes />
    </Sequence>
    <Sequence from={T_CLOSER} durationInFrames={CLOSER_LEN}>
      <Closer />
    </Sequence>
  </AbsoluteFill>
);
