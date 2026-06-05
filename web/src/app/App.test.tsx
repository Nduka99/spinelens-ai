// @vitest-environment jsdom
import { fireEvent, render, screen } from "@testing-library/react";

import { App } from "./App";
import type { SpineContent } from "../types/content";
import type { ReactNode } from "react";

// MapLibre needs WebGL, which jsdom lacks - stub the map module for the shell test.
vi.mock("react-map-gl/maplibre", () => ({
  default: ({ children }: { children?: ReactNode }) => <div data-testid="map">{children}</div>,
  Source: ({ children }: { children?: ReactNode }) => <>{children}</>,
  Layer: () => null,
  NavigationControl: () => null,
  Popup: ({ children }: { children?: ReactNode }) => <div>{children}</div>,
}));

// Scrollama relies on IntersectionObserver - stub it for jsdom.
vi.mock("scrollama", () => {
  const instance = {
    setup: () => instance,
    onStepEnter: () => instance,
    onStepExit: () => instance,
    onStepProgress: () => instance,
    resize: () => instance,
    enable: () => instance,
    disable: () => instance,
    destroy: () => undefined,
    offsetTrigger: () => undefined,
  };
  return { default: () => instance };
});

const contentFixture: SpineContent = {
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
    legibility: [{ route: "Colmore Row", score: 68, walkTimeMin: 8.7, directness: 86 }],
    budget: { envelope: 1000000, centralNet: 692523, headroomCentral: 307477, highEstimateFits: false },
    wayfinders: { count: 7, tiers: { tier2_totem: 4, tier3_marker: 3 }, model: "tiered" },
    crossing: { vehiclesPerDay: 35141, cyclesPerDay: 43, nearbyCollisions: 20, seriousOrFatal: 5 },
  },
  layers: [{ id: "routes", file: "layers/routes.geojson", kind: "geojson" }],
  confidenceLabels: {
    verified: "Verified data",
    modelled: "Evidence-led model",
    estimate: "Early estimate",
  },
  disclaimer: "Evidence-led concept.",
};

function jsonResponse(body: unknown) {
  return new Response(JSON.stringify(body), { headers: { "Content-Type": "application/json" } });
}

beforeEach(() => {
  // Mark the first-load intro as already seen so the shell tests see the app
  // directly (a dedicated test below covers the intro itself).
  localStorage.setItem("spinelens.introSeen", "1");
  globalThis.fetch = vi.fn(async (input: RequestInfo | URL) => {
    const url = String(input);
    if (url.endsWith("/content/spine.json")) return jsonResponse(contentFixture);
    return new Response(null, { status: 404 });
  }) as typeof fetch;
});

afterEach(() => {
  vi.restoreAllMocks();
  localStorage.clear();
});

describe("App shell", () => {
  it("loads the content and renders the journey", async () => {
    render(<App />);
    expect(await screen.findByRole("heading", { name: "The Innovation Spine · Phase 1" })).toBeTruthy();
    expect(screen.getByText("SpineLens AI")).toBeTruthy();
    expect(await screen.findByRole("heading", { name: "Close, Yet Far" })).toBeTruthy();
    expect(screen.getByRole("region", { name: "Innovation Spine map" })).toBeTruthy();
    // Diegetic wayfinder renders with the destination and a journey-progress label.
    expect(screen.getByText("Birmingham Knowledge Quarter")).toBeTruthy();
    expect(screen.getByText(/You are here/i)).toBeTruthy();
  });

  it("shows the intro on first load and dismisses it on start", async () => {
    localStorage.clear();
    render(<App />);
    const dialog = await screen.findByRole("dialog");
    expect(dialog).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /start the walk/i }));
    expect(screen.queryByRole("dialog")).toBeNull();
    expect(localStorage.getItem("spinelens.introSeen")).toBe("1");
  });

  it("switches views via the nav", async () => {
    render(<App />);
    const evidenceTab = await screen.findByRole("button", { name: "The Evidence" });
    fireEvent.click(evidenceTab);
    expect(evidenceTab.getAttribute("aria-current")).toBe("page");
    // Evidence is a lazy-loaded view, so wait for its chunk to resolve.
    expect(await screen.findByRole("heading", { name: "The Evidence" })).toBeTruthy();
  });
});
