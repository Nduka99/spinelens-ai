import { type RefObject, useEffect, useState } from "react";
import { useInView, useReducedMotion } from "framer-motion";

type CountUpOptions = {
  /** Only animate when true (e.g. the stat is numeric). */
  enabled?: boolean;
  durationMs?: number;
};

/**
 * Animate a number from 0 to `target` the first time `ref` scrolls into view.
 * Honours prefers-reduced-motion (jumps straight to the target) and cleans up
 * its animation frame. Returns the current value to render each frame.
 */
export function useCountUp(
  target: number,
  ref: RefObject<Element | null>,
  options: CountUpOptions = {},
): number {
  const { enabled = true, durationMs = 1100 } = options;
  const inView = useInView(ref, { once: true, amount: 0.5 });
  const reduce = useReducedMotion();
  const [value, setValue] = useState(enabled ? 0 : target);

  useEffect(() => {
    if (!enabled || !inView) return;
    if (reduce) {
      setValue(target);
      return;
    }
    let frame = 0;
    let startTs = 0;
    const tick = (now: number) => {
      if (!startTs) startTs = now;
      const progress = Math.min(1, (now - startTs) / durationMs);
      const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      if (progress < 1) {
        setValue(target * eased);
        frame = requestAnimationFrame(tick);
      } else {
        setValue(target);
      }
    };
    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [enabled, inView, reduce, target, durationMs]);

  return value;
}
