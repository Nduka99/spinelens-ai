import { useRef } from "react";

import type { Stat } from "../types/content";
import { useCountUp } from "../lib/useCountUp";

type StatPillProps = {
  stat: Stat;
};

/** Decimal places to preserve while animating (so 0.28 km counts up cleanly). */
function decimalsOf(value: number): number {
  if (Number.isInteger(value)) return 0;
  const text = String(value);
  const dot = text.indexOf(".");
  return dot < 0 ? 0 : Math.min(2, text.length - dot - 1);
}

function formatNumber(value: number, format: Stat["format"], decimals: number): string {
  if (format === "gbp") return `£${Math.round(value).toLocaleString("en-GB")}`;
  if (format === "percent") return `${Math.round(value)}%`;
  if (format === "km") return `${value.toFixed(decimals)} km`;
  if (format === "m") return `${value.toFixed(decimals)} m`;
  // compact / default: whole-number with thousands separators
  return Math.round(value).toLocaleString("en-GB");
}

export function StatPill({ stat }: StatPillProps) {
  const ref = useRef<HTMLDivElement>(null);
  const isNumber = typeof stat.value === "number";
  const target = isNumber ? (stat.value as number) : 0;
  const decimals = isNumber ? decimalsOf(target) : 0;
  const current = useCountUp(target, ref, { enabled: isNumber });

  const display = isNumber ? formatNumber(current, stat.format, decimals) : (stat.value as string);

  return (
    <div className="stat-pill" ref={ref}>
      <strong>{display}</strong>
      <span>{stat.label}</span>
    </div>
  );
}
