/**
 * Walk — the guided journey ("Walk the Spine").
 *
 * Step 3: a scrollytelling experience. The map is pinned full-height behind, and the
 * scene cards scroll over it; as each scene reaches the trigger line, it becomes the
 * active chapter and the camera flies to it (Step 2 mechanism).
 */
import { useMemo, useRef } from "react";

import { MapStage } from "../map/MapStage";
import { ConfidenceChip } from "../components/ConfidenceChip";
import { StatPill } from "../components/StatPill";
import { DiegeticWayfinder } from "../components/DiegeticWayfinder";
import { useScrollama } from "../lib/useScrollama";
import type { Chapter, ConfidenceLabels, LayerReference, SpineContent } from "../types/content";

type WalkProps = {
  chapters: Chapter[];
  confidenceLabels: ConfidenceLabels;
  layers: LayerReference[];
  metrics: SpineContent["metrics"];
  activeId: string;
  onActivate: (id: string) => void;
};

/** Median on-foot time across the studied approaches — a real, grounded figure. */
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

  return (
    <main className="walk" aria-label="The Innovation Spine journey">
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
              <article className="scene__card">
                <header className="scene__header">
                  <p className="scene__kicker">
                    <span className="scene__index">{String(index + 1).padStart(2, "0")}</span>
                    {chapter.kicker}
                  </p>
                  <ConfidenceChip value={chapter.confidence} labels={confidenceLabels} />
                </header>
                <h2 className="scene__title">{chapter.title}</h2>
                <p className="scene__body">{chapter.body}</p>
                {chapter.stats.length > 0 && (
                  <div className="scene__stats">
                    {chapter.stats.map((stat) => (
                      <StatPill key={`${chapter.id}-${stat.label}`} stat={stat} />
                    ))}
                  </div>
                )}
              </article>
            </section>
          );
        })}
      </div>
    </main>
  );
}
