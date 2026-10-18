"""Agent Registry: roles, permissions, output schemas, spawn/handoff rights."""

AGENT_REGISTRY = {
    "planner": {
        "role": "Challenge Decomposition & RAG Planner",
        "permissions": ["search_knowledge"],
        "spawn_rights": ["researcher", "architect"],
        "handoff_target": "architect"
    },
    "researcher": {
        "role": "Knowledge Retrieval & Evidence Gatherer",
        "permissions": ["search_knowledge"],
        "spawn_rights": [],
        "handoff_target": "architect"
    },
    "architect": {
        "role": "Tool Selection & Docker Lab Constructor",
        "permissions": ["validate_tool_whitelist", "build_compose_lab"],
        "spawn_rights": ["compliance_critic"],
        "handoff_target": "compliance_critic"
    },
    "compliance_critic": {
        "role": "Security Harness Veto & Walkthrough Generator",
        "permissions": [],
        "spawn_rights": [],
        "handoff_target": None
    }
}

def get_agent_spec(name: str) -> dict:
    return AGENT_REGISTRY.get(name, {})
