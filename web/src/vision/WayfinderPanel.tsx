/**
 * WayfinderPanel - the conceptual "digital panel" card shown for the active
 * wayfinder in the Vision step-through (Step 2).
 *
 * Light (city-core): direction + "full guide at the pavilion" + transport + QR.
 * Rich (Nechells, no pavilion): direction + find-by-need + general B-KQ
 * opportunities + transport + QR. Opportunities are conceptual/general; live
 * fields update at deployment.
 */

export type WfPanel = {
  id: string;
  side: string;
  variant: "light" | "rich";
  type?: string;
  destination: string;
  heading?: string | null;
  walkTimeMin?: number | null;
  nextMarker?: string | null;
  nearbyStops?: string;
  crossingCaution?: string;
  findByNeed: string[];
  opportunities: { place: string; items: string[] }[];
  pavilionGuide: boolean;
};

function isPlaceName(marker: string | null | undefined): marker is string {
  return !!marker && !/^W\d+$/.test(marker);
}

export function WayfinderPanel({ panel }: { panel: WfPanel }) {
  return (
    <aside className={`wf-panel wf-panel--${panel.variant}`} aria-live="polite">
      <header className="wf-panel__top">
        <span className="wf-panel__brand">B-KQ</span>
        <span className="wf-panel__id">
          {panel.id}
          {panel.type ? ` · ${panel.type}` : ""}
        </span>
      </header>

      <div className="wf-panel__glance">
        <span className="wf-panel__arrow" aria-hidden="true">
          ↑
        </span>
        <span className="wf-panel__dest">{panel.destination}</span>
        {panel.walkTimeMin != null && <span className="wf-panel__time">≈ {panel.walkTimeMin} min</span>}
      </div>

      {panel.crossingCaution && <p className="wf-panel__caution">⚠ {panel.crossingCaution}</p>}

      {panel.variant === "rich" ? (
        <>
          {panel.findByNeed.length > 0 && (
            <div className="wf-panel__needs" aria-label="Find by need">
              {panel.findByNeed.map((need) => (
                <span key={need} className="wf-panel__chip">
                  {need}
                </span>
              ))}
            </div>
          )}
          {panel.opportunities.map((opp) => (
            <div key={opp.place} className="wf-panel__opp">
              <strong className="wf-panel__opp-place">{opp.place}</strong>
              <ul className="wf-panel__opp-items">
                {opp.items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
        </>
      ) : (
        <p className="wf-panel__pavilion">
          Full guide &amp; what&apos;s on at the <strong>Ryder Street pavilion</strong>.
        </p>
      )}

      {isPlaceName(panel.nextMarker) && <p className="wf-panel__next">Continue to {panel.nextMarker}</p>}

      {panel.nearbyStops && (
        <p className="wf-panel__transport">
          Buses nearby <span className="wf-panel__tag">live</span>
          <br />
          {panel.nearbyStops}
        </p>
      )}

      <footer className="wf-panel__foot">
        <span className="wf-panel__qr" aria-hidden="true">
          <span className="wf-panel__qr-grid" />
          Scan
        </span>
        <span className="wf-panel__note">Concept content · live info shown once installed</span>
      </footer>
    </aside>
  );
}
