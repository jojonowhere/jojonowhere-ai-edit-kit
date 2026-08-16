// Fits text to a box by actually measuring rendered glyph width (canvas
// 2D `measureText`), not by assuming a fixed per-character width ratio.
// The previous approach (`width / text.length`) implicitly assumed
// roughly-square CJK glyphs — correct for "先幫你踩雷" but badly
// under-sized Latin text like "Claude" (real characters run notably
// narrower than their font-size), which is exactly the bug this replaced.
// Works for any script/mix without per-language tuning.
export const fitFontSizeToBox = (
  text: string,
  boxWidth: number,
  boxHeight: number,
  fontFamily: string,
  fontWeight: number = 700,
  widthFillRatio: number = 0.88,
  heightFillRatio: number = 0.8,
): number => {
  const REF_SIZE = 200;
  let measuredWidth = text.length * REF_SIZE * 0.6; // fallback if canvas unavailable
  if (typeof document !== "undefined") {
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    if (ctx) {
      ctx.font = `${fontWeight} ${REF_SIZE}px ${fontFamily}`;
      measuredWidth = ctx.measureText(text).width || measuredWidth;
    }
  }
  const widthConstrained = ((boxWidth * widthFillRatio) / measuredWidth) * REF_SIZE;
  const heightConstrained = boxHeight * heightFillRatio;
  return Math.min(widthConstrained, heightConstrained);
};
