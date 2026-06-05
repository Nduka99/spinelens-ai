import "@testing-library/jest-dom/vitest";

// jsdom lacks several browser APIs that Framer Motion and Recharts rely on.
// Provide minimal, guarded polyfills so component tests don't crash.
if (typeof window !== "undefined") {
  if (typeof window.matchMedia !== "function") {
    window.matchMedia = (query: string): MediaQueryList =>
      ({
        matches: false,
        media: query,
        onchange: null,
        addEventListener: () => {},
        removeEventListener: () => {},
        addListener: () => {},
        removeListener: () => {},
        dispatchEvent: () => false,
      }) as MediaQueryList;
  }

  if (typeof window.IntersectionObserver !== "function") {
    class MockIntersectionObserver implements IntersectionObserver {
      readonly root: Element | null = null;
      readonly rootMargin: string = "";
      readonly thresholds: ReadonlyArray<number> = [];
      observe(): void {}
      unobserve(): void {}
      disconnect(): void {}
      takeRecords(): IntersectionObserverEntry[] {
        return [];
      }
    }
    window.IntersectionObserver = MockIntersectionObserver;
    globalThis.IntersectionObserver = MockIntersectionObserver;
  }

  if (typeof window.ResizeObserver !== "function") {
    class MockResizeObserver implements ResizeObserver {
      observe(): void {}
      unobserve(): void {}
      disconnect(): void {}
    }
    window.ResizeObserver = MockResizeObserver;
    globalThis.ResizeObserver = MockResizeObserver;
  }
}
