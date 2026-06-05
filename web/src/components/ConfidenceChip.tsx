import type { Confidence, ConfidenceLabels } from "../types/content";

type ConfidenceChipProps = {
  value: Confidence;
  labels: ConfidenceLabels;
};

export function ConfidenceChip({ value, labels }: ConfidenceChipProps) {
  return <span className={`confidence-chip confidence-${value}`}>{labels[value]}</span>;
}
