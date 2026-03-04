"""
Social simulation problem for FunSearch.

The goal: simulate interactions between AI agents and optimize their social behaviors.
"""

from __future__ import annotations

import json
import pathlib
from typing import Callable, Dict, List, Tuple

Agent = Dict[str, object]
Conversation = List[Dict[str, str]]
SocialMetrics = Dict[str, float]


def _load_scenarios() -> List[Dict]:
    """Load social interaction scenarios from data/social_scenarios.json."""
    data_path = pathlib.Path(__file__).parent.parent / "data" / "social_scenarios.json"
    try:
        raw = json.loads(data_path.read_text(encoding="utf-8"))
        return raw["scenarios"]
    except FileNotFoundError:
        # Default scenarios if file doesn't exist
        return [
            {"id": "debate", "topic": "AI ethics", "max_turns": 10},
            {"id": "collaboration", "topic": "Problem solving", "max_turns": 8},
            {"id": "creative", "topic": "Story writing", "max_turns": 6}
        ]


def load_solution_function(candidate_code: str) -> Callable[[List[Agent]], SocialMetrics]:
    """
    Execute candidate code and return its social_interaction function.
    The candidate must define:

    def social_interaction(agents, scenario):
        # agents: list of agent dictionaries with personality traits
        # scenario: dict with topic and constraints
        return {"cohesion": float, "diversity": float, "engagement": float}
    """
    local_vars: Dict[str, object] = {}
    # Safe builtins for social simulation code
    safe_globals = {
        "__builtins__": {
            "range": range,
            "len": len,
            "sorted": sorted,
            "set": set,
            "list": list,
            "dict": dict,
            "enumerate": enumerate,
            "min": min,
            "max": max,
            "abs": abs,
            "sum": sum,
            "random": __import__("random"),
        }
    }
    exec(candidate_code, safe_globals, local_vars)
    if "social_interaction" not in local_vars:
        raise ValueError("Candidate code must define social_interaction(agents, scenario).")
    return local_vars["social_interaction"]


def _calculate_cohesion(conversation: Conversation) -> float:
    """Measure how well agents stay on topic and build on each other's ideas."""
    if not conversation:
        return 0.0
    
    topic_consistency = 0.0
    for i, turn in enumerate(conversation):
        if i > 0:
            # Simple topic consistency check
            topic_consistency += len(set(turn["content"].lower().split()) & 
                                   set(conversation[i-1]["content"].lower().split()))
    
    return topic_consistency / len(conversation)


def _calculate_diversity(conversation: Conversation) -> float:
    """Measure variety of perspectives and vocabulary."""
    if not conversation:
        return 0.0
    
    all_words = set()
    for turn in conversation:
        all_words.update(turn["content"].lower().split())
    
    return len(all_words) / max(1, sum(len(turn["content"].split()) for turn in conversation))


def _calculate_engagement(conversation: Conversation) -> float:
    """Measure level of participation and interaction."""
    if not conversation:
        return 0.0
    
    # Simple engagement metric based on response length and frequency
    avg_length = sum(len(turn["content"]) for turn in conversation) / len(conversation)
    return min(1.0, avg_length / 100.0)  # Normalize to 0-1


def score_function(solution_fn: Callable[[List[Agent]], SocialMetrics]) -> Dict[str, float]:
    """
    Evaluate a social interaction function on various scenarios.
    
    Score is weighted combination of social metrics:
    - Higher cohesion = better topic focus
    - Higher diversity = more varied perspectives  
    - Higher engagement = more active participation
    """
    scenarios = _load_scenarios()
    total_score = 0.0
    details = []

    for scenario in scenarios:
        # Create test agents with different personalities
        test_agents = [
            {"id": f"agent_{i}", "personality": f"personality_type_{i}"}
            for i in range(3)  # Start with 3 agents
        ]
        
        try:
            metrics = solution_fn(test_agents, scenario)
            
            # Extract individual metrics with defaults
            cohesion = metrics.get("cohesion", 0.0)
            diversity = metrics.get("diversity", 0.0)
            engagement = metrics.get("engagement", 0.0)
            
            # Weighted score (can be adjusted)
            scenario_score = 0.4 * cohesion + 0.3 * diversity + 0.3 * engagement
            total_score += scenario_score
            
            details.append({
                "scenario": scenario["id"],
                "cohesion": cohesion,
                "diversity": diversity,
                "engagement": engagement,
                "score": scenario_score
            })
            
        except Exception as e:
            # Penalize functions that crash
            total_score -= 1.0
            details.append({
                "scenario": scenario["id"],
                "error": str(e),
                "score": -1.0
            })

    avg_score = total_score / len(scenarios)
    return {"score": avg_score, "details": details}
