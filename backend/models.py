"""Pydantic schemas for the Hormuz Simulator API."""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class StepUnit(str, Enum):
    day = "day"
    week = "week"
    month = "month"


class AgentProfile(BaseModel):
    """Per-country tunable parameters."""
    aggressiveness: float = Field(0.5, ge=0.0, le=1.0, description="Strategic aggressiveness")
    economic_tolerance: float = Field(0.5, ge=0.0, le=1.0, description="Ability to withstand economic pressure")
    red_lines: list[str] = Field(default_factory=list, description="Actions that trigger escalation")
    # Country-specific adjustable constraints (optional — loaded from soul defaults)
    constraints: dict[str, float] = Field(default_factory=dict, description="Country-specific constraint sliders")


class SimulationRequest(BaseModel):
    """Payload from the frontend to run ONE round of simulation."""
    client_uuid: str
    api_key: Optional[str] = None
    chaos_factor: float = Field(0.3, ge=0.0, le=1.0)
    profiles: dict[str, AgentProfile] = Field(default_factory=dict)
    round_num: int = Field(1, ge=1, description="Which round to simulate")
    step_unit: StepUnit = Field(StepUnit.day, description="Time granularity per round")
    active_tags: list[str] = Field(default_factory=list, description="IDs of active scenario tags")
    model: Optional[str] = None  # Override model for BYOK users
    locale: str = "en"  # Output language: "en" or "zh"
    # Context from previous rounds (fed back by frontend)
    previous_summaries: list[str] = Field(default_factory=list, description="Rolling summaries from prior rounds")
    previous_oil_price: Optional[float] = None  # None = use initial price


class ActorOutput(BaseModel):
    """Structured output expected from each Actor agent."""
    strategic_reasoning: str = Field(description="Why this action — goals, leverage, and trade-offs considered")
    constraints_considered: str = Field(description="What limits this actor — resources, politics, red lines")
    public_action: str = Field(description="The actual public action taken, visible to all parties")
    risk_assessment: str = Field(description="What could go wrong — escalation risks, unintended consequences")


class MarketUpdate(BaseModel):
    """Output from the Market agent."""
    oil_price: float
    escalation_index: float = Field(ge=0.0, le=1.0)
    commentary: str


class SSEEvent(BaseModel):
    """A single Server-Sent Event chunk."""
    type: str  # "actor", "market", "system", "error", "done"
    sender: str  # "Iran", "US", "MarketAgent", "System"
    round: int
    data: dict
