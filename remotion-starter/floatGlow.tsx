import React from "react";

// Precise two-part white halo, per spec: a solid pure-white ring hugging
// the shape for the first ~5px, then a soft glow fading from white down
// to transparent over roughly 5–50px out. This is NOT a drop-shadow (a
// single offset+blur pass reads as "gray shadow," not "glow") — it's built
// from an SVG filter: a small dilate for the crisp ring, a larger
// dilate+blur for the falloff, merged under the source image.
export const GLOW_FILTER_ID = "crispWhiteGlow";
export const GLOW_FILTER = `url(#${GLOW_FILTER_ID})`;

export const GlowDefs: React.FC<{ glowOpacity?: number }> = ({ glowOpacity = 0.85 }) => {
  return (
    <svg width={0} height={0} style={{ position: "absolute" }}>
      <defs>
        <filter id={GLOW_FILTER_ID} x="-100%" y="-100%" width="300%" height="300%">
          {/* soft outer halo: dilate further out, then blur heavily — the
              gradual falloff from ~5px to ~50px */}
          <feMorphology in="SourceAlpha" operator="dilate" radius={16} result="glowShape" />
          <feGaussianBlur in="glowShape" stdDeviation={13} result="glowBlur" />
          <feFlood floodColor="#ffffff" floodOpacity={glowOpacity} result="glowColor" />
          <feComposite in="glowColor" in2="glowBlur" operator="in" result="glow" />

          {/* crisp solid ring: small fixed dilate, no blur, full opacity */}
          <feMorphology in="SourceAlpha" operator="dilate" radius={5} result="ringShape" />
          <feFlood floodColor="#ffffff" floodOpacity={1} result="ringColor" />
          <feComposite in="ringColor" in2="ringShape" operator="in" result="ring" />

          <feMerge>
            <feMergeNode in="glow" />
            <feMergeNode in="ring" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
    </svg>
  );
};

export const glowPulse = (frame: number, fps: number): number => {
  return 0.75 + 0.15 * Math.sin((frame / fps) * ((2 * Math.PI) / 1.8));
};
