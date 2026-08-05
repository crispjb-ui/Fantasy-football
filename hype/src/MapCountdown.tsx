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
import { ALL_TIME, CHAMPIONS, DRAFT_VENUES, LOCATIONS, NAME_HISTORY, UNC, VENUE_PHOTOS } from "./data";
// eslint-disable-next-line @typescript-eslint/no-var-requires
const topo = require("us-atlas/states-10m.json");

/* ---- UNC palette ---- */
const NAVY = "#0d1f3c";
const NAVY_DEEP = "#081527";
const CAROLINA = "#4B9CD3";
const CAROLINA_LIGHT = "#7BAFD4";
const WHITE = "#f4f8fc";
const RED_ISH = "#d94f4f";
const GOLD = "#e8c15a";

export const MAP_FPS = 30;
const HOLD_CH = 70; // tight on Chapel Hill
const ZOOM_OUT_END = 160; // full USA visible
const ARCS_DONE = 280; // all arcs landed
const PER_STOP = 145; // frames per manager in the countdown — long enough to read & talk
const PREAMBLE = 380; // methodology card: formula builds term by term
/* Structure (Brett's order): champions & the venues they picked FIRST,
   then the methodology preamble, then the all-time rankings countdown. */
const JOURNEY_START = ARCS_DONE + 30;
const PER_LEG = 195; // slow burn: ~3.2s on the champ, ~3s on the venue + one-liner
const PER_LEG_LOST = 120; // lost-site years move quicker so the middle doesn't drag
const PHOTO_HOLD = 50; // stops with a draft-night photo linger on the polaroid
// per-leg extras: linger on the Emerald Isle punchline and the Lothian arrival
const LEG_EXTRA: Record<number, number> = { 2021: 100, 2026: 130 }; // keyed by venue year
export const MAP_JOURNEY_START = JOURNEY_START;

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

/* The journey: each champion (crowned at their home city) carries the league
   to the venue THEY picked for the next August. Missing venues = lost legs. */
type Leg = {
  champ: (typeof CHAMPIONS)[number];
  from: { x: number; y: number };
  to: { x: number; y: number } | null;
  venue: (typeof DRAFT_VENUES)[number];
  start: number; // frame offset within the journey
  len: number;
};
const LEGS: Leg[] = (() => {
  let t = 0;
  return CHAMPIONS.map((c) => {
    const venue = DRAFT_VENUES.find((v) => v.year === c.year + 1)!;
    const loc = LOCATIONS[c.key];
    const [hx, hy] = pt(loc.lng, loc.lat);
    const dx = c.key === "Link" ? 16 : c.key === "Crisp" ? -16 : 0;
    let to: { x: number; y: number } | null = null;
    if (venue.lat != null && venue.lng != null) {
      const [vx, vy] = pt(venue.lng, venue.lat);
      to = { x: vx, y: vy };
    }
    const leg: Leg = {
      champ: c,
      from: { x: hx + dx, y: hy },
      to,
      venue,
      start: t,
      len:
        (to ? PER_LEG : PER_LEG_LOST) +
        (LEG_EXTRA[venue.year] || 0) +
        PHOTO_HOLD * Math.min(VENUE_PHOTOS[venue.year]?.length ?? 0, 6),
    };
    t += leg.len;
    return leg;
  });
})();
const JOURNEY_LEN = LEGS.reduce((a, l) => a + l.len, 0);
const JOURNEY_END = JOURNEY_START + JOURNEY_LEN + 20;
const PREAMBLE_START = JOURNEY_END;
const COUNTDOWN_START = PREAMBLE_START + PREAMBLE;
const COUNTDOWN_END = COUNTDOWN_START + PER_STOP * 10;
export const MAP_DURATION = COUNTDOWN_END + 200; // standalone closer
export const MAP_EMBED_DURATION = COUNTDOWN_END + 60;
export const MAP_PREAMBLE_START = PREAMBLE_START;
/* music switch points: era boundaries in the journey */
export const MAP_VEGAS_AT = JOURNEY_START + (LEGS.find((l) => l.venue.year === 2011)?.start ?? 0);
export const MAP_BEACH_AT = JOURNEY_START + (LEGS.find((l) => l.venue.year === 2018)?.start ?? 0);
export const MAP_MODERN_AT = JOURNEY_START + (LEGS.find((l) => l.venue.year === 2022)?.start ?? 0);
const EMERALD_LEG = LEGS.find((l) => l.venue.year === 2021)!;
const BYRD_PT = (() => {
  const loc = LOCATIONS.Byrd;
  const [x, y] = pt(loc.lng, loc.lat);
  return { x, y };
})();

