import React from "react";
import { Composition } from "remotion";
import { Hype, HYPE_DURATION, FPS } from "./Hype";

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
  </>
);
