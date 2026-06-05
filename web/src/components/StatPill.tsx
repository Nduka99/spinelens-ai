import type { Stat } from "../types/content";

type StatPillProps = {
  stat: Stat;
};

function formatStat(stat: Stat): string {
  if (typeof stat.value === "string") return stat.value;
  if (stat.format === "gbp") return `£${Math.round(stat.value).toLocaleString("en-GB")}`;
  if (stat.format === "km") return `${stat.value.toLocaleString("en-GB")} km`;
  if (stat.format === "m") return `${stat.value.toLocaleString("en-GB")} m`;
  if (stat.format === "percent") return `${stat.value}%`;
  return stat.value.toLocaleString("en-GB");
}

export function StatPill({ stat }: StatPillProps) {
  return (
    <div className="stat-pill">
      <strong>{formatStat(stat)}</strong>
      <span>{stat.label}</span>
    </div>
  );
}