/* one line of lore per journey leg, keyed by VENUE year (champ = prior season) */
const LEG_LINES: Record<number, string> = {
  2007: "WON IT ON AUTOPILOT. THE LEAGUE NEVER FORGOT.",
  2008: "CHARM CITY SMASH WON. THE DRAFT WAS STILL A BROWSER TAB.",
  2009: "SINGER'S FIRST RING. NOBODY LEFT THE HOUSE FOR IT.",
  2010: "LINK'S ONLY RING. 16 YEARS AND COUNTING.",
  2011: "KEVIN'S RING PUT ALL TEN IN ONE ROOM — AND THAT ROOM WAS VEGAS.",
  2012: "FARMER BOOKED A RESTAURANT. THE FANCY ERA.",
  2013: "PEACHES WON AND MADE EVERYONE COME TO ATLANTA.",
  2014: "THE 7-6 MIRACLE EARNED OMAR THE CAPITAL.",
  2015: "FACE CAPITAL KEPT IT IN THE CAPITAL. BACK-TO-BACK DC.",
  2016: "OMAR'S SECOND RING — AND HE SENT EVERYONE BACK TO ATLANTA.",
  2017: "LESESNE'S THIRD RING. BACK TO THE STRIP.",
  2018: "THE MOST DOMINANT RUN EVER ENDED AT THE BEACH.",
  2019: "FARMER TOOK THE LEAGUE TO NYC. THE BOAT PARTY WAS A BONUS.",
  2020: "NED PICKED GOLF COUNTRY. THE HARPOONS SHARPENED.",
  2021: "12-0-1. PERFECTION PICKED THE FAMILY BEACH HOUSE.",
  2022: "ROB'S EXPECTATIONS — FINALLY GRRRRRREAT.",
  2023: "THE CONCEDED RING. KEVIN HOSTED ANYWAY.",
  2024: "THE COMMISH WON, THEN PICKED HIS OWN BACHELOR PARTY. VEGAS.",
  2025: "THE HARPOONS TOOK THE LEAGUE TO BIG SKY COUNTRY.",
  2026: "SIX RINGS IN, THE ROAD ENDS AT FARMER'S HOUSE.",
};

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
  // journey: full-USA view; drift in for the Emerald Isle gag and the Lothian arrival
  kfs.push({ t: JOURNEY_START, x: 960, y: 540, s: 1 });
  const emT = JOURNEY_START + EMERALD_LEG.start;
  kfs.push({ t: emT + PER_LEG - 10, x: 960, y: 540, s: 1 });
  kfs.push({ t: emT + PER_LEG + 40, x: BYRD_PT.x, y: BYRD_PT.y, s: 2.3 });
  kfs.push({ t: emT + EMERALD_LEG.len - 8, x: BYRD_PT.x, y: BYRD_PT.y, s: 2.3 });
  kfs.push({ t: emT + EMERALD_LEG.len + 26, x: 960, y: 540, s: 1 });
  const LOTHIAN = LEGS[LEGS.length - 1];
  const loT = JOURNEY_START + LOTHIAN.start;
  kfs.push({ t: loT + 70, x: 960, y: 540, s: 1 });
  if (LOTHIAN.to) {
    kfs.push({ t: loT + 124, x: LOTHIAN.to.x, y: LOTHIAN.to.y, s: 2.6 });
    kfs.push({ t: loT + LOTHIAN.len - 8, x: LOTHIAN.to.x, y: LOTHIAN.to.y, s: 2.6 });
  }
  kfs.push({ t: PREAMBLE_START + 20, x: 960, y: 540, s: 1 });
  kfs.push({ t: COUNTDOWN_START, x: 960, y: 540, s: 1 });
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

