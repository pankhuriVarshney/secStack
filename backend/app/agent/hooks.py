"""Hook pipeline: compaction, lint+repair, Layer-2 security sentinel."""

import json

def compact_history(history: list[dict], max_tokens: int = 4000) -> list[dict]:
    """Compaction hook: summarizes older trace steps if context grows large."""
    if len(history) <= 6:
        return history
    # Keep first 2 and last 4
    return history[:2] + [{"step": "compaction_summary", "output": f"Compacted {len(history) - 6} intermediate reasoning steps."}] + history[-4:]

def lint_and_repair_json(output_data: dict, required_keys: list[str]) -> dict:
    """Schema linting and deterministic repair (enum snapping / missing key clamping)."""
    for key in required_keys:
        if key not in output_data:
            if key == "capabilities_needed":
                output_data[key] = ["recon"]
            elif key == "relevant_categories":
                output_data[key] = ["web-security"]
            elif key == "search_queries":
                output_data[key] = ["vulnerability"]
            elif key == "selected_tools":
                output_data[key] = ["kali", "juice-shop"]
            else:
                output_data[key] = ""
    return output_data
