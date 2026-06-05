import type { FeatureCollection, Geometry } from "geojson";

export type Confidence = "verified" | "modelled" | "estimate";

export type ConfidenceLabels = Record<Confidence, string>;

export type Stat = {
  label: string;
  value: number | string;
  format?: "gbp" | "km" | "m" | "percent" | "compact";
};

/** Camera for the cinematic fly-through: [lng, lat, zoom, pitch, bearing]. */
export type Focus = [number, number, number, number, number];

export type Chapter = {
  id: string;
  title: string;
  kicker: string;
  body: string;
  confidence: Confidence;
  stats: Stat[];
  map: {
    layers: string[];
    focus?: Focus;
  };
};

export type LayerReference = {
  id: string;
  file: string;
  kind: "geojson";
};

export type SpineContent = {
  schemaVersion: string;
  project: {
    title: string;
    product: string;
    tagline: string;
    phase: string;
    envelope: string;
  };
  chapters: Chapter[];
  metrics: {
    legibility: Array<{
      route: string;
      score: number;
      walkTimeMin: number;
      directness: number;
    }>;
    budget: {
      envelope: number;
      centralNet: number;
      headroomCentral: number;
      highEstimateFits: boolean;
    };
    wayfinders: {
      count: number;
      tiers: Record<string, number>;
      model: string;
    };
    crossing: {
      vehiclesPerDay: number;
      cyclesPerDay: number;
      nearbyCollisions: number;
      seriousOrFatal: number;
    };
  };
  layers: LayerReference[];
  confidenceLabels: ConfidenceLabels;
  disclaimer: string;
};

export type GeoFeatureCollection = FeatureCollection<Geometry, Record<string, unknown>>;
