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
import { feature, mesh } from "topojson-client";
import { geoAlbersUsa, geoPath } from "d3-geo";
import { ALL_TIME, LOCATIONS, NAME_HISTORY, UNC } from "./data";
// eslint-disable-next-line @typescript-eslint/no-var-requires
const topo = require("us-atlas/states-10m.json");

/* ---- UNC palette ---- */
const NAVY = "#0d1f3c";
const NAVY_DEEP = "#081527";
const CAROLINA = "#4B9CD3";
const CAROLINA_LIGHT = "#7BAFD4";
const WHITE = "#f4f8fc";

export const MAP_FPS = 30;
const HOLD_CH = 70; // tight on Chapel Hill
const ZOOM_OUT_END = 160; // full USA visible
const ARCS_DONE = 280; // all arcs landed
const PER_STOP = 100; // frames per manager in the countdown
const COUNTDOWN_START = ARCS_DONE;
const COUNTDOWN_END = COUNTDOWN_START + PER_STOP * 10;
export const MAP_DURATION = COUNTDOWN_END + 110; // pull back + hold

/* ---- geo (computed once) ---- */
const nation = feature(topo, topo.objects.nation) as any;
const stateLines = mesh(topo, topo.objects.states, (a: any, b: any) => a !== b);
const projection = geoAlbersUsa().fitExtent(
  [
    [80, 70],
    [1840, 1010],
  ],
  nation
);
const path = geoPath(projection);
const NATION_D = path(nation) as string;
const STATES_D = path(stateLines) as string;

const pt = (lng: number, lat: number) => projection([lng, lat]) as [number, number];
const CH = pt(UNC.lng, UNC.lat);

/* Countdown order: worst first. ALL_TIME is best->worst, so reverse. */
const STOPS = [...ALL_TIME].reverse().map((row, i) => {
  const loc = LOCATIONS[row.key];
  const [x, y] = pt(loc.lng, loc.lat);
  // Crisp & Link share Charleston — nudge apart so both dots/logos read
  const dx = row.key === "Link" ? 16 : row.key === "Crisp" ? -16 : 0;
  const hist = NAME_HISTORY[row.key];
  return {
    ...row,
    city: loc.city,
    x: x + dx,
    y,
    teamNow: hist[hist.length - 1].name,
    order: i, // 0 = worst (rank 10)
  };
});

const TAGLINES: Record<string, string> = {
  Crisp: "2017: THE MOST DOMINANT TITLE RUN EVER. SINCE: PAIN.",
  Rob: "GRRRRRREAT EXPECTATIONS — FINALLY MET IN 2021.",
  Link: "16 YEARS SINCE THE RING. 11-3 LAST YEAR. STILL WAITING.",
  Ned: "TWO TITLES. THE HARPOONS KEEP GETTING SHARPER.",
  Lesesne: "THE FIRST CHAMP EVER (LaSIZZLE, 2006). THREE RINGS.",
  Byrd: "RESUME: 1ST ALL-TIME. RINGS: ZERO.",
  Omar: "TWO TITLES — INCLUDING THE 7-6 MIRACLE OF 2013.",
  Kevin: "SAME NAME 19 YEARS. TWO RINGS, 12 YEARS APART.",
  Singer: "12-0-1 IN 2020. THE ONLY PERFECT SEASON.",
  Farmer: "SIX TITLES. SIX DIFFERENT FACES.",
};

/* piecewise camera keyframes with cubic ease per segment */
type Kf = { t: number; x: number; y: number; s: number };
const KFS: Kf[] = (() => {
  const usa: Kf = { t: ZOOM_OUT_END, x: 960, y: 540, s: 1 };
  const kfs: Kf[] = [
    { t: 0, x: CH[0], y: CH[1], s: 9 },
    { t: HOLD_CH, x: CH[0], y: CH[1], s: 9 },
    usa,
    { t: ARCS_DONE, x: 960, y: 540, s: 1 },
  ];
  STOPS.forEach((st, i) => {
    const t0 = COUNTDOWN_START + i * PER_STOP;
    kfs.push({ t: t0 + 26, x: st.x, y: st.y, s: 3.1 });
    kfs.push({ t: t0 + PER_STOP, x: st.x, y: st.y, s: 3.1 });
  });
  kfs.push({ t: COUNTDOWN_END + 60, x: 960, y: 540, s: 1 });
  kfs.push({ t: MAP_DURATION, x: 960, y: 540, s: 1 });
  return kfs;
})();

function camera(frame: number) {
  let a = KFS[0];
  let b = KFS[KFS.length - 1];
  for (let i = 0; i < KFS.length - 1; i++) {
    if (frame >= KFS[i].t && frame <= KFS[i + 1].t) {
      a = KFS[i];
      b = KFS[i + 1];
      break;
    }
  }
  const span = Math.max(1, b.t - a.t);
  const p = Easing.inOut(Easing.cubic)(Math.min(1, Math.max(0, (frame - a.t) / span)));
  const lerp = (u: number, v: number) => u + (v - u) * p;
  // zoom in log space so push-ins feel constant-speed
  const s = Math.exp(lerp(Math.log(a.s), Math.log(b.s)));
  return { x: lerp(a.x, b.x), y: lerp(a.y, b.y), s };
}

