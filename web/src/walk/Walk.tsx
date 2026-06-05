/**
 * Walk - the guided journey ("Walk the Spine").
 *
 * Step 3: a scrollytelling experience. The map is pinned full-height behind, and the
 * scene cards scroll over it; as each scene reaches the trigger line, it becomes the
 * active chapter and the camera flies to it (Step 2 mechanism).
 */
import { Suspense, lazy, useMemo, useRef } from "react";
import { type Variants, motion, useScroll } from "framer-motion";

import { MapStage } from "../map/MapStage";
import { ConfidenceChip } from "../components/ConfidenceChip";
import { StatPill } from "../components/StatPill";
import { DiegeticWayfinder } from "../components/DiegeticWayfinder";

// Recharts is heavy and only appears in one scene, so load it on demand to keep
// the Walk's first paint light.
const RliBeforeAfter = lazy(() =>
  import("../components/RliBeforeAfter").then((m) => ({ default: m.RliBeforeAfter })),
);
import { useScrollama } from "../lib/useScrollama";
import type { Chapter, ConfidenceLabels, LayerReference, SpineContent } from "../types/content";

const EASE: [number, number, number, number] = [0.22, 0.61, 0.36, 1];

// Card enters as one block, then staggers its children in.
const cardVariants: Variants = {
  hidden: { opacity: 0, y: 26 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: EASE, when: "beforeChildren", staggerChildren: 0.07, delayChildren: 0.05 },
  },
};
const itemVariants: Variants = {
  hidden: { opacity: 0, y: 10 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: EASE } },
};

type WalkProps = {
  chapters: Chapter[];
  confidenceLabels: ConfidenceLabels;
  layers: LayerReference[];
  metrics: SpineContent["metrics"];
  activeId: string;
  onActivate: (id: string) => void;
};

/** Median on-foot time across the studied approaches - a real, grounded figure. */
function medianWalkMinutes(metrics: SpineContent["metrics"]): number {
  const times = metrics.legibility
    .map((route) => route.walkTimeMin)
    .filter((value) => Number.isFinite(value))
    .sort((a, b) => a - b);
  if (times.length === 0) return 10;
  const mid = Math.floor(times.length / 2);
  const median = times.length % 2 ? times[mid] : (times[mid - 1] + times[mid]) / 2;
  return Math.round(median);
}

export function Walk({ chapters, confidenceLabels, layers, metrics, activeId, onActivate }: WalkProps) {
  const scenesRef = useRef<HTMLDivElement>(null);
  useScrollama(scenesRef, onActivate);

  const active = chapters.find((chapter) => chapter.id === activeId) ?? chapters[0];
  const walkMinutes = useMemo(() => medianWalkMinutes(metrics), [metrics]);
  const { scrollYProgress } = useScroll();

  return (
    <section className="walk" aria-label="The Innovation Spine journey">
      <motion.div className="walk__progress" style={{ scaleX: scrollYProgress }} aria-hidden="true" />
      <div className="walk__map">
        <MapStage layers={layers} focus={active?.map.focus} activeLayerIds={active?.map.layers} />
        <DiegeticWayfinder chapters={chapters} activeId={activeId} walkMinutes={walkMinutes} />
      </div>

      <div className="walk__scenes" ref={scenesRef}>
        {chapters.map((chapter, index) => {
          const isActive = chapter.id === activeId;
          return (
            <section
              key={chapter.id}
              id={`scene-${chapter.id}`}
              data-scene-id={chapter.id}
              className={isActive ? "scene is-active" : "scene"}
              aria-current={isActive ? "step" : undefined}
            >
              <motion.article
                className="scene__card"
                variants={cardVariants}
                initial="hidden"
                whileInView="show"
                viewport={{ once: true, amount: 0.4 }}
              >
                <motion.header className="scene__header" variants={itemVariants}>
                  <p className="scene__kicker">
                    <span className="scene__index">{String(index + 1).padStart(2, "0")}</span>
                    {chapter.kicker}
                  </p>
                  <ConfidenceChip value={chapter.confidence} labels={confidenceLabels} />
                </motion.header>
                <motion.h2 className="scene__title" variants={itemVariants}>
                  {chapter.title}
                </motion.h2>
                <motion.p className="scene__body" variants={itemVariants}>
                  {chapter.body}
                </motion.p>
                {chapter.id === "wayfinding" && metrics.legibilityBeforeAfter && (
                  <motion.div className="scene__chart" variants={itemVariants}>
                    <Suspense fallback={null}>
                      <RliBeforeAfter data={metrics.legibilityBeforeAfter} />
                    </Suspense>
                  </motion.div>
                )}
                {chapter.stats.length > 0 && (
                  <motion.div className="scene__stats" variants={itemVariants}>
                    {chapter.stats.map((stat) => (
                      <StatPill key={`${chapter.id}-${stat.label}`} stat={stat} />
                    ))}
                  </motion.div>
                )}
              </motion.article>
            </section>
          );
        })}
      </div>
    </section>
  );
}
