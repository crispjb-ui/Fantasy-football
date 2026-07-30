import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";

/* The REAL Champions Club plaque (photo from James' wall), treated
   cinematically: slow push-ins to the actual plates for the story beats. */

const CAROLINA = "#7BAFD4";
const WHITE = "#f4f8fc";
const BG = "#0a0806";

export const PLAQUE_DURATION = 840;
export const PLAQUE_FINALE_DURATION = 280;

/* photo geometry (public/plaque.png) */
const IMG_W = 1072;
const IMG_H = 1415;

/* focus keyframes: (image-px focus point, zoom). Beats:
   full reveal -> 2006 LaSizzle plate -> 2022 poop shoot plate -> empty rows -> pull back */
type Pkf = { t: number; fx: number; fy: number; s: number };
const PKFS: Pkf[] = [
  { t: 0, fx: 536, fy: 690, s: 0.98 },
  { t: 140, fx: 536, fy: 690, s: 1.05 },
  { t: 210, fx: 235, fy: 480, s: 2.5 }, // 2006-2007 LaSizzle (top-left plate)
  { t: 360, fx: 235, fy: 480, s: 2.5 },
  { t: 430, fx: 235, fy: 868, s: 2.5 }, // 2022-2023 poop shoot (bottom-left filled plate)
  { t: 580, fx: 235, fy: 868, s: 2.5 },
  { t: 650, fx: 560, fy: 1090, s: 1.75 }, // the empty rows
  { t: 770, fx: 560, fy: 1090, s: 1.75 },
  { t: PLAQUE_DURATION, fx: 536, fy: 690, s: 1.02 },
];

function photoCam(frame: number) {
  let a = PKFS[0];
  let b = PKFS[PKFS.length - 1];
  for (let i = 0; i < PKFS.length - 1; i++) {
    if (frame >= PKFS[i].t && frame <= PKFS[i + 1].t) {
      a = PKFS[i];
      b = PKFS[i + 1];
      break;
    }
  }
  const span = Math.max(1, b.t - a.t);
  const p = Easing.inOut(Easing.cubic)(Math.min(1, Math.max(0, (frame - a.t) / span)));
  const lerp = (u: number, v: number) => u + (v - u) * p;
  return { fx: lerp(a.fx, b.fx), fy: lerp(a.fy, b.fy), s: Math.exp(lerp(Math.log(a.s), Math.log(b.s))) };
}

/* Photo placed so the focus point sits at screen center, clamped so we never
   show a gap on a side the image could cover. */
const PlaquePhoto: React.FC<{ fx: number; fy: number; s: number; dim?: number; blur?: number }> = ({
  fx,
  fy,
  s,
  dim = 0,
  blur = 0,
}) => {
  const ds = (1080 * s) / IMG_H; // display px per image px
  const W = IMG_W * ds;
  const H = IMG_H * ds;
  let left = 960 - fx * ds;
  let top = 540 - fy * ds;
  left = W <= 1920 ? (1920 - W) / 2 : Math.min(0, Math.max(1920 - W, left));
  top = H <= 1080 ? (540 - fy * ds < 1080 - H ? 1080 - H : Math.min(0, top)) : Math.min(0, Math.max(1080 - H, top));
  if (H <= 1080) top = (1080 - H) / 2;
  return (
    <Img
      src={staticFile("plaque.png")}
      style={{
        position: "absolute",
        left,
        top,
        width: W,
        height: H,
        filter: `${blur ? `blur(${blur}px)` : ""} brightness(${1 - dim})`,
        boxShadow: "0 40px 140px rgba(0,0,0,.85)",
        borderRadius: 6,
      }}
    />
  );
};

const serif: React.CSSProperties = {
  fontFamily: "Georgia, 'Times New Roman', serif",
  fontWeight: 700,
  textAlign: "center",
};

const GOLD = "#e8c15a";

