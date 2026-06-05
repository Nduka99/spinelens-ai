import { useEffect, type RefObject } from "react";
import scrollama from "scrollama";

/**
 * useScrollama - fire `onEnter(sceneId)` as each `[data-scene-id]` step scrolls past
 * the trigger line. Drives the cinematic map (scroll → active chapter → camera flyTo).
 * Cleans up on unmount; re-binds on resize.
 */
export function useScrollama(
  containerRef: RefObject<HTMLElement | null>,
  onEnter: (sceneId: string) => void,
) {
  useEffect(() => {
    const root = containerRef.current;
    if (!root) return;
    const steps = Array.from(root.querySelectorAll<HTMLElement>("[data-scene-id]"));
    if (steps.length === 0) return;

    const scroller = scrollama();
    scroller
      .setup({ step: steps, offset: 0.6 })
      .onStepEnter(({ element }) => {
        const id = element.dataset.sceneId;
        if (id) onEnter(id);
      });

    const handleResize = () => scroller.resize();
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      scroller.destroy();
    };
  }, [containerRef, onEnter]);
}
