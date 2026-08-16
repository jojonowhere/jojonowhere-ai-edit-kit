import React from "react";
import { AbsoluteFill, interpolate, Easing, useCurrentFrame, useVideoConfig } from "remotion";
import { FONT_FAMILY } from "./loadFonts";
import "./loadFonts";
import { fitFontSizeToBox } from "./fitText";

// "蓋章式衝擊" — text slams down like a rubber stamp hitting paper: fast
// scale-down with a hard stop (no bounce-back, real stamps don't bounce),
// a brief camera-shake on impact, and a quick warning-red flash that
// settles to the caption's real color. Legibility over arbitrary video
// comes from a solid dark outline/shadow, not the white "floating card"
// glow used elsewhere — a red flash would fight a white rim glow.
export const StampImpactText: React.FC<{ text?: string; color?: string }> = ({
  text = "先幫你踩雷",
  color = "#ffffff",
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();

  const IMPACT = 7; // frame the stamp lands on

  // Composition width/height ARE the user's drawn box (see index.tsx) —
  // fontSize fills that box directly via actual glyph measurement, not a
  // guessed per-character ratio (see fitText.ts for why that broke on
  // Latin text like "Claude").
  const fontSize = fitFontSizeToBox(text, width, height, FONT_FAMILY, 700);

  const scale = interpolate(frame, [0, IMPACT], [2.4, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const opacity = interpolate(frame, [0, 3], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });

  // decaying shake for ~12 frames after impact
  const shakeEnv = interpolate(frame, [IMPACT, IMPACT + 12], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const shakeX = Math.sin(frame * 3.1) * 9 * shakeEnv;
  const shakeY = Math.cos(frame * 2.3) * 6 * shakeEnv;

  // red warning flash on impact, settling to the real color by ~+16 frames
  const flash = interpolate(frame, [IMPACT, IMPACT + 2, IMPACT + 16], [0, 1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const textColor = flash > 0 ? mixColor("#ff2d2d", color, 1 - flash) : color;

  return (
    <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center", fontFamily: FONT_FAMILY }}>
      <div style={{ transform: `translate(${shakeX}px, ${shakeY}px)` }}>
        <div
          style={{
            opacity,
            transform: `scale(${scale})`,
            fontSize,
            fontWeight: 700,
            color: textColor,
            textShadow: [
              "0 2px 0 rgba(0,0,0,0.85)",
              "0 4px 10px rgba(0,0,0,0.65)",
              "0 0 2px rgba(0,0,0,0.9)",
            ].join(", "),
            whiteSpace: "nowrap",
          }}
        >
          {text}
        </div>
      </div>
    </AbsoluteFill>
  );
};

function mixColor(a: string, b: string, t: number): string {
  const pa = hexToRgb(a);
  const pb = hexToRgb(b);
  const r = Math.round(pa.r + (pb.r - pa.r) * t);
  const g = Math.round(pa.g + (pb.g - pa.g) * t);
  const bl = Math.round(pa.b + (pb.b - pa.b) * t);
  return `rgb(${r},${g},${bl})`;
}
function hexToRgb(hex: string) {
  const h = hex.replace("#", "");
  return { r: parseInt(h.slice(0, 2), 16), g: parseInt(h.slice(2, 4), 16), b: parseInt(h.slice(4, 6), 16) };
}