const bez = (t: number, p0: [number, number], p1: [number, number], p2: [number, number]) =>
  [
    (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
    (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1],
  ] as [number, number];

const arcCtrl = (a: [number, number], b: [number, number]): [number, number] => {
  const mx = (a[0] + b[0]) / 2;
  const my = (a[1] + b[1]) / 2;
  const dist = Math.hypot(b[0] - a[0], b[1] - a[1]);
  return [mx, my - Math.max(60, dist * 0.28)]; // arch upward
};

const font: React.CSSProperties = {
  fontFamily: "Arial, 'DejaVu Sans', sans-serif",
  fontWeight: 900,
  color: WHITE,
};

/* standalone=false when embedded in the full Film (its closer is handled there) */
export const MAP_EMBED_DURATION = COUNTDOWN_END + 60;

export const MapCountdown: React.FC<{ standalone?: boolean }> = ({ standalone = true }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cam = camera(frame);
  const activeIdx =
    frame >= COUNTDOWN_START && frame < COUNTDOWN_END
      ? Math.floor((frame - COUNTDOWN_START) / PER_STOP)
      : -1;

  return (
    <AbsoluteFill style={{ background: `radial-gradient(ellipse at 50% 40%, ${NAVY} 0%, ${NAVY_DEEP} 78%)` }}>
      <svg
        width={1920}
        height={1080}
        style={{ position: "absolute", inset: 0 }}
        viewBox="0 0 1920 1080"
      >
        <g
          transform={`translate(960 540) scale(${cam.s}) translate(${-cam.x} ${-cam.y})`}
        >
          {/* USA */}
          <path d={NATION_D} fill="#12294a" stroke={CAROLINA} strokeWidth={2 / cam.s} />
          <path d={STATES_D} fill="none" stroke={CAROLINA} strokeOpacity={0.28} strokeWidth={0.8 / cam.s} />

          {/* Chapel Hill beacon + the real interlocking NC */}
          {(() => {
            const pulse = 1 + 0.25 * Math.sin(frame / 7);
            const k = 1 / Math.sqrt(cam.s); // gentle counter-scale so it reads at every zoom
            const lw = 52 * k; // logo width (unc.png is 211x176)
            const lh = lw * (176 / 211);
            return (
              <g>
                <circle cx={CH[0]} cy={CH[1]} r={30 * pulse * k} fill={CAROLINA} opacity={0.2} />
                <image
                  href={staticFile("logos/unc.png")}
                  x={CH[0] - lw / 2}
                  y={CH[1] - lh / 2}
                  width={lw}
                  height={lh}
                />
              </g>
            );
          })()}

          {/* arcs + traveling logos */}
          {STOPS.map((st, i) => {
            const start = ZOOM_OUT_END - 20 + i * 9;
            const draw = interpolate(frame, [start, start + 55], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            });
            if (draw <= 0) return null;
            const end: [number, number] = [st.x, st.y];
            const ctrl = arcCtrl(CH, end);
            const [lx, ly] = bez(draw, CH, ctrl, end);
            const landed = draw >= 1;
            const isActive = activeIdx === st.order;
            const logoR = (landed ? 20 : 15) / Math.sqrt(cam.s);
            return (
              <g key={st.key}>
                <path
                  d={`M ${CH[0]} ${CH[1]} Q ${ctrl[0]} ${ctrl[1]} ${end[0]} ${end[1]}`}
                  fill="none"
                  stroke={isActive ? WHITE : CAROLINA_LIGHT}
                  strokeOpacity={isActive ? 0.95 : 0.55}
                  strokeWidth={(isActive ? 2.6 : 1.4) / cam.s}
                  pathLength={1}
                  strokeDasharray={1}
                  strokeDashoffset={1 - draw}
                />
                {isActive && (
                  <circle
                    cx={end[0]}
                    cy={end[1]}
                    r={(26 + 6 * Math.sin(frame / 5)) / Math.sqrt(cam.s)}
                    fill="none"
                    stroke={WHITE}
                    strokeWidth={1.6 / cam.s}
                    opacity={0.8}
                  />
                )}
                <g transform={`translate(${lx} ${ly})`}>
                  <clipPath id={`clip-${st.key}`}>
                    <circle r={logoR} />
                  </clipPath>
                  <circle r={logoR + 1.6 / Math.sqrt(cam.s)} fill={NAVY_DEEP} stroke={isActive ? WHITE : CAROLINA} strokeWidth={1.4 / Math.sqrt(cam.s)} />
                  <image
                    href={staticFile(`logos/${st.key.toLowerCase()}.png`)}
                    x={-logoR}
                    y={-logoR}
                    width={logoR * 2}
                    height={logoR * 2}
                    clipPath={`url(#clip-${st.key})`}
                  />
                </g>
              </g>
            );
          })}
        </g>
      </svg>

      {/* phase titles (screen space) */}
      {frame < ZOOM_OUT_END && (
        <div
          style={{
            ...font,
            position: "absolute",
            top: 96,
            width: "100%",
            textAlign: "center",
            fontSize: 58,
            letterSpacing: 16,
            color: CAROLINA_LIGHT,
            opacity: interpolate(frame, [8, 30, HOLD_CH + 40, ZOOM_OUT_END - 10], [0, 1, 1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            textShadow: `0 0 40px ${CAROLINA}66`,
          }}
        >
          CHAPEL HILL, NC
          <div style={{ fontSize: 30, letterSpacing: 8, marginTop: 16, color: WHITE }}>
            WHERE IT STARTED · EST. 2006
          </div>
        </div>
      )}
      {frame >= ZOOM_OUT_END && frame < COUNTDOWN_START && (
        <div
          style={{
            ...font,
            position: "absolute",
            top: 60,
            width: "100%",
            textAlign: "center",
            fontSize: 52,
            letterSpacing: 12,
            color: WHITE,
            opacity: interpolate(frame, [ZOOM_OUT_END, ZOOM_OUT_END + 20], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          TEN MANAGERS. TEN CITIES. ONE LEAGUE.
        </div>
      )}
      {activeIdx >= 0 && (
        <div
          style={{
            ...font,
            position: "absolute",
            top: 44,
            width: "100%",
            textAlign: "center",
            fontSize: 34,
            letterSpacing: 14,
            color: CAROLINA_LIGHT,
          }}
        >
          ALL-TIME · WORST → BEST
        </div>
      )}

      {/* countdown card */}
      {activeIdx >= 0 &&
        (() => {
          const st = STOPS[activeIdx];
          const local = frame - (COUNTDOWN_START + activeIdx * PER_STOP);
          const enter = spring({ frame: local - 22, fps, config: { damping: 14, stiffness: 130 } });
          const exit = interpolate(local, [PER_STOP - 10, PER_STOP - 2], [1, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const left = activeIdx % 2 === 0;
          const titleYrs = st.titles.length ? st.titles.map(String).join(" · ") : "—";
          return (
            <div
              style={{
                position: "absolute",
                top: 200,
                [left ? "left" : "right"]: 90,
                width: 660,
                padding: "34px 40px",
                borderRadius: 18,
                background: `linear-gradient(160deg, ${NAVY}f2, ${NAVY_DEEP}f2)`,
                border: `2px solid ${CAROLINA}`,
                boxShadow: `0 0 80px ${CAROLINA}33`,
                opacity: enter * exit,
                transform: `translateX(${(1 - enter) * (left ? -80 : 80)}px)`,
              } as React.CSSProperties}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 26 }}>
                <div style={{ ...font, fontSize: 92, color: CAROLINA_LIGHT, lineHeight: 1 }}>
                  #{10 - st.order}
                </div>
                <Img
                  src={staticFile(`logos/${st.key.toLowerCase()}.png`)}
                  style={{ width: 108, height: 108, borderRadius: "50%", border: `3px solid ${CAROLINA}` }}
                />
                <div>
                  <div style={{ ...font, fontSize: 40, lineHeight: 1.1 }}>{st.teamNow.toUpperCase()}</div>
                  <div style={{ ...font, fontSize: 24, color: CAROLINA_LIGHT, marginTop: 6 }}>
                    {st.manager.toUpperCase()} · {st.city.toUpperCase()}
                  </div>
                </div>
              </div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginTop: 26,
                  paddingTop: 20,
                  borderTop: `1px solid ${CAROLINA}55`,
                }}
              >
                {[
                  ["RECORD", st.record],
                  ["WIN %", `.${Math.round(st.winPct * 1000)}`],
                  ["AVG FINISH", st.avgFinish.toFixed(1)],
                  ["TITLES", titleYrs],
                ].map(([k, v]) => (
                  <div key={k} style={{ textAlign: "center" }}>
                    <div style={{ ...font, fontSize: 18, letterSpacing: 3, color: CAROLINA_LIGHT }}>{k}</div>
                    <div style={{ ...font, fontSize: 30, marginTop: 4 }}>{v}</div>
                  </div>
                ))}
              </div>
              <div style={{ ...font, fontSize: 23, marginTop: 22, color: WHITE, letterSpacing: 1 }}>
                {TAGLINES[st.key]}
              </div>
            </div>
          );
        })()}

      {/* closer */}
      {standalone && frame >= COUNTDOWN_END + 40 && (
        <div
          style={{
            ...font,
            position: "absolute",
            top: "40%",
            width: "100%",
            textAlign: "center",
            fontSize: 96,
            letterSpacing: 10,
            color: WHITE,
            opacity: interpolate(frame, [COUNTDOWN_END + 45, COUNTDOWN_END + 70], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            textShadow: `0 0 90px ${CAROLINA}88`,
          }}
        >
          20 YEARS. ONE ROOM.
          <div style={{ fontSize: 40, letterSpacing: 20, marginTop: 30, color: CAROLINA_LIGHT }}>
            DRAFT NIGHT 2026
          </div>
        </div>
      )}
    </AbsoluteFill>
  );
};
