import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { CHAMPIONS } from "./data";

/* Digital recreation of the real rotating Champions Club plaque:
   dark wood, Carolina-blue band, gold plates, four empty rows waiting. */

const CAROLINA = "#7BAFD4";
const WOOD_DARK = "#2b1c10";
const WOOD = "#3a2817";
const WHITE = "#f4f8fc";

export const PLAQUE_DURATION = 840;

const PLATE_IN_START = 55;
const PLATE_STAGGER = 11;
const AUTOPILOT_AT = PLATE_IN_START + 20 * PLATE_STAGGER + 50; // both asterisk stories get a beat
const CONCESSION_AT = AUTOPILOT_AT + 170;
const NEXT_AT = CONCESSION_AT + 190;

const serif: React.CSSProperties = {
  fontFamily: "Georgia, 'Times New Roman', serif",
  fontWeight: 700,
  textAlign: "center",
};

const spanFor = (year: number) => `${year}-${year + 1}`;

export const Plaque: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const head = spring({ frame, fps, config: { damping: 13 } });
  const drift = interpolate(frame, [0, PLAQUE_DURATION], [1.0, 1.06]);
  const autopilot = frame >= AUTOPILOT_AT && frame < CONCESSION_AT;
  const concession = frame >= CONCESSION_AT;
  const autoS = spring({ frame: frame - AUTOPILOT_AT, fps, config: { damping: 13 } });
  const conS = spring({ frame: frame - CONCESSION_AT, fps, config: { damping: 13 } });
  const nextS = spring({ frame: frame - NEXT_AT, fps, config: { damping: 12 } });

  const plates = CHAMPIONS.map((c, i) => {
    const s = spring({
      frame: frame - PLATE_IN_START - i * PLATE_STAGGER,
      fps,
      config: { damping: 12, stiffness: 150 },
    });
    const star = c.year === 2006 || c.year === 2022;
    const highlight = (autopilot && c.year === 2006) || (concession && frame < NEXT_AT + 40 && c.year === 2022);
    return { ...c, s, star, highlight, idx: i };
  });

  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 50% 30%, ${WOOD} 0%, ${WOOD_DARK} 75%, #17100a 100%)`,
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <div style={{ transform: `scale(${drift})` }}>
        {/* plaque board */}
        <div
          style={{
            width: 1240,
            padding: "38px 46px 46px",
            borderRadius: 10,
            background: `linear-gradient(170deg, #43301b, ${WOOD_DARK})`,
            border: `3px solid ${CAROLINA}55`,
            boxShadow: "0 40px 120px rgba(0,0,0,.7), inset 0 0 60px rgba(0,0,0,.55)",
          }}
        >
          <div style={{ ...serif, fontSize: 52, letterSpacing: 6, color: WHITE, opacity: head }}>
            LEAGUE UNC
          </div>
          <div style={{ ...serif, fontSize: 26, letterSpacing: 10, color: WHITE, opacity: head, marginTop: 2 }}>
            FANTASY FOOTBALL
          </div>
          <div
            style={{
              ...serif,
              fontSize: 44,
              letterSpacing: 14,
              color: WOOD_DARK,
              background: CAROLINA,
              margin: "16px -46px 26px",
              padding: "8px 0",
              opacity: head,
            }}
          >
            CHAMPIONS CLUB
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(4, 1fr)",
              gap: "12px 14px",
            }}
          >
            {plates.map((p) => (
              <div
                key={p.year}
                style={{
                  height: 86,
                  borderRadius: 4,
                  padding: "10px 8px 0",
                  background: p.highlight
                    ? "linear-gradient(160deg, #ffe9a8, #e8c15a 55%, #c9a23e)"
                    : "linear-gradient(160deg, #e6d193, #cdb26a 60%, #b39950)",
                  border: `1px solid ${p.highlight ? "#fff3c4" : "#8a723f"}`,
                  boxShadow: p.highlight
                    ? "0 0 46px rgba(232,193,90,.85)"
                    : "0 3px 8px rgba(0,0,0,.5)",
                  opacity: p.s,
                  transform: `scale(${0.7 + p.s * 0.3})`,
                }}
              >
                <div style={{ ...serif, fontSize: 19, color: "#241a0c", lineHeight: 1.15 }}>
                  {p.star ? "* " : ""}
                  {p.manager.toUpperCase()}
                </div>
                <div
                  style={{
                    ...serif,
                    fontSize: p.team.length > 22 ? 13 : 16,
                    color: "#241a0c",
                    lineHeight: 1.15,
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                  }}
                >
                  {p.team}
                </div>
                <div style={{ ...serif, fontSize: 15, color: "#3a2c14" }}>{spanFor(p.year)}</div>
              </div>
            ))}
            {/* the empty plates — the future */}
            {[0, 1, 2, 3].map((i) => (
              <div
                key={`empty-${i}`}
                style={{
                  height: 86,
                  borderRadius: 4,
                  border: `1px solid ${CAROLINA}44`,
                  background: "rgba(0,0,0,.25)",
                  boxShadow:
                    i === 0 && frame >= NEXT_AT
                      ? `0 0 ${30 + 14 * Math.sin(frame / 6)}px ${CAROLINA}aa`
                      : "none",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                }}
              >
                {i === 0 && frame >= NEXT_AT && (
                  <div style={{ ...serif, fontSize: 22, color: CAROLINA, opacity: nextS }}>
                    2026-2027 · ?
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* autopilot caption */}
      {autopilot && (
        <div
          style={{
            position: "absolute",
            bottom: 46,
            width: "100%",
            textAlign: "center",
            ...serif,
            fontSize: 30,
            letterSpacing: 3,
            color: WHITE,
            opacity:
              autoS *
              interpolate(frame, [CONCESSION_AT - 20, CONCESSION_AT - 2], [1, 0], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
            textShadow: "0 2px 20px #000",
          }}
        >
          * 2006 — THE AUTOPILOT: LESESNE SKIPPED THE DRAFT. AUTOPICK TOOK LT &amp; BREES.
          <br />
          HE WON THE WHOLE THING.
        </div>
      )}

      {/* concession caption */}
      {concession && frame < NEXT_AT + 40 && (
        <div
          style={{
            position: "absolute",
            bottom: 46,
            width: "100%",
            textAlign: "center",
            ...serif,
            fontSize: 30,
            letterSpacing: 3,
            color: WHITE,
            opacity:
              conS *
              interpolate(frame, [NEXT_AT - 20, NEXT_AT + 20], [1, 0], {
                extrapolateLeft: "clamp",
                extrapolateRight: "clamp",
              }),
            textShadow: "0 2px 20px #000",
          }}
        >
          * 2022 — THE CONCESSION: UP BY LESS THAN A POINT WHEN THE HAMLIN GAME WAS SUSPENDED,
          <br />
          SINGER HANDED KEVIN THE RING.
        </div>
      )}
      {frame >= NEXT_AT + 50 && (
        <div
          style={{
            position: "absolute",
            bottom: 46,
            width: "100%",
            textAlign: "center",
            ...serif,
            fontSize: 34,
            letterSpacing: 5,
            color: CAROLINA,
            opacity: spring({ frame: frame - NEXT_AT - 50, fps, config: { damping: 13 } }),
            textShadow: "0 2px 20px #000",
          }}
        >
          ONE PLATE GETS ENGRAVED THIS YEAR.
        </div>
      )}
    </AbsoluteFill>
  );
};
