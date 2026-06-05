import { isValidContent } from "./content";
import type { SpineContent } from "../types/content";

const baseContent: SpineContent = {
  schemaVersion: "0.1.0",
  project: {
    title: "The Innovation Spine",
    product: "SpineLens AI",
    tagline: "Reconnecting Birmingham Knowledge Quarter to the city core.",
    phase: "Phase 1 - Make It Visible",
    envelope: "£1,000,000",
  },
  chapters: [
    {
      id: "challenge",
      title: "Close, Yet Far",
      kicker: "The problem",
      body: "The route feels unclear.",
      confidence: "modelled",
      stats: [{ label: "vehicles a day", value: 35141 }],
      map: { layers: ["routes"] },
    },
  ],
  metrics: {
    legibility: [],
    budget: {
      envelope: 1000000,
      centralNet: 692523,
      headroomCentral: 307477,
      highEstimateFits: false,
    },
    wayfinders: { count: 7, tiers: { tier2_totem: 4, tier3_marker: 3 }, model: "tiered" },
    crossing: {
      vehiclesPerDay: 35141,
      cyclesPerDay: 43,
      nearbyCollisions: 20,
      seriousOrFatal: 5,
    },
  },
  layers: [{ id: "routes", file: "layers/routes.geojson", kind: "geojson" }],
  confidenceLabels: {
    verified: "Verified data",
    modelled: "Evidence-led model",
    estimate: "Early estimate",
  },
  disclaimer: "Evidence-led concept.",
};

describe("isValidContent", () => {
  it("accepts the minimum public content contract", () => {
    expect(isValidContent(baseContent)).toBe(true);
  });

  it("rejects content without chapters", () => {
    expect(isValidContent({ ...baseContent, chapters: [] })).toBe(false);
  });
});