/* Lower-third callout: dark pill so it never washes out over the gold plates. */
const Caption: React.FC<{ from: number; to: number; label?: string; children: React.ReactNode }> = ({
  from,
  to,
  label,
  children,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (frame < from || frame > to + 20) return null;
  const s = spring({ frame: frame - from, fps, config: { damping: 13 } });
  const out = interpolate(frame, [to - 15, to + 15], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        position: "absolute",
        bottom: 44,
        width: "100%",
        textAlign: "center",
        opacity: s * out,
        transform: `translateY(${(1 - s) * 30}px)`,
      }}
    >
      <div
        style={{
          display: "inline-block",
          maxWidth: 1560,
          padding: "22px 52px",
          borderRadius: 16,
          background: "rgba(5, 4, 2, 0.88)",
          border: `2px solid ${GOLD}66`,
          boxShadow: "0 12px 60px rgba(0,0,0,.8)",
        }}
      >
        {label && (
          <div style={{ ...serif, fontSize: 30, letterSpacing: 5, color: GOLD, marginBottom: 10 }}>
            {label}
          </div>
        )}
        <div style={{ ...serif, fontSize: 34, letterSpacing: 2, color: WHITE, lineHeight: 1.4 }}>
          {children}
        </div>
      </div>
    </div>
  );
};

export const Plaque: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cam = photoCam(frame);
  const reveal = interpolate(frame, [0, 30], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const head = spring({ frame: frame - 10, fps, config: { damping: 13 } });
  return (
    <AbsoluteFill style={{ background: BG }}>
      <div style={{ position: "absolute", inset: 0, opacity: reveal }}>
        <PlaquePhoto fx={cam.fx} fy={cam.fy} s={cam.s} />
      </div>
      {/* vignette */}
      <AbsoluteFill
        style={{
          background: "radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,.6) 100%)",
          pointerEvents: "none",
        }}
      />
      {frame < 145 && (
        <div
          style={{
            position: "absolute",
            top: 40,
            width: "100%",
            textAlign: "center",
            opacity: head * interpolate(frame, [120, 145], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
          }}
        >
          <div
            style={{
              display: "inline-block",
              padding: "14px 44px",
              borderRadius: 14,
              background: "rgba(5, 4, 2, 0.82)",
              border: `2px solid ${CAROLINA}55`,
              ...serif,
              fontSize: 42,
              letterSpacing: 12,
              color: CAROLINA,
            }}
          >
            THE PLAQUE DOESN'T LIE.
          </div>
        </div>
      )}
      <Caption from={230} to={415} label="* 2006 · THE AUTOPILOT">
        YAHOO SNAKE DRAFT — LESESNE NEVER TOUCHED IT. AUTOPICK TOOK LT &amp; BREES.
        <br />
        SEASON-LONG TOTAL POINTS, NO MATCHUPS. HE WON THE WHOLE THING.
      </Caption>
      <Caption from={450} to={635} label="* 2022 · THE CONCESSION">
        HIGGINS PUT KEVIN OVER — THEN HAMLIN WENT DOWN AND THE GAME FROZE.
        <br />
        SINGER CONCEDED. THE NFL VOIDED THE GAME — SINGER WOULD'VE WON. HE LET IT STAND.
      </Caption>
      <Caption from={670} to={800}>
        <span style={{ color: CAROLINA, fontSize: 40 }}>ONE PLATE GETS ENGRAVED THIS YEAR.</span>
      </Caption>
    </AbsoluteFill>
  );
};

/* Finale: the real board, dimmed — START THE DRAFT. */
export const PlaqueFinale: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const push = interpolate(frame, [0, PLAQUE_FINALE_DURATION], [1.02, 1.14], {
    easing: Easing.out(Easing.quad),
  });
  const slam = spring({ frame: frame - 55, fps, config: { damping: 10, stiffness: 180 } });
  const flash = interpolate(frame, [55, 63], [0.9, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ background: BG }}>
      <PlaquePhoto fx={536} fy={690} s={push} dim={0.45} blur={2} />
      {frame >= 55 && (
        <div
          style={{
            position: "absolute",
            width: "100%",
            top: "32%",
            textAlign: "center",
            ...serif,
            fontWeight: 900,
            fontSize: 150,
            letterSpacing: 8,
            color: WHITE,
            transform: `scale(${0.7 + slam * 0.3})`,
            textShadow: `0 0 120px ${CAROLINA}, 0 4px 30px #000`,
          }}
        >
          START
          <br />
          THE DRAFT.
        </div>
      )}
      <AbsoluteFill style={{ background: "#fff", opacity: flash, pointerEvents: "none" }} />
    </AbsoluteFill>
  );
};
