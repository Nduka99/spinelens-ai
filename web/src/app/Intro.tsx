/**
 * Intro - a light first-load overlay that answers "what is this?" in a few
 * seconds, then gets out of the way. Names the product (SpineLens AI), the
 * subject (the Innovation Spine, Phase 1) and a one-line value statement, with a
 * single clear way in. Dismissal is remembered so it doesn't nag on return.
 */
import { useEffect, useRef } from "react";

type IntroProps = {
  product: string;
  title: string;
  phase: string;
  tagline: string;
  onStart: () => void;
};

export function Intro({ product, title, phase, tagline, onStart }: IntroProps) {
  const ctaRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    ctaRef.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onStart();
        return;
      }
      // Trap focus within the modal (it is aria-modal).
      if (event.key === "Tab" && panelRef.current) {
        const f = panelRef.current.querySelectorAll<HTMLElement>("button");
        if (f.length === 0) return;
        const first = f[0];
        const last = f[f.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first.focus();
        }
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onStart]);

  return (
    <div className="intro" role="dialog" aria-modal="true" aria-labelledby="intro-title" ref={panelRef}>
      <div className="intro__panel">
        <p className="intro__product">{product}</p>
        <h1 id="intro-title" className="intro__title">
          {title}
        </h1>
        <p className="intro__phase">{phase}</p>
        <p className="intro__lead">{tagline}</p>
        <p className="intro__sub">
          A guided walk-through of Phase 1: clear wayfinders, a bright amber route, a safer crossing
          and a welcoming gateway pavilion, with the evidence behind each idea.
        </p>
        <div className="intro__actions">
          <button ref={ctaRef} type="button" className="intro__cta" onClick={onStart}>
            Start the walk →
          </button>
          <button type="button" className="intro__skip" onClick={onStart}>
            Skip intro
          </button>
        </div>
      </div>
    </div>
  );
}
