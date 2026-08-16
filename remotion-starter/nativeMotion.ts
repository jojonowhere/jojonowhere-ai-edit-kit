import { spring, interpolate } from "remotion";

// "Native UI realism" motion language: overlays move the way the real OS
// element they're mimicking actually would (bounce-pop for icons, slide
// for sheets/banners). The visual treatment (glow vs. shadow) lives in
// floatGlow.tsx — this file is motion-only.

// Icon-style pop-in (iOS app icons appearing, a file "landing" in a
// folder): scale overshoots past 1 before settling — noticeably bouncier
// than the sheet/banner slide below.
export const bouncePop = (frame: number, fps: number, delayFrames: number = 0) => {
  const local = frame - delayFrames;
  const scale = spring({ frame: local, fps, from: 0, to: 1, config: { damping: 9, mass: 0.5, stiffness: 180 } });
  const opacity = interpolate(local, [0, 4], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  return { scale: local < 0 ? 0 : scale, opacity: local < 0 ? 0 : opacity };
};

// Sheet/banner slide (comment bar up from the bottom, notification banner
// down from the top): high damping, minimal-to-no overshoot — this is how
// iOS actually presents sheets and banners, not a springy bounce.
export const slideEase = (frame: number, fps: number, delayFrames: number = 0) => {
  const local = frame - delayFrames;
  const t = spring({ frame: local, fps, from: 0, to: 1, config: { damping: 20, mass: 0.8 } });
  return local < 0 ? 0 : t;
};

// Idle float/sway — for treatments that sit still mid-frame and gently
// breathe, rather than arriving from off-screen (unlike the two above).
// phaseFrames offsets the cycle so multiple cards floating together don't
// move in lockstep (matching the reference: each card drifts on its own).
export const floatSway = (frame: number, fps: number, phaseFrames: number = 0) => {
  const t = frame + phaseFrames;
  const bobY = Math.sin((t / fps) * ((2 * Math.PI) / 2.4)) * 10;
  const rotate = Math.sin((t / fps) * ((2 * Math.PI) / 3.2)) * 1.6;
  return { bobY, rotate };
};
