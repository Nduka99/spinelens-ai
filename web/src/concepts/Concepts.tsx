/**
 * Concepts - a gallery of the Phase 1 concept artwork.
 *
 * A responsive grid of fast-loading cards (WebP thumbnails, lazy-loaded). Tap any
 * card to open a full-size lightbox with the larger image, caption, and keyboard
 * navigation (arrow keys to move, Escape to close). Content comes from the
 * sanitised public manifest built by build_concepts.py.
 */
import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";

type Concept = {
  id: string;
  title: string;
  caption: string;
  alt: string;
  src: string;
  thumb: string;
  width: number;
  height: number;
};

export function Concepts() {
  const [items, setItems] = useState<Concept[]>([]);
  const [open, setOpen] = useState<number | null>(null);

  useEffect(() => {
    fetch("/concepts.json")
      .then((r) => r.json())
      .then((d: { concepts?: Concept[] }) => setItems(d.concepts ?? []))
      .catch(() => {});
  }, []);

  return (
    <section className="concepts" aria-label="Concept artwork">
      <header className="concepts__head">
        <h2 className="concepts__title">Concepts</h2>
        <p className="concepts__lead">
          Artist's impressions of how Phase 1 could look and feel. Select any image to see it larger.
        </p>
      </header>

      <div className="concepts__grid">
        {items.map((c, i) => (
          <button key={c.id} type="button" className="concept-card" onClick={() => setOpen(i)} aria-label={`View ${c.title} larger`}>
            <span className="concept-card__media">
              <img
                src={`/${c.thumb}`}
                alt={c.alt}
                loading="lazy"
                decoding="async"
                width={c.width}
                height={c.height}
              />
              <span className="concept-card__zoom" aria-hidden="true">⤢</span>
            </span>
            <span className="concept-card__body">
              <strong className="concept-card__title">{c.title}</strong>
              <span className="concept-card__caption">{c.caption}</span>
            </span>
          </button>
        ))}
      </div>

      <p className="concepts__note">Concept artist's impressions. Indicative only.</p>

      <AnimatePresence>
        {open !== null && items[open] && (
          <Lightbox items={items} index={open} onClose={() => setOpen(null)} onIndex={setOpen} />
        )}
      </AnimatePresence>
    </section>
  );
}

function Lightbox({
  items,
  index,
  onClose,
  onIndex,
}: {
  items: Concept[];
  index: number;
  onClose: () => void;
  onIndex: (i: number) => void;
}) {
  const item = items[index];
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
      else if (e.key === "ArrowLeft") onIndex((index - 1 + items.length) % items.length);
      else if (e.key === "ArrowRight") onIndex((index + 1) % items.length);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [index, items.length, onClose, onIndex]);

  return (
    <motion.div
      className="lightbox"
      role="dialog"
      aria-modal="true"
      aria-label={item.title}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.2 }}
      onClick={onClose}
    >
      <button ref={closeRef} type="button" className="lightbox__close" onClick={onClose} aria-label="Close">
        ×
      </button>
      <button
        type="button"
        className="lightbox__nav lightbox__nav--prev"
        onClick={(e) => {
          e.stopPropagation();
          onIndex((index - 1 + items.length) % items.length);
        }}
        aria-label="Previous image"
      >
        ‹
      </button>

      <motion.figure
        className="lightbox__figure"
        onClick={(e) => e.stopPropagation()}
        initial={{ scale: 0.97, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.98, opacity: 0 }}
        transition={{ duration: 0.22, ease: [0.22, 0.61, 0.36, 1] }}
      >
        <img className="lightbox__img" src={`/${item.src}`} alt={item.alt} />
        <figcaption className="lightbox__cap">
          <strong className="lightbox__cap-title">{item.title}</strong>
          <span className="lightbox__cap-text">{item.caption}</span>
          <span className="lightbox__count">
            {index + 1} / {items.length}
          </span>
        </figcaption>
      </motion.figure>

      <button
        type="button"
        className="lightbox__nav lightbox__nav--next"
        onClick={(e) => {
          e.stopPropagation();
          onIndex((index + 1) % items.length);
        }}
        aria-label="Next image"
      >
        ›
      </button>
    </motion.div>
  );
}
