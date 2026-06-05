/**
 * DiegeticWayfinder - an in-world directional sign pinned to the map.
 *
 * Reinforces the "walk the spine" idea: as the journey progresses the sign
 * fills its track and the on-foot time to B-KQ counts down. The headline time
 * is the median walk time across the studied approaches (a real, grounded
 * figure), used here as a journey metaphor - the precise numbers live in the
 * scene cards and the Evidence view.
 */
import type { Chapter } from "../types/content";

type DiegeticWayfinderProps = {
  chapters: Chapter[];
  activeId: string;
  /** Representative on-foot minutes from the city core (median of approaches). */
  walkMinutes: number;
};

export function DiegeticWayfinder({ chapters, activeId, walkMinutes }: DiegeticWayfinderProps) {
  const total = chapters.length;
  const index = Math.max(
    0,
    chapters.findIndex((chapter) => chapter.id === activeId),
  );
  const active = chapters[index] ?? chapters[0];
  const progress = total > 1 ? index / (total - 1) : 1;
  const arrived = index >= total - 1;
  const remaining = Math.max(1, Math.round(walkMinutes * (1 - progress)));
  const eta = arrived ? "Arrived" : `≈ ${remaining} min`;

  return (
    <aside
      className="wayfinder"
      aria-label={`On the spine: step ${index + 1} of ${total}, ${arrived ? "arrived at" : `about ${remaining} minute${remaining === 1 ? "" : "s"} on foot to`} Birmingham Knowledge Quarter`}
    >
      <div className="wayfinder__sign">
        <span className="wayfinder__arrow" aria-hidden="true">
          ↑
        </span>
        <span className="wayfinder__dest">
          <span className="wayfinder__eyebrow">On foot</span>
          <strong className="wayfinder__place">Birmingham Knowledge Quarter</strong>
        </span>
        <span className="wayfinder__eta" data-arrived={arrived || undefined}>
          {eta}
        </span>
      </div>

      <ol className="wayfinder__track" aria-hidden="true">
        {chapters.map((chapter, i) => (
          <li key={chapter.id} className={i <= index ? "is-done" : ""} />
        ))}
      </ol>

      <p className="wayfinder__here">
        <span className="wayfinder__dot" aria-hidden="true" />
        You are here · {active.kicker}
      </p>
    </aside>
  );
}
