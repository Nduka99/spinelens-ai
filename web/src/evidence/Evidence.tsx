/**
 * Evidence — the dashboard view (charts + plain-language "how we know").
 * Step 0: placeholder surfacing the headline metrics from the contract.
 * Step 8 turns these into animated charts.
 */
import type { SpineContent } from "../types/content";

type EvidenceProps = {
  metrics: SpineContent["metrics"];
};

export function Evidence({ metrics }: EvidenceProps) {
  return (
    <section className="view-panel" aria-label="The evidence dashboard">
      <h2 className="view-panel__title">The Evidence</h2>
      <p className="view-panel__lead">
        Built on official public datasets and independently checked. Charts arrive in a later step.
      </p>
      <dl className="view-panel__metrics">
        <div>
          <dt>Clearest approach</dt>
          <dd>{metrics.legibility[0]?.route ?? "—"}</dd>
        </div>
        <div>
          <dt>Central estimate (net)</dt>
          <dd>£{metrics.budget.centralNet.toLocaleString("en-GB")}</dd>
        </div>
        <div>
          <dt>Wayfinders</dt>
          <dd>{metrics.wayfinders.count}</dd>
        </div>
        <div>
          <dt>Vehicles a day at the barrier</dt>
          <dd>{metrics.crossing.vehiclesPerDay.toLocaleString("en-GB")}</dd>
        </div>
      </dl>
    </section>
  );
}
