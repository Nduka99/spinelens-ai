/**
 * Vision - the 3D "true experience" (Step 8): real building footprints extruded,
 * the proposed pavilion and a before/after improved crossing, the amber spine and
 * labels, under a cinematic tilted camera. Full-bleed.
 */
import { VisionMap } from "./VisionMap";
import type { LayerReference } from "../types/content";

type VisionProps = {
  layers: LayerReference[];
};

export function Vision({ layers }: VisionProps) {
  return (
    <section className="vision" aria-label="The vision in 3D">
      <h2 className="sr-only">The Vision in 3D</h2>
      <VisionMap layers={layers} />
    </section>
  );
}
