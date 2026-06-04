"""Tests for wayfinder placement optimisation."""

from __future__ import annotations

from spinelens.models import wayfinding as wf


def _setup():
    # demands a..e, weight 1 each
    weights = {d: 1.0 for d in "abcde"}
    covers = {
        "X": {"a", "b", "c"},   # best single (3)
        "Y": {"c", "d"},        # overlaps X on c
        "Z": {"d", "e"},        # complements X with d, e
        "W": {"a"},             # dominated
    }
    return weights, covers


def test_greedy_picks_max_then_complement() -> None:
    weights, covers = _setup()
    picks = wf.greedy_max_coverage(["X", "Y", "Z", "W"], covers, weights, k=2)
    assert picks[0]["node"] == "X"
    assert picks[0]["marginal_gain"] == 3.0
    # second pick should be Z (adds d,e = 2) over Y (adds only d = 1)
    assert picks[1]["node"] == "Z"
    assert picks[1]["marginal_gain"] == 2.0
    assert picks[1]["cumulative_gain"] == 5.0


def test_greedy_stops_when_no_gain() -> None:
    weights = {"a": 1.0}
    covers = {"X": {"a"}, "Y": {"a"}}
    picks = wf.greedy_max_coverage(["X", "Y"], covers, weights, k=5)
    assert len(picks) == 1  # second candidate adds nothing


def test_spacing_constraint_blocks_close_sites() -> None:
    weights, covers = _setup()
    # forbid choosing Z once X is chosen
    too_close = lambda a, b: {a, b} == {"X", "Z"}
    picks = wf.greedy_max_coverage(["X", "Y", "Z", "W"], covers, weights, k=2, too_close=too_close)
    assert picks[0]["node"] == "X"
    assert picks[1]["node"] == "Y"  # Z blocked, Y is next best


def test_assign_tier() -> None:
    assert wf.assign_tier(1, "ground_graphic", is_gateway=True) == wf.TIER_HUB
    assert wf.assign_tier(4, "ground_graphic") == wf.TIER_TOTEM        # serves many routes
    assert wf.assign_tier(1, "directional_totem") == wf.TIER_TOTEM     # totem type
    assert wf.assign_tier(1, "crossing_support") == wf.TIER_TOTEM      # crossing type
    assert wf.assign_tier(1, "ground_graphic") == wf.TIER_MARKER       # single-route marker


def test_modules_for_tier() -> None:
    enabled = {"directory_find_by_need", "interactive_map", "whats_on",
               "accessibility_language", "qr_handoff"}
    assert wf.modules_for_tier(wf.TIER_MARKER, enabled) == ["qr_handoff"]
    hub = wf.modules_for_tier(wf.TIER_HUB, enabled)
    assert "directory_find_by_need" in hub and "interactive_map" in hub
    # a disabled module never appears even if the tier could carry it
    assert "whats_on" not in wf.modules_for_tier(wf.TIER_TOTEM, {"interactive_map"})


def test_serves_non_hub_and_content_role() -> None:
    assert wf.serves_non_hub_approach(["nechells_dartmouth"]) is True
    assert wf.serves_non_hub_approach(["colmore", "new_street"]) is False
    assert wf.content_role(wf.TIER_HUB, ["colmore"]) == "hub"
    assert wf.content_role(wf.TIER_MARKER, ["nechells_dartmouth"]) == "dwell_no_pavilion"
    assert wf.content_role(wf.TIER_TOTEM, ["colmore"]) == "guide_totem"
    assert wf.content_role(wf.TIER_MARKER, ["colmore"]) == "light_marker"


def test_effective_modules_boosts_nechells_and_adds_teaser() -> None:
    enabled = {"directory_find_by_need", "interactive_map", "whats_on",
               "accessibility_language", "qr_handoff"}
    # city-core marker stays light: just qr + universal teaser
    core = wf.effective_modules(wf.TIER_MARKER, enabled, ["colmore"])
    assert set(core) == {"qr_handoff", wf.GATEWAY_TEASER}
    # nechells marker is boosted with hub-lite modules
    nech = wf.effective_modules(wf.TIER_MARKER, enabled, ["nechells_dartmouth"])
    assert "interactive_map" in nech and "directory_find_by_need" in nech and "whats_on" in nech
    assert wf.GATEWAY_TEASER in nech


def test_sponsorship_slot() -> None:
    hub = wf.sponsorship_slot(wf.TIER_HUB)
    assert hub["enabled"] is True and hub["model"] == "civic_partner"
    assert "never_blocks_wayfinding" in hub["guardrails"]
    marker = wf.sponsorship_slot(wf.TIER_MARKER)
    assert marker["enabled"] is False and marker["max_screen_share"] == 0.0


def test_bearing_to_compass() -> None:
    assert wf.bearing_to_compass(0) == "N"
    assert wf.bearing_to_compass(90) == "E"
    assert wf.bearing_to_compass(45) == "NE"
    assert wf.bearing_to_compass(180) == "S"
    assert wf.bearing_to_compass(359) == "N"  # wraps


def test_walk_time_minutes() -> None:
    assert wf.walk_time_minutes(0) == 0.0
    assert wf.walk_time_minutes(-5) == 0.0
    # 79.8 m at 1.33 m/s ~ 1.0 min
    assert wf.walk_time_minutes(79.8) == 1.0


def test_coverage_curve_is_monotonic() -> None:
    weights, covers = _setup()
    curve = wf.coverage_curve(["X", "Y", "Z", "W"], covers, weights, max_k=4)
    assert curve == sorted(curve)  # cumulative gain never decreases
    assert curve[-1] == 5.0        # all of a..e covered
