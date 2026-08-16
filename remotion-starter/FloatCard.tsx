import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";
import { floatSway } from "./nativeMotion";
import { glowPulse } from "./floatGlow";

// The "白框＋光暈＋懸浮" card treatment, factored out of JojoCard so
// ThreeToolsIcons can reuse the exact same look per-icon instead of
// duplicating the box-shadow/motion recipe three times.
export const FloatCard: React.FC<{
  children: React.ReactNode;
  padding: number;
  radius: number;
  phaseFrames?: number;
}> = ({ children, padding, radius, phaseFrames = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const pulse = glowPulse(frame, fps);
  const { bobY, rotate } = floatSway(frame, fps, phaseFrames);

  return (
    <div
      style={{
        transform: `translateY(${bobY}px) rotate(${rotate}deg)`,
        background: "#ffffff",
        borderRadius: radius,
        padding,
        boxShadow: [
          `0 ${padding * 0.5}px ${padding}px rgba(0,0,0,0.4)`,
          `0 0 ${26 + pulse * 16}px rgba(255,255,255,${pulse})`,
        ].join(", "),
      }}
    >
      {children}
    </div>
  );
};
