import { Suspense, lazy, useCallback, useEffect, useState } from "react";

import { useSpineContent } from "../content/content";
import { Intro } from "./Intro";
import { Walk } from "../walk/Walk";

// Non-default views are code-split: their JS (and Recharts for Evidence) only
// downloads when the tab is first opened, keeping first paint lighter.
const Explore = lazy(() => import("../explore/Explore").then((m) => ({ default: m.Explore })));
const Evidence = lazy(() => import("../evidence/Evidence").then((m) => ({ default: m.Evidence })));
const Vision = lazy(() => import("../vision/Vision").then((m) => ({ default: m.Vision })));
const Concepts = lazy(() => import("../concepts/Concepts").then((m) => ({ default: m.Concepts })));

const INTRO_KEY = "spinelens.introSeen";

type ViewId = "walk" | "explore" | "evidence" | "vision" | "concepts";

const VIEWS: { id: ViewId; label: string }[] = [
  { id: "walk", label: "The Walk" },
  { id: "explore", label: "Explore" },
  { id: "evidence", label: "The Evidence" },
  { id: "vision", label: "The Vision" },
  { id: "concepts", label: "Concepts" },
];

export function App() {
  const { content, error, loading } = useSpineContent();
  const [view, setView] = useState<ViewId>("walk");
  const [activeId, setActiveId] = useState<string>("");
  const [pendingScroll, setPendingScroll] = useState<string | null>(null);
  const [introSeen, setIntroSeen] = useState<boolean>(() => {
    try {
      return localStorage.getItem(INTRO_KEY) === "1";
    } catch {
      return false;
    }
  });

  const dismissIntro = useCallback(() => {
    setIntroSeen(true);
    try {
      localStorage.setItem(INTRO_KEY, "1");
    } catch {
      /* storage unavailable - fine, the intro just shows again next time */
    }
    // Return focus to the main content so keyboard users aren't dropped on <body>.
    requestAnimationFrame(() => document.getElementById("main")?.focus());
  }, []);

  // Dropdown selection: set the active chapter and scroll its scene into view
  // (scroll then keeps it active via Scrollama).
  const jumpToChapter = useCallback((id: string) => {
    setActiveId(id);
    const target = document.getElementById(`scene-${id}`);
    if (target) {
      const reduce = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
      target.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    }
  }, []);

  // "The Ask" works from any view: switch to the Walk first, then scroll to it.
  const goToAsk = useCallback(() => {
    if (view === "walk") jumpToChapter("ask");
    else {
      setView("walk");
      setPendingScroll("ask");
    }
  }, [view, jumpToChapter]);

  useEffect(() => {
    if (pendingScroll && view === "walk") {
      jumpToChapter(pendingScroll);
      setPendingScroll(null);
    }
  }, [pendingScroll, view, jumpToChapter]);

  if (loading) {
    return (
      <main className="app-state" aria-busy="true">
        <span>Preparing the route story…</span>
      </main>
    );
  }

  if (error || !content) {
    return (
      <main className="app-state app-state--error" role="alert">
        <strong>The story could not be loaded.</strong>
        <span>{error?.message ?? "Missing public content bundle."}</span>
      </main>
    );
  }

  const activeChapterId = content.chapters.some((c) => c.id === activeId)
    ? activeId
    : content.chapters[0].id;

  // "Phase 1 - Make It Visible" -> "Phase 1" for the compact subject line.
  const phaseShort = content.project.phase.split(/\s*[-–·]\s*/)[0].trim();

  return (
    <div className="app">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="topbar">
        <div className="topbar__brand">
          <span className="topbar__product">{content.project.product}</span>
          <h1 className="topbar__title">
            {content.project.title} · {phaseShort}
          </h1>
        </div>

        <nav className="topbar__nav" aria-label="Views">
          {VIEWS.map((item) => (
            <button
              key={item.id}
              type="button"
              aria-current={view === item.id ? "page" : undefined}
              className={view === item.id ? "is-active" : ""}
              onClick={() => setView(item.id)}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="topbar__end">
          {view === "walk" && (
            <label className="topbar__jump">
              <span className="sr-only">Jump to chapter</span>
              <select value={activeChapterId} onChange={(event) => jumpToChapter(event.target.value)}>
                {content.chapters.map((chapter) => (
                  <option key={chapter.id} value={chapter.id}>
                    {chapter.title}
                  </option>
                ))}
              </select>
            </label>
          )}
          <button type="button" className="topbar__cta" onClick={goToAsk}>
            The Ask
          </button>
        </div>
      </header>

      <main id="main" className="app__body" tabIndex={-1}>
        {view === "walk" && (
          <Walk
            chapters={content.chapters}
            confidenceLabels={content.confidenceLabels}
            layers={content.layers}
            metrics={content.metrics}
            activeId={activeChapterId}
            onActivate={setActiveId}
          />
        )}
        <Suspense fallback={<div className="view-loading" role="status">Loading…</div>}>
          {view === "explore" && <Explore layers={content.layers} tagline={content.project.tagline} />}
          {view === "evidence" && <Evidence metrics={content.metrics} />}
          {view === "vision" && <Vision layers={content.layers} />}
          {view === "concepts" && <Concepts />}
        </Suspense>
      </main>

      <footer className="app__footer">
        <p>{content.disclaimer}</p>
      </footer>

      {!introSeen && (
        <Intro
          product={content.project.product}
          title={content.project.title}
          phase={content.project.phase}
          tagline={content.project.tagline}
          onStart={dismissIntro}
        />
      )}
    </div>
  );
}