export const MapCountdown: React.FC<{ standalone?: boolean }> = ({ standalone = true }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const cam = camera(frame);
  const activeIdx =
    frame >= COUNTDOWN_START && frame < COUNTDOWN_END
      ? Math.floor((frame - COUNTDOWN_START) / PER_STOP)
      : -1;
  // during the journey, the reigning champion's home logo flares gold
  let champKeyNow: string | null = null;
  let legNow: Leg | null = null;
  let legLocal = 0;
  if (frame >= JOURNEY_START && frame < JOURNEY_END) {
    const local = frame - JOURNEY_START;
    legNow = LEGS.find((l) => local >= l.start && local < l.start + l.len) ?? null;
    if (legNow) {
      legLocal = local - legNow.start;
      if (legLocal < 60) champKeyNow = legNow.champ.key;
    }
  }

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
            const isChampNow = champKeyNow === st.key;
            const logoR = (landed ? (isChampNow ? 28 : 20) : 15) / Math.sqrt(cam.s);
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
                  <circle
                    r={logoR + 1.6 / Math.sqrt(cam.s)}
                    fill={NAVY_DEEP}
                    stroke={isChampNow ? GOLD : isActive ? WHITE : CAROLINA}
                    strokeWidth={(isChampNow ? 2.4 : 1.4) / Math.sqrt(cam.s)}
                    style={isChampNow ? { filter: `drop-shadow(0 0 ${10 / Math.sqrt(cam.s)}px ${GOLD})` } : undefined}
                  />
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

          {/* the journey: crown the champion at home (gold rings + logo swell),
              then a comet carries the league to the venue THEY picked. Every
              visited venue leaves a persistent gold diamond on the map. */}
          {frame >= JOURNEY_START - 10 && frame < PREAMBLE_START + 40 && (() => {
            const k = 1 / Math.sqrt(cam.s);
            const local = frame - JOURNEY_START;
            const dotsFade = interpolate(frame, [PREAMBLE_START, PREAMBLE_START + 30], [1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            });
            // persistent venue diamonds for every completed arrival
            const dots = LEGS.filter((l) => l.to && local >= l.start + 124);
            const diamond = (x: number, y: number, r: number, o: number, key: string) => (
              <path
                key={key}
                d={`M ${x} ${y - r} L ${x + r} ${y} L ${x} ${y + r} L ${x - r} ${y} Z`}
                fill={GOLD}
                opacity={o}
                stroke={NAVY_DEEP}
                strokeWidth={0.8 * k}
              />
            );
            let active: React.ReactNode = null;
            if (legNow) {
              const leg = legNow;
              const crownP = Math.min(1, legLocal / 34);
              active = (
                <g>
                  {/* crown flare at the champion's home */}
                  {legLocal < 40 && (
                    <>
                      <circle cx={leg.from.x} cy={leg.from.y} r={(14 + crownP * 42) * k} fill="none"
                        stroke={GOLD} strokeWidth={2.6 * (1 - crownP) * k} opacity={1 - crownP * 0.85} />
                      <circle cx={leg.from.x} cy={leg.from.y} r={(8 + crownP * 24) * k} fill="none"
                        stroke={WHITE} strokeWidth={1.6 * (1 - crownP) * k} opacity={0.85 * (1 - crownP)} />
                    </>
                  )}
                  {/* comet to the venue (when we know where it was) */}
                  {leg.to && legLocal >= 60 && (() => {
                    const p = Math.min(1, (legLocal - 60) / 56);
                    const eased = Easing.inOut(Easing.quad)(p);
                    const from: [number, number] = [leg.from.x, leg.from.y];
                    const to: [number, number] = [leg.to.x, leg.to.y];
                    const ctrl: [number, number] = [
                      (from[0] + to[0]) / 2,
                      Math.min(from[1], to[1]) - Math.max(50, Math.hypot(to[0] - from[0], to[1] - from[1]) * 0.3),
                    ];
                    const trail: [number, number][] = [];
                    if (p < 1) {
                      for (let j = 0; j < 10; j++) trail.push(bez(Math.max(0, eased - j * 0.05), from, ctrl, to));
                    }
                    const flareP = Math.min(1, Math.max(0, (legLocal - 116) / 20));
                    return (
                      <g>
                        {trail.map(([tx, ty], j) => (
                          <circle key={j} cx={tx} cy={ty} r={Math.max(1.2, 7.5 - j * 0.62) * k}
                            fill={j === 0 ? WHITE : CAROLINA_LIGHT}
                            opacity={j === 0 ? 1 : 0.55 * (1 - j / 10)}
                            style={j === 0 ? { filter: `drop-shadow(0 0 ${8 * k}px ${CAROLINA_LIGHT})` } : undefined} />
                        ))}
                        {p >= 1 && flareP < 1 && (
                          <>
                            <circle cx={to[0]} cy={to[1]} r={(14 + flareP * 38) * k} fill="none" stroke={GOLD}
                              strokeWidth={2.4 * (1 - flareP) * k} opacity={1 - flareP} />
                            <circle cx={to[0]} cy={to[1]} r={(9 + flareP * 20) * k} fill="none" stroke={WHITE}
                              strokeWidth={1.5 * (1 - flareP) * k} opacity={0.8 * (1 - flareP)} />
                          </>
                        )}
                      </g>
                    );
                  })()}
                </g>
              );
            }
            return (
              <g>
                {dots.map((l) => diamond(l.to!.x, l.to!.y, 6.5 * k, 0.95 * dotsFade, `v${l.venue.year}`))}
                {active}
                {/* Emerald Isle: the draft came here. the trophy never has. */}
                {legNow && legNow.venue.year === 2021 && legLocal >= PER_LEG + 20 && (
                  <circle cx={BYRD_PT.x} cy={BYRD_PT.y} r={(30 + 6 * Math.sin(frame / 5)) * k} fill="none"
                    stroke={RED_ISH} strokeWidth={2 * k} strokeDasharray={`${7 * k} ${5 * k}`} opacity={0.9} />
                )}
              </g>
            );
          })()}
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
      {frame >= ZOOM_OUT_END && frame < ARCS_DONE + 15 && (
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
            opacity: interpolate(frame, [ZOOM_OUT_END, ZOOM_OUT_END + 20, ARCS_DONE - 5, ARCS_DONE + 15], [0, 1, 1, 0], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
          }}
        >
          TEN MANAGERS. TEN CITIES. ONE LEAGUE.
        </div>
      )}

      {/* methodology preamble — the formula assembles itself, term by term
          (after the journey: champions & venues first, then the rankings) */}
      {frame >= PREAMBLE_START && frame < COUNTDOWN_START && (() => {
        const local = frame - PREAMBLE_START;
        const inS = spring({ frame: local, fps, config: { damping: 14 } });
        const out = interpolate(frame, [COUNTDOWN_START - 20, COUNTDOWN_START - 2], [1, 0], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const line = (delay: number) =>
          spring({ frame: local - delay, fps, config: { damping: 13, stiffness: 150 } });
        const TERMS = [
          { at: 85, coef: "2 ×", term: "AVG FINISH", why: "20 YEARS OF SHOWING UP" },
          { at: 155, coef: "3 ×", term: "TITLES", why: "WE PLAY FOR RINGS" },
          { at: 225, coef: "½ ×", term: "TOP-3 FINISHES", why: "CONTENDING COUNTS" },
        ];
        return (
          <AbsoluteFill style={{ background: `${NAVY_DEEP}d9`, justifyContent: "center", alignItems: "center", opacity: out }}>
            <div style={{ width: 1660, textAlign: "center" }}>
              <div style={{ ...font, fontSize: 54, letterSpacing: 14, color: CAROLINA_LIGHT, opacity: inS }}>
                THE ALL-TIME RANKINGS
              </div>
              <div style={{ ...font, fontSize: 26, letterSpacing: 4, color: WHITE, marginTop: 28, lineHeight: 1.6, opacity: line(18) }}>
                COMPILED INDEPENDENTLY BY CLAUDE — AN AI — FROM ALL 20 SEASONS OF FINAL STANDINGS.
                <br />
                NO MANAGER HAD INPUT. NO THUMB ON THE SCALE.
              </div>

              <div
                style={{
                  display: "flex",
                  alignItems: "stretch",
                  justifyContent: "center",
                  gap: 26,
                  marginTop: 54,
                }}
              >
                <div style={{ ...font, fontSize: 42, letterSpacing: 3, color: WHITE, alignSelf: "center", opacity: line(70) }}>
                  SCORE&nbsp;=
                </div>
                {TERMS.map((t, i) => {
                  const s = line(t.at);
                  return (
                    <React.Fragment key={t.term}>
                      {i > 0 && (
                        <div style={{ ...font, fontSize: 52, color: CAROLINA_LIGHT, alignSelf: "center", opacity: s }}>
                          +
                        </div>
                      )}
                      <div
                        style={{
                          padding: "26px 34px 22px",
                          border: `2px solid ${GOLD}88`,
                          borderRadius: 14,
                          background: `${GOLD}10`,
                          boxShadow: `0 0 ${34 * s}px ${GOLD}33`,
                          opacity: s,
                          transform: `translateY(${(1 - s) * 46}px) scale(${0.85 + s * 0.15})`,
                        }}
                      >
                        <div style={{ ...font, fontSize: 40, letterSpacing: 1, color: GOLD, whiteSpace: "nowrap" }}>
                          {t.coef} {t.term}
                        </div>
                        <div style={{ ...font, fontSize: 21, letterSpacing: 3, color: CAROLINA_LIGHT, marginTop: 12, whiteSpace: "nowrap" }}>
                          {t.why}
                        </div>
                      </div>
                    </React.Fragment>
                  );
                })}
              </div>

              <div style={{ ...font, fontSize: 26, letterSpacing: 6, color: WHITE, marginTop: 48, opacity: line(295) }}>
                TEN FRANCHISES ENTER. THE MATH DECIDES.
              </div>
            </div>
          </AbsoluteFill>
        );
      })()}
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

      {/* journey captions (screen space, readable from the couch) */}
      {frame >= JOURNEY_START && frame < JOURNEY_END && (
        <div
          style={{
            ...font,
            position: "absolute",
            top: 44,
            width: "100%",
            textAlign: "center",
            fontSize: 40,
            letterSpacing: 12,
            color: GOLD,
            opacity: interpolate(frame, [JOURNEY_START, JOURNEY_START + 20], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
            }),
            textShadow: "0 0 40px rgba(232,193,90,.4)",
          }}
        >
          WIN THE RING. PICK THE ROOM.
        </div>
      )}
      {legNow && (() => {
        const leg = legNow;
        const v = leg.venue;
        const isFinal = v.year === 2026;
        /* comet legs: pill hands off as the comet flies; lost legs sooner */
        const venueAt = leg.to ? 96 : 56;
        const champIn = spring({ frame: legLocal, fps, config: { damping: 14, stiffness: 160 } });
        const champOut = interpolate(legLocal, [venueAt - 22, venueAt - 8], [1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
        const venueIn = spring({ frame: legLocal - venueAt, fps, config: { damping: 14, stiffness: 160 } });
        const venueOut = interpolate(
          legLocal,
          v.year === 2021 ? [PER_LEG + 10, PER_LEG + 26] : [leg.len - 8, leg.len],
          [1, 0],
          { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
        );
        const venueLabel = v.city
          ? `${isFinal ? "AUG 28, 2026" : `AUG ${v.year}`} · ${(v.venue ? `${v.venue.toUpperCase()} · ` : "")}${v.city.toUpperCase()}${v.uncertain ? " (?)" : ""}${v.first ? " · THE FIRST LIVE DRAFT" : ""}`
          : v.online
            ? `${v.year} DRAFT · ONLINE. NOBODY LEFT THE HOUSE.`
            : `${v.year} DRAFT · SITE LOST TO HISTORY`;
        const photos = VENUE_PHOTOS[v.year] ?? [];
        return (
          <>
            {legLocal < venueAt - 6 && (
              <div style={{ position: "absolute", bottom: 54, width: "100%", textAlign: "center", opacity: champIn * champOut }}>
                <div
                  style={{
                    ...font,
                    display: "inline-block",
                    padding: "16px 46px",
                    borderRadius: 14,
                    background: `${NAVY_DEEP}e0`,
                    border: `2px solid ${GOLD}55`,
                    boxShadow: "0 10px 50px rgba(0,0,0,.7)",
                    fontSize: 46,
                    letterSpacing: 6,
                    color: WHITE,
                  }}
                >
                  <span style={{ color: GOLD }}>{leg.champ.year} CHAMP</span>
                  &nbsp;&nbsp;{leg.champ.team.toUpperCase()}
                  <span style={{ color: CAROLINA_LIGHT }}>&nbsp;&nbsp;· {leg.champ.manager.toUpperCase()}</span>
                </div>
              </div>
            )}
            {legLocal >= venueAt && (
              <div style={{ position: "absolute", bottom: 54, width: "100%", textAlign: "center", opacity: venueIn * venueOut }}>
                <div
                  style={{
                    ...font,
                    display: "inline-block",
                    padding: "16px 46px",
                    borderRadius: 14,
                    background: `${NAVY_DEEP}e0`,
                    border: `2px solid ${v.city ? (isFinal ? GOLD : `${CAROLINA}88`) : `${RED_ISH}55`}`,
                    boxShadow: isFinal ? `0 10px 50px rgba(0,0,0,.7), 0 0 50px ${GOLD}44` : "0 10px 50px rgba(0,0,0,.7)",
                    fontSize: isFinal ? 50 : 42,
                    letterSpacing: 5,
                    color: v.city ? WHITE : `${WHITE}bb`,
                  }}
                >
                  {v.city ? <span style={{ color: isFinal ? GOLD : CAROLINA_LIGHT }}>→&nbsp;&nbsp;</span> : null}
                  {venueLabel}
                  {LEG_LINES[v.year] && (
                    <div
                      style={{
                        ...font,
                        fontSize: 25,
                        letterSpacing: 3,
                        color: CAROLINA_LIGHT,
                        marginTop: 12,
                        opacity: interpolate(legLocal, [venueAt + 16, venueAt + 30], [0, 1], {
                          extrapolateLeft: "clamp",
                          extrapolateRight: "clamp",
                        }),
                      }}
                    >
                      {LEG_LINES[v.year]}
                    </div>
                  )}
                </div>
              </div>
            )}
            {/* draft-night photos burst OUT of the venue point on the map,
                fanning into polaroid slots (populated via VENUE_PHOTOS) */}
            {photos.length > 0 && leg.to && (() => {
              // venue position in screen space (tracks the live camera)
              const vsx = 960 + (leg.to.x - cam.x) * cam.s;
              const vsy = 540 + (leg.to.y - cam.y) * cam.s;
              const SLOTS = [
                { x: 1430, y: 300, r: 3.5 },
                { x: 1020, y: 260, r: -2.5 },
                { x: 1560, y: 700, r: -4 },
                { x: 1140, y: 640, r: 2.5 },
                { x: 720, y: 420, r: -3.5 },
                { x: 1700, y: 470, r: 2 },
                { x: 880, y: 700, r: 4 },
                { x: 1310, y: 480, r: -2 },
              ];
              const n = Math.min(photos.length, SLOTS.length);
              // polaroids shrink as the pile grows so the collage still fits
              const w = n <= 3 ? 340 : n <= 5 ? 290 : 250;
              return photos.slice(0, SLOTS.length).map((entry, i) => {
                // "file.jpg|CUSTOM CAPTION" overrides the default city-year label
                const [f, customCap] = entry.split("|");
                const t = legLocal - (venueAt + 12 + i * 14);
                if (t < 0) return null;
                const s = spring({ frame: t, fps, config: { damping: 13, stiffness: 110 } });
                const slot = SLOTS[i];
                const px = vsx + (slot.x - vsx) * s;
                const py = vsy + (slot.y - vsy) * s;
                return (
                  <div
                    key={f}
                    style={{
                      position: "absolute",
                      left: px,
                      top: py,
                      padding: "12px 12px 36px",
                      background: "#f6f2e8",
                      borderRadius: 4,
                      boxShadow: "0 24px 80px rgba(0,0,0,.75)",
                      transform: `translate(-50%, -50%) rotate(${slot.r * s}deg) scale(${0.08 + s * 0.92})`,
                    }}
                  >
                    <Img
                      src={staticFile(`photos/${f}`)}
                      style={{ width: w, maxHeight: Math.round(w * 1.15), objectFit: "cover", objectPosition: "50% 28%", display: "block" }}
                    />
                    {/* width pinned to the photo: without it a long caption
                        stretches the polaroid sideways into a white void */}
                    <div style={{ ...font, width: w, color: "#2a2318", fontSize: 19, letterSpacing: 3, lineHeight: 1.3, textAlign: "center", marginTop: 8 }}>
                      {customCap || (v.city ? `${v.city.toUpperCase()} · ${v.year}` : v.year)}
                    </div>
                  </div>
                );
              });
            })()}
            {/* the Emerald Isle punchline — the gag, corrected: the DRAFT made it here */}
            {v.year === 2021 && legLocal >= PER_LEG + 30 && (
              <div
                style={{
                  position: "absolute",
                  bottom: 54,
                  width: "100%",
                  textAlign: "center",
                  opacity: interpolate(legLocal, [PER_LEG + 30, PER_LEG + 48], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }),
                }}
              >
                <div
                  style={{
                    ...font,
                    display: "inline-block",
                    padding: "16px 46px",
                    borderRadius: 14,
                    background: `${NAVY_DEEP}e0`,
                    border: `2px solid ${RED_ISH}77`,
                    boxShadow: `0 10px 50px rgba(0,0,0,.7), 0 0 40px ${RED_ISH}33`,
                    fontSize: 42,
                    letterSpacing: 5,
                    color: RED_ISH,
                  }}
                >
                  THE DRAFT HAS BEEN TO EMERALD ISLE. THE TROPHY NEVER HAS.
                </div>
              </div>
            )}
          </>
        );
      })()}

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
