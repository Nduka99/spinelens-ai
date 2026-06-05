/**
 * Explore — free interactive map view.
 * Step 0: placeholder listing the available layers. Step 7 adds layer/focus
 * dropdowns and clickable plain-language popups on the real map.
 */
import type { LayerReference } from "../types/content";

type ExploreProps = {
  layers: LayerReference[];
  tagline: string;
};

export function Explore({ layers, tagline }: ExploreProps) {
  return (
    <section className="view-panel" aria-label="Explore the evidence">
      <h2 className="view-panel__title">Explore</h2>
      <p className="view-panel__lead">{tagline}</p>
      <ul className="view-panel__chips">
        {layers.map((layer) => (
          <li key={layer.id}>{layer.id.replace(/_/g, " ")}</li>
        ))}
      </ul>
      <p className="view-panel__note">Interactive layers and map popups arrive in a later step.</p>
    </section>
  );
}
