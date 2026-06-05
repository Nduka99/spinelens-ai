import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { palette } from "../theme/tokens";

type Row = { route: string; before: number; after: number; delta: number };

/**
 * Horizontal before→after bars for route legibility (0-100), driven by the real
 * wayfinder before/after model. The SVG is decorative for assistive tech; an
 * sr-only table carries the same numbers.
 */
export function RliBeforeAfter({ data }: { data: Row[] }) {
  if (data.length === 0) return null;
  const height = Math.max(150, data.length * 36 + 44);

  return (
    <figure className="rli-chart">
      <figcaption className="rli-chart__cap">How easy routes are to follow, before → after wayfinders (0–100)</figcaption>

      <div className="rli-chart__plot" aria-hidden="true">
        <ResponsiveContainer width="100%" height={height}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 4, right: 14, bottom: 0, left: 6 }}
            barGap={2}
            barCategoryGap={12}
          >
            <CartesianGrid horizontal={false} stroke="rgba(248,250,252,0.08)" />
            <XAxis
              type="number"
              domain={[0, 100]}
              tick={{ fill: palette.muted, fontSize: 11 }}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              type="category"
              dataKey="route"
              width={104}
              tick={{ fill: "#dbe4ef", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              cursor={{ fill: "rgba(255,255,255,0.04)" }}
              contentStyle={{
                background: "#0d1321",
                border: "1px solid rgba(248,250,252,0.14)",
                borderRadius: 10,
                fontSize: 12,
              }}
              labelStyle={{ color: "#f8fafc" }}
            />
            <Legend wrapperStyle={{ fontSize: 11, color: "#dbe4ef" }} />
            <Bar dataKey="before" name="Before" fill={palette.muted} radius={[0, 3, 3, 0]} />
            <Bar dataKey="after" name="After" fill={palette.amber} radius={[0, 3, 3, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Screen-reader data table. Wrapped in an sr-only div (not on the table
          itself) because a <table> resists width:1px and would otherwise overflow. */}
      <div className="sr-only">
        <table>
          <caption>How easy routes are to follow before and after wayfinders (0–100)</caption>
          <thead>
            <tr>
              <th>Route</th>
              <th>Before</th>
              <th>After</th>
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr key={row.route}>
                <td>{row.route}</td>
                <td>{row.before}</td>
                <td>{row.after}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </figure>
  );
}
