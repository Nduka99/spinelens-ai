/**
 * Evidence - the dashboard (Step 8c).
 * Animated, plain-language charts of the Phase 1 evidence: route legibility, the
 * wayfinding uplift (before/after), the barrier, and the budget vs the £1m envelope.
 * Verified data vs evidence-led models are labelled; costs are early estimates.
 */
import { type ReactNode } from "react";
import { type Variants, motion } from "framer-motion";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { StatPill } from "../components/StatPill";
import { RliBeforeAfter } from "../components/RliBeforeAfter";
import { palette } from "../theme/tokens";
import type { SpineContent } from "../types/content";

const EASE: [number, number, number, number] = [0.22, 0.61, 0.36, 1];
const cardVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: EASE } },
};

function Card({ title, tag, children }: { title: string; tag: string; children: ReactNode }) {
  return (
    <motion.article
      className="ev-card"
      variants={cardVariants}
      initial="hidden"
      whileInView="show"
      viewport={{ once: true, amount: 0.25 }}
    >
      <header className="ev-card__head">
        <h3 className="ev-card__title">{title}</h3>
        <span className="ev-card__chip">{tag}</span>
      </header>
      {children}
    </motion.article>
  );
}

export function Evidence({ metrics }: { metrics: SpineContent["metrics"] }) {
  const legibility = [...metrics.legibility].sort((a, b) => b.score - a.score);
  const { budget, crossing } = metrics;
  const spentPct = Math.max(0, Math.min(100, Math.round((budget.centralNet / budget.envelope) * 100)));
  const vehiclesPerCycle = crossing.cyclesPerDay
    ? Math.round(crossing.vehiclesPerDay / crossing.cyclesPerDay)
    : 0;

  return (
    <section className="evidence" aria-label="The evidence dashboard">
      <header className="evidence__head">
        <h2 className="evidence__title">The Evidence</h2>
        <p className="evidence__lead">
          What the data shows: how easy each route is to follow, the barrier, the difference
          wayfinders make, and the budget.
        </p>
      </header>

      <div className="evidence__grid">
        <Card title="How easy routes are to follow (0–100)" tag="Our analysis">
          <div className="ev-chart">
            <ResponsiveContainer width="100%" height={legibility.length * 34 + 24}>
              <BarChart data={legibility} layout="vertical" margin={{ left: 6, right: 16, top: 4, bottom: 0 }}>
                <CartesianGrid horizontal={false} stroke="rgba(248,250,252,0.08)" />
                <XAxis type="number" domain={[0, 100]} tick={{ fill: palette.muted, fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis type="category" dataKey="route" width={106} tick={{ fill: "#dbe4ef", fontSize: 11 }} tickLine={false} axisLine={false} />
                <Tooltip cursor={{ fill: "rgba(255,255,255,0.04)" }} contentStyle={{ background: "#0d1321", border: "1px solid rgba(248,250,252,0.14)", borderRadius: 10, fontSize: 12 }} labelStyle={{ color: "#f8fafc" }} />
                <Bar dataKey="score" name="Score" fill={palette.sky} radius={[0, 3, 3, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {metrics.legibilityBeforeAfter && metrics.legibilityBeforeAfter.length > 0 && (
          <Card title="The difference wayfinders make" tag="Our analysis">
            <RliBeforeAfter data={metrics.legibilityBeforeAfter} />
          </Card>
        )}

        <Card title="The barrier" tag="Measured data">
          <div className="ev-stats">
            <StatPill stat={{ label: "vehicles a day", value: crossing.vehiclesPerDay }} />
            <StatPill stat={{ label: "cycles a day", value: crossing.cyclesPerDay }} />
            <StatPill stat={{ label: "injury collisions (2020–24)", value: crossing.nearbyCollisions }} />
            <StatPill stat={{ label: "serious or fatal", value: crossing.seriousOrFatal }} />
          </div>
          <p className="ev-card__cap">
            ≈ {vehiclesPerCycle.toLocaleString("en-GB")} vehicles for every person on a bike. That
            is how cut off the area is.
          </p>
        </Card>

        <Card title="Budget vs the £1m total" tag="Early estimate">
          <div
            className="ev-budget__bar"
            role="img"
            aria-label={`Likely cost is ${spentPct}% of the £1,000,000 budget`}
          >
            <motion.div
              className="ev-budget__spent"
              initial={{ width: 0 }}
              whileInView={{ width: `${spentPct}%` }}
              viewport={{ once: true }}
              transition={{ duration: 0.9, ease: EASE }}
            >
              <span>spend {spentPct}%</span>
            </motion.div>
            <div className="ev-budget__headroom">
              <span>spare</span>
            </div>
          </div>
          <div className="ev-stats">
            <StatPill stat={{ label: "likely cost", value: budget.centralNet, format: "gbp" }} />
            <StatPill stat={{ label: "money to spare", value: budget.headroomCentral, format: "gbp" }} />
          </div>
        </Card>
      </div>

      <p className="evidence__note">
        Some figures are measured (traffic and collisions). Others come from our analysis (how easy
        routes are to follow, and the wayfinders). Costs are early estimates and would be checked
        before anything is funded.
      </p>
    </section>
  );
}
