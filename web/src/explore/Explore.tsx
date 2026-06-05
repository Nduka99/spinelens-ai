/**
 * Explore - free interactive map view (Step 7): pan/zoom, toggle layers, click
 * features for plain-language popups. Full-bleed map with overlay controls.
 */
import { ExploreMap } from "./ExploreMap";
import type { LayerReference } from "../types/content";

type ExploreProps = {
  layers: LayerReference[];
  tagline: string;
};

export function Explore({ layers, tagline }: ExploreProps) {
  return (
    <section className="explore" aria-label="Explore the evidence">
      <h2 className="sr-only">Explore the evidence</h2>
      <ExploreMap layers={layers} />
      <p className="explore__caption">{tagline}</p>
    </section>
  );
}
