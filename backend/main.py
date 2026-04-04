"""FastAPI entrypoint for the Hormuz Strait Simulator."""

import json
import logging
import os
from collections import defaultdict
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from agents import DEFAULT_MODEL, run_single_round
from config_loader import (
    load_souls, load_tags, get_tag_injection, get_market_tag_injection,
    localize_actor, localize_tag, SUPPORTED_LOCALES,
)
from models import AgentProfile, SimulationRequest

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PRESETS_PATH = Path(__file__).parent / "presets.json"
PRESETS = json.loads(PRESETS_PATH.read_text(encoding="utf-8"))

# Load souls and tags from markdown files
ACTORS = load_souls()
TAGS = load_tags()

I18N_PATH = Path(__file__).parent / "i18n.json"
I18N = json.loads(I18N_PATH.read_text(encoding="utf-8"))

FREE_TRIAL_LIMIT = int(os.getenv("FREE_TRIAL_LIMIT", "10"))
TRIAL_MODEL = os.getenv("TRIAL_MODEL", DEFAULT_MODEL)

# In-memory trial counter: {uuid: count}
trial_counter: dict[str, int] = defaultdict(int)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Hormuz Strait Simulator",
    version="0.2.0",
    description="Multi-agent geopolitical simulation sandbox",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production to your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.2.0"}


@app.get("/api/i18n")
async def get_i18n(locale: str = "en"):
    """Return UI strings for the given locale."""
    loc = locale if locale in SUPPORTED_LOCALES else "en"
    return {"locale": loc, "strings": I18N.get(loc, I18N["en"])}


@app.get("/api/presets")
async def get_presets(locale: str = "en"):
    """Return scenario config, actors, and available tags for the frontend.
    Query param `locale` accepts 'en' or 'zh'."""
    loc = locale if locale in SUPPORTED_LOCALES else "en"
    scenario = PRESETS["scenario"]
    i18n_scenario = PRESETS.get("scenario_i18n", {}).get(loc, {})

    return {
        "scenario": {
            "name": i18n_scenario.get("name", scenario["name"]),
            "description": i18n_scenario.get("description", scenario.get("description", "")),
            "briefing": i18n_scenario.get("briefing", []),
            "start_date": scenario["start_date"],
            "initial_oil_price": scenario["initial_oil_price"],
        },
        "actors": {
            actor_id: localize_actor(cfg, loc)
            for actor_id, cfg in ACTORS.items()
        },
        "tags": {
            tag_id: localize_tag(cfg, loc)
            for tag_id, cfg in TAGS.items()
        },
        "locale": loc,
        "supported_locales": list(SUPPORTED_LOCALES),
    }


@app.post("/api/simulate")
async def simulate(req: SimulationRequest):
    """Main simulation endpoint. Returns an SSE stream."""

    # --- Determine model & key ---
    if req.api_key:
        model = req.model or DEFAULT_MODEL
        api_key = req.api_key
    else:
        if trial_counter[req.client_uuid] >= FREE_TRIAL_LIMIT:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "TRIAL_LIMIT_REACHED",
                    "message": f"Free trial limit ({FREE_TRIAL_LIMIT} runs) reached. Please provide your own API key to continue.",
                },
            )
        model = TRIAL_MODEL
        api_key = None
        trial_counter[req.client_uuid] += 1

    # --- Merge user profiles with soul defaults ---
    profiles: dict[str, AgentProfile] = {}
    for actor_id, actor_cfg in ACTORS.items():
        if actor_id in req.profiles:
            profiles[actor_id] = req.profiles[actor_id]
        else:
            profiles[actor_id] = AgentProfile(**actor_cfg["default_profile"])

    market_config = {
        **PRESETS["market_agent"],
        "initial_oil_price": PRESETS["scenario"]["initial_oil_price"],
    }

    # --- Build per-actor tag injections ---
    actor_tag_injections = {
        actor_id: get_tag_injection(TAGS, req.active_tags, actor_id)
        for actor_id in ACTORS
    }
    market_tag_inj = get_market_tag_injection(TAGS, req.active_tags)

    # --- Stream SSE (single round) ---
    async def event_stream():
        try:
            async for event in run_single_round(
                actors_config=ACTORS,
                market_config=market_config,
                profiles=profiles,
                chaos_factor=req.chaos_factor,
                round_num=req.round_num,
                step_unit=req.step_unit,
                model=model,
                api_key=api_key,
                background=PRESETS["scenario"].get("background", ""),
                actor_tag_injections=actor_tag_injections,
                market_tag_injection=market_tag_inj,
                previous_summaries=req.previous_summaries,
                previous_oil_price=req.previous_oil_price,
                locale=req.locale,
            ):
                yield f"data: {event.model_dump_json()}\n\n"
        except Exception as e:
            logger.exception("Simulation stream error")
            error_payload = json.dumps({"type": "error", "sender": "System", "round": -1, "data": {"message": str(e)}})
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
