// Shared geometry helpers for flight-route-map style animations (see
// 11-航線地圖動畫規則.md). Import these rather than re-deriving them per
// project — the arc-length table is what fixes the "traveling light drifts
// off the line's tip" bug documented there.

export type Point = { x: number; y: number };

export function arcPath(from: Point, to: Point, bow: number = 0.28) {
  // Quadratic bezier bowing outward (away from a straight line), the
  // standard "flight path" arc convention.
  const midX = (from.x + to.x) / 2;
  const midY = (from.y + to.y) / 2;
  const dx = to.x - from.x;
  const dy = to.y - from.y;
  const ctrlX = midX + dy * bow;
  const ctrlY = midY - Math.abs(dx) * bow * 0.5;
  return { d: `M ${from.x} ${from.y} Q ${ctrlX} ${ctrlY} ${to.x} ${to.y}`, ctrl: { x: ctrlX, y: ctrlY } };
}

// point on a quadratic bezier at parameter t (0..1). NOT arc-length
// proportional on a curved bezier — do not use directly to place anything
// that has to track a strokeDashoffset reveal. Use pointAtArcFraction.
export function pointOnQuadratic(from: Point, ctrl: Point, to: Point, t: number): Point {
  const mt = 1 - t;
  const x = mt * mt * from.x + 2 * mt * t * ctrl.x + t * t * to.x;
  const y = mt * mt * from.y + 2 * mt * t * ctrl.y + t * t * to.y;
  return { x, y };
}

export type ArcLengthTable = { t: number; len: number }[];

// Precompute once per curve (control points are static) — do not rebuild
// per frame.
export function buildArcLengthTable(from: Point, ctrl: Point, to: Point, samples: number = 120): ArcLengthTable {
  const table: ArcLengthTable = [{ t: 0, len: 0 }];
  let prev = pointOnQuadratic(from, ctrl, to, 0);
  let cum = 0;
  for (let i = 1; i <= samples; i++) {
    const t = i / samples;
    const p = pointOnQuadratic(from, ctrl, to, t);
    cum += Math.hypot(p.x - prev.x, p.y - prev.y);
    table.push({ t, len: cum });
    prev = p;
  }
  return table;
}

// The point at a given FRACTION OF ARC LENGTH along the curve — this is
// what matches where strokeDashoffset has revealed the line up to. Feed it
// the same `progress` value (post-easing) you use for strokeDashoffset.
export function pointAtArcFraction(table: ArcLengthTable, from: Point, ctrl: Point, to: Point, fraction: number): Point {
  const targetLen = fraction * table[table.length - 1].len;
  for (let i = 1; i < table.length; i++) {
    if (table[i].len >= targetLen) {
      const a = table[i - 1];
      const b = table[i];
      const segFrac = (targetLen - a.len) / (b.len - a.len || 1);
      const t = a.t + (b.t - a.t) * segFrac;
      return pointOnQuadratic(from, ctrl, to, t);
    }
  }
  return pointOnQuadratic(from, ctrl, to, 1);
}
