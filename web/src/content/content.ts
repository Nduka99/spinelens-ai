import { useEffect, useState } from "react";

import type { SpineContent } from "../types/content";

const CONTENT_URL = "/content/spine.json";

export function isValidContent(content: SpineContent): boolean {
  return Boolean(
    content.project.title &&
      content.chapters.length >= 1 &&
      content.layers.length >= 1 &&
      content.confidenceLabels.verified,
  );
}

export function useSpineContent() {
  const [content, setContent] = useState<SpineContent | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadContent() {
      setLoading(true);
      const response = await fetch(CONTENT_URL);
      if (!response.ok) throw new Error(`Failed to load ${CONTENT_URL}`);
      const nextContent = (await response.json()) as SpineContent;
      if (!isValidContent(nextContent)) throw new Error("Public content contract is incomplete");
      if (!cancelled) {
        setContent(nextContent);
        setError(null);
      }
    }

    loadContent()
      .catch((nextError: unknown) => {
        if (!cancelled) setError(nextError instanceof Error ? nextError : new Error("Unknown content error"));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { content, loading, error };
}
