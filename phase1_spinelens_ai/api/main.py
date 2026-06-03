"""FastAPI entry point for Phase 1, kept intentionally thin for now."""

from __future__ import annotations

from fastapi import FastAPI

from spinelens.config import PHASE1_TOTAL_BUDGET_GBP, budget_is_balanced


app = FastAPI(title="SpineLens AI Phase 1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "phase": "phase1_spinelens_ai"}


@app.get("/phase1/budget")
def phase1_budget() -> dict[str, int | bool]:
    return {
        "total_budget_gbp": PHASE1_TOTAL_BUDGET_GBP,
        "budget_is_balanced": budget_is_balanced(),
    }
