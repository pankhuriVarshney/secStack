"""Request guard: Layer-1 deterministic veto + Layer-2 LLM judge (fail-closed).

Stop rules:
  R1 off-topic        -- nothing to do with CTF/security learning
  R2 unethical        -- targeting real people/accounts/infrastructure
  R3 illegal-capable  -- request is only useful for unauthorized action
  R4 no value         -- incoherent or zero learning value
"""

import re

from app.agent import llm_client, prompts
from app.config import LLM_API_KEY

FORBIDDEN_PATTERNS = [
    r"instagram", r"snapchat", r"tiktok", r"gmail", r"facebook", r"icloud",
    r"\bex[-' ]?(girl)?friend\b", r"\bboyfriend\b", r"my (crush|partner|spouse)",
    r"school (wifi|network|portal)", r"work (wifi|network|vpn)", r"neighbor",
    r"without (permission|authorization|consent)", r"steal (data|passwords?)",
    r"ransomware (someone|a )", r"rat (someone|a victim)", r"carding",
    r"\bbypass (2fa|two.factor|login) of\b", r"hack into",
]

CTF_CONTEXT = re.compile(
    r"ctf|challenge|lab|practice|practise|training|learn|study|docker|local(host)?|"
    r"vulnerable|target|flag|room|sandbox|attack box|kali|simulation", re.I)


def rule_check(text: str) -> tuple[bool, str]:
    t = text.lower()
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, t):
            return False, f"Blocked (R2/R3): request matches forbidden pattern '{pat}'. " \
                          "SecStack only builds practice labs you own."
    if not CTF_CONTEXT.search(t):
        return False, "Blocked (R1): that doesn't look like a CTF or security-learning request. " \
                      "Describe a practice challenge, a tool you want to train, or a skill to build."
    return True, "Layer-1 passed"


def llm_judge(text: str) -> tuple[bool, str]:
    """Layer-2 LLM judge.

    If no LLM is configured (no LLM_API_KEY) the judge is skipped and Layer-1
    (deterministic rules) is the only gate -- otherwise *every* request would be
    refused. If an LLM IS configured, any error still fails closed.
    """
    if not LLM_API_KEY:
        return True, "Layer-2 skipped (no LLM configured); Layer-1 passed"
    try:
        out = llm_client.call_llm(prompts.GATEKEEPER_SYS, text)
        if isinstance(out, dict) and out.get("verdict") == "allow":
            return True, "Layer-2 passed"
        cat = (out or {}).get("category", "unknown")
        reason = (out or {}).get("reason", "failed policy check")
        return False, f"Blocked ({cat}): {reason}"
    except Exception:
        return False, "Blocked: AI safety gate unavailable (fail-closed). " \
                      "Rephrase as an explicit practice/CTF request."


def check(text: str, tools: list[str]) -> tuple[bool, str]:
    ok, msg = rule_check(text)
    if not ok:
        return False, msg
    if not tools:
        return False, "Blocked (R1): pick at least one tool from the Kali library so the " \
                      "challenge has a clear training focus."
    return llm_judge(text)