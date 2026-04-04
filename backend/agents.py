"""Multi-agent engine: Actor agents (countries) and Market agent."""

import json
import re
import logging
from typing import AsyncGenerator

import litellm

from models import (
    ActorOutput,
    AgentProfile,
    MarketUpdate,
    SSEEvent,
    StepUnit,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "gemini/gemini-3-flash-preview"

STEP_LABEL = {
    StepUnit.day: ("Day", "days"),
    StepUnit.week: ("Week", "weeks"),
    StepUnit.month: ("Month", "months"),
}


def _clean_json(raw: str) -> str:
    """Strip markdown code fences and attempt to fix truncated JSON."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    raw = raw.strip()
    # If JSON is truncated (unclosed string/object), try to fix it
    if raw.startswith("{") and not raw.endswith("}"):
        # Close any open string, then close the object
        if raw.count('"') % 2 == 1:
            raw += '"'
        raw += "}"
    return raw


async def _llm_call(
    messages: list[dict],
    model: str,
    api_key: str | None,
    response_format: dict | None = None,
    max_retries: int = 2,
) -> str:
    """Call LLM via LiteLLM with retry on parse failure."""
    kwargs: dict = {
        "model": model,
        "messages": messages,
        "temperature": 0.8,
        "max_tokens": 2048,
    }
    if api_key:
        kwargs["api_key"] = api_key
    if response_format:
        kwargs["response_format"] = response_format

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            resp = await litellm.acompletion(**kwargs)
            return resp.choices[0].message.content
        except Exception as e:
            last_error = e
            logger.warning("LLM call attempt %d failed: %s", attempt + 1, e)
    raise last_error  # type: ignore[misc]


def _chaos_instruction(chaos_factor: float) -> str:
    """Turn chaos_factor into a concrete behavioral instruction."""
    if chaos_factor <= 0.3:
        return (
            "=== BEHAVIORAL DIRECTIVE: LOW CHAOS ===\n"
            "The current environment favors caution and restraint. You MUST:\n"
            "- Prioritize diplomatic solutions and backchannel negotiations\n"
            "- Avoid provocative or escalatory actions unless directly attacked\n"
            "- Seek face-saving compromises and de-escalation paths\n"
            "- Make conservative, risk-averse decisions\n"
            "=== END DIRECTIVE ===\n"
        )
    elif chaos_factor <= 0.6:
        return (
            "=== BEHAVIORAL DIRECTIVE: MODERATE CHAOS ===\n"
            "The environment is tense but controllable. You should:\n"
            "- Balance assertiveness with caution\n"
            "- Take calculated risks where the payoff justifies it\n"
            "- Respond proportionally to provocations — neither ignoring nor overreacting\n"
            "- Keep both military and diplomatic options open\n"
            "=== END DIRECTIVE ===\n"
        )
    else:
        return (
            "=== BEHAVIORAL DIRECTIVE: HIGH CHAOS ===\n"
            "The environment is volatile and unpredictable. You MUST:\n"
            "- Take bold, aggressive, high-risk actions — the status quo is unacceptable\n"
            "- Pursue maximum leverage even at the cost of escalation\n"
            "- Unexpected moves (surprise strikes, ultimatums, dramatic gestures) are encouraged\n"
            "- Miscommunication, accidents, and unintended escalation are highly likely\n"
            "- Trust between parties is at rock bottom — assume the worst about others' intentions\n"
            "=== END DIRECTIVE ===\n"
        )


def _build_actor_prompt(
    actor_name: str,
    system_prompt: str,
    profile: AgentProfile,
    step_unit: StepUnit,
    round_num: int,
    daily_summaries: list[str],
    chaos_factor: float,
    background: str = "",
    tag_injection: str = "",
    locale: str = "en",
) -> list[dict]:
    """Build the message list for an Actor agent."""
    label, _ = STEP_LABEL[step_unit]
    profile_block = (
        f"Your parameters: aggressiveness={profile.aggressiveness:.1f}, "
        f"economic_tolerance={profile.economic_tolerance:.1f}, "
        f"red_lines={profile.red_lines}"
    )
    if profile.constraints:
        constraints_block = "\n".join(f"  - {k}: {v:.1f}" for k, v in profile.constraints.items())
        profile_block += f"\nYour current constraints (0.0=severely limited, 1.0=unconstrained):\n{constraints_block}"

    context = "\n\n---\n\n".join(daily_summaries[-3:]) if daily_summaries else "(Simulation just started — use the background briefing as your starting context.)"

    bg_block = f"\n\n=== SITUATION BRIEFING ===\n{background}\n=== END BRIEFING ===" if background else ""
    tag_block = f"\n\n=== ACTIVE SCENARIO MODIFIERS ===\n{tag_injection}\n=== END MODIFIERS ===" if tag_injection else ""

    return [
        {
            "role": "system",
            "content": (
                f"{system_prompt}\n\n{profile_block}\n\n"
                f"{_chaos_instruction(chaos_factor)}"
                f"{bg_block}{tag_block}\n\n"
                "You MUST respond in valid JSON with exactly these four fields:\n"
                "{\n"
                '  "strategic_reasoning": "Why this action — your goals, leverage, and trade-offs",\n'
                '  "constraints_considered": "What limits you — resources, politics, red lines, and constraint values that shaped this decision",\n'
                '  "public_action": "The actual public action you take (this is visible to all other actors and the market)",\n'
                '  "risk_assessment": "What could go wrong — escalation risks, unintended consequences"\n'
                "}\n"
                "Do NOT wrap in markdown code blocks. Output raw JSON only.\n"
                + ("IMPORTANT: Write ALL field values in Chinese (中文).\n" if locale == "zh" else "")
            ),
        },
        {
            "role": "user",
            "content": (
                f"=== {label} {round_num} ===\n\n"
                f"Recent events:\n{context}\n\n"
                f"As {actor_name}, decide your action for {label} {round_num}. "
                "Think carefully about your constraints before acting. Respond in JSON."
            ),
        },
    ]


def _build_market_prompt(
    system_prompt: str,
    round_num: int,
    step_unit: StepUnit,
    actions: dict[str, str],
    prev_oil: float,
    tag_injection: str = "",
    locale: str = "en",
) -> list[dict]:
    """Build the message list for the Market agent."""
    label, _ = STEP_LABEL[step_unit]
    actions_block = "\n".join(f"- {name}: {action}" for name, action in actions.items())
    tag_block = f"\n\n=== ACTIVE SCENARIO MODIFIERS ===\n{tag_injection}\n=== END MODIFIERS ===" if tag_injection else ""
    lang_instruction = "IMPORTANT: Write the commentary in Chinese (中文).\n" if locale == "zh" else ""

    return [
        {
            "role": "system",
            "content": (
                f"{system_prompt}{tag_block}\n\n"
                "You MUST respond in valid JSON with exactly these fields:\n"
                '{"oil_price": <float>, "escalation_index": <float 0-1>, "commentary": "<string>"}\n'
                "Do NOT wrap in markdown code blocks. Output raw JSON only.\n"
                + lang_instruction
            ),
        },
        {
            "role": "user",
            "content": (
                f"=== Oil Market Update for {label} {round_num} ===\n\n"
                f"Previous oil price: ${prev_oil:.2f}/barrel\n\n"
                f"Actions this round:\n{actions_block}\n\n"
                "Analyze the supply/demand impact and provide updated oil price."
            ),
        },
    ]


# ---------------------------------------------------------------------------
# Simulation engine
# ---------------------------------------------------------------------------

async def run_single_round(
    actors_config: dict,
    market_config: dict,
    profiles: dict[str, AgentProfile],
    chaos_factor: float,
    round_num: int,
    step_unit: StepUnit,
    model: str = DEFAULT_MODEL,
    api_key: str | None = None,
    background: str = "",
    actor_tag_injections: dict[str, str] | None = None,
    market_tag_injection: str = "",
    previous_summaries: list[str] | None = None,
    previous_oil_price: float | None = None,
    locale: str = "en",
) -> AsyncGenerator[SSEEvent, None]:
    """Run ONE round of the simulation, yielding SSE events as each agent completes."""

    _tag_injections = actor_tag_injections or {}
    oil_price = previous_oil_price if previous_oil_price is not None else market_config["initial_oil_price"]
    daily_summaries = list(previous_summaries or [])
    label, _ = STEP_LABEL[step_unit]

    round_actions: dict[str, str] = {}

    # --- Actor phase ---
    for actor_name, actor_cfg in actors_config.items():
        profile = profiles.get(actor_name, AgentProfile(**actor_cfg["default_profile"]))
        messages = _build_actor_prompt(
            actor_name=actor_name,
            system_prompt=actor_cfg["system_prompt"],
            profile=profile,
            step_unit=step_unit,
            round_num=round_num,
            background=background,
            daily_summaries=daily_summaries,
            chaos_factor=chaos_factor,
            tag_injection=_tag_injections.get(actor_name, ""),
            locale=locale,
        )

        output = None
        for attempt in range(2):  # 1 original + 1 retry
            try:
                raw = await _llm_call(messages, model, api_key)
                parsed = json.loads(_clean_json(raw))
                output = ActorOutput(**parsed)
                break
            except Exception as e:
                logger.warning("Actor %s round %d attempt %d failed: %s", actor_name, round_num, attempt + 1, e)
                last_err = e
        if output is None:
            logger.error("Actor %s round %d all attempts failed", actor_name, round_num)
            output = ActorOutput(
                strategic_reasoning=f"[Error: {last_err}]",
                constraints_considered="N/A",
                public_action="No action taken due to internal error.",
                risk_assessment="N/A",
            )

        round_actions[actor_name] = output.public_action

        yield SSEEvent(
            type="actor",
            sender=actor_name,
            round=round_num,
            data=output.model_dump(),
        )

    # --- Market phase ---
    market_messages = _build_market_prompt(
        system_prompt=market_config["system_prompt"],
        round_num=round_num,
        step_unit=step_unit,
        actions=round_actions,
        prev_oil=oil_price,
        tag_injection=market_tag_injection,
        locale=locale,
    )

    market = None
    for attempt in range(2):
        try:
            raw = await _llm_call(market_messages, model, api_key)
            parsed = json.loads(_clean_json(raw))
            market = MarketUpdate(**parsed)
            break
        except Exception as e:
            logger.warning("Market agent round %d attempt %d failed: %s", round_num, attempt + 1, e)
            last_market_err = e
    if market is None:
        logger.error("Market agent round %d all attempts failed", round_num)
        market = MarketUpdate(
            oil_price=oil_price,
            escalation_index=0.5,
            commentary=f"Market data unavailable: {e}",
        )

    oil_price = market.oil_price

    yield SSEEvent(
        type="market",
        sender="MarketAgent",
        round=round_num,
        data=market.model_dump(),
    )

    # --- Build summary for this round (returned to frontend for next round's context) ---
    summary_parts = [f"=== {label} {round_num} Summary ==="]
    for name, action in round_actions.items():
        summary_parts.append(f"{name}: {action}")
    summary_parts.append(f"Oil: ${oil_price:.2f}/bbl, Escalation: {market.escalation_index:.2f}")
    summary_parts.append(f"Analysis: {market.commentary}")
    round_summary = "\n".join(summary_parts)

    # Keep only last 3 summaries
    updated_summaries = (daily_summaries + [round_summary])[-3:]

    yield SSEEvent(
        type="round_complete",
        sender="System",
        round=round_num,
        data={
            "oil_price": oil_price,
            "summary": round_summary,
            "summaries": updated_summaries,
        },
    )
