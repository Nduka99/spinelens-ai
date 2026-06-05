import { useCallback, useState } from "react";

import { useSpineContent } from "../content/content";
import { Walk } from "../walk/Walk";
import { Explore } from "../explore/Explore";
import { Evidence } from "../evidence/Evidence";
import { Vision } from "../vision/Vision";

type ViewId = "walk" | "explore" | "evidence" | "vision";

const VIEWS: { id: ViewId; label: string }[] = [
  { id: "walk", label: "The Walk" },
  { id: "explore", label: "Explore" },
  { id: "evidence", label: "The Evidence" },
  { id: "vision", label: "The Vision" },
];

export function App() {
  const { content, error, loading } = useSpineContent();
  const [view, setView] = useState<ViewId>("walk");
  const [activeId, setActiveId] = useState<string>("");

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

  return (
    <div className="app">
      <header className="topbar">
        <div className="topbar__brand">
          <p className="topbar__phase">{content.project.phase}</p>
          <h1 className="topbar__title">{content.project.title}</h1>
        </div>

        <nav className="topbar__nav" role="tablist" aria-label="Views">
          {VIEWS.map((item) => (
            <button
              key={item.id}
              type="button"
              role="tab"
              aria-selected={view === item.id}
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
          <a className="topbar__cta" href="#scene-ask">
            The Ask
          </a>
        </div>
      </header>

      <div className="app__body">
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
        {view === "explore" && (
          <main className="app__view">
            <Explore layers={content.layers} tagline={content.project.tagline} />
          </main>
        )}
        {view === "evidence" && (
          <main className="app__view">
            <Evidence metrics={content.metrics} />
          </main>
        )}
        {view === "vision" && (
          <main className="app__view">
            <Vision />
          </main>
        )}
      </div>

      <footer className="app__footer">
        <p>{content.disclaimer}</p>
      </footer>
    </div>
  );
}
