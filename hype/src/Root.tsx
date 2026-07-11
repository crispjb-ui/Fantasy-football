import React from "react";
import { Composition } from "remotion";
import { Hype, HYPE_DURATION, FPS } from "./Hype";
import { MapCountdown, MAP_DURATION, MAP_FPS } from "./MapCountdown";

export const Root: React.FC = () => (
  <>
    <Composition
      id="Hype"
      component={Hype}
      durationInFrames={HYPE_DURATION}
      fps={FPS}
      width={1920}
      height={1080}
    />
    <Composition
      id="MapCountdown"
      component={MapCountdown}
      durationInFrames={MAP_DURATION}
      fps={MAP_FPS}
      width={1920}
      height={1080}
    />
  </>
);
