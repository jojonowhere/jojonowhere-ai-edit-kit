import React from "react";
import { useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";
import { FloatCard } from "./FloatCard";
import { bouncePop } from "./nativeMotion";

// 「數字跳動 + 光暈」的 PR 值揭曉動畫，配色直接照 JoJo 便宜機票查詢台
// 網頁上那個 PR 標籤（見 flight_query_console.html 的 --cat-price /
// --cat-price-bg），讓影片裡的動畫跟工具本身的視覺是同一套語言，
// 不是另外設計一套。數字用 IBM Plex Mono，跟網頁的 --font-mono 一致。
//
// 時間軸（30fps 假設，startFrame 是這個元件開始動的那一格）：
//   0–4    FloatCard 彈出（bouncePop），標籤還是中性灰色，顯示 "PR --"
//   4–19   數字從 0 快速跳到 prValue，ease-out（一開始跳很快、最後變慢，
//          像吃角子老虎定格的感覺，不是等速跑）
//   19     顏色從灰瞬間切成粉紅（--cat-price-bg / --cat-price）——這是
//          「開獎」的瞬間，色彩用瞬切不是漸層，跳動停下來的同一格顏色
//          就到位，兩個效果疊在同一個節點上，力道才夠
//   19+    FloatCard 本身自帶的 glowPulse 持續呼吸，維持這是重點的訊號

const NEUTRAL_BG = "#e5d8bf"; // 揭曉前：中性灰調，跟工具的 --line-strong 同色系，不用另外挑色
const NEUTRAL_TEXT = "#7c6f59"; // 對應 --ink-muted
const PR_BG = "#f3dde2"; // --cat-price-bg
const PR_TEXT = "#9c3d52"; // --cat-price

export const PRBadgeReveal: React.FC<{
  prValue: number;
  startFrame: number;
  phaseFrames?: number;
}> = ({ prValue, startFrame, phaseFrames = 0 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const local = frame - startFrame;

  const { scale, opacity } = bouncePop(local, fps, 0);

  const countProgress = interpolate(local, [4, 19], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  const displayValue = local < 4 ? null : Math.round(countProgress * prValue);
  const revealed = local >= 19;

  return (
    <div style={{ transform: `scale(${scale})`, opacity }}>
      <FloatCard padding={28} radius={20} phaseFrames={phaseFrames}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 14,
            background: revealed ? PR_BG : NEUTRAL_BG,
            borderRadius: 999,
            padding: "14px 32px",
            // 顏色瞬切，不用 transition——這裡要的是「開獎」的力道，
            // 漸層過渡反而會讓這個瞬間感覺軟掉。
          }}
        >
          <span
            style={{
              fontFamily: "IBM Plex Mono, monospace",
              fontWeight: 600,
              fontSize: 22,
              letterSpacing: "0.02em",
              color: revealed ? PR_TEXT : NEUTRAL_TEXT,
            }}
          >
            PR
          </span>
          <span
            style={{
              fontFamily: "IBM Plex Mono, monospace",
              fontWeight: 700,
              fontSize: 56,
              fontVariantNumeric: "tabular-nums",
              color: revealed ? PR_TEXT : NEUTRAL_TEXT,
              minWidth: "1.6em",
              textAlign: "center",
            }}
          >
            {displayValue === null ? "--" : displayValue}
          </span>
        </div>
      </FloatCard>
    </div>
  );
};
