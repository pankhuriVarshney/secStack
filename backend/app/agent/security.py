"""Security harness Layer 1: deterministic veto for prompt injection, privilege escalation, and unsafe flags."""

import re
import yaml

FORBIDDEN_PATTERNS = [
    r"privileged:\s*true",
    r"network_mode:\s*host",
    r"pid:\s*host",
    r"-\s*['\"]?/var/run/docker\.sock",
    r"rm\s+-rf\s+/",
    r"eval\(",
]

def scan_text_input(text: str) -> tuple[bool, str]:
    for pat in FORBIDDEN_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            return False, f"Deterministic security veto: input matched forbidden pattern '{pat}'"
    return True, "Passed Layer-1 security check"

def scan_compose_safety(compose_yaml: str) -> tuple[bool, list[str]]:
    issues = []
    try:
        doc = yaml.safe_load(compose_yaml)
    except yaml.YAMLError as e:
        return False, [f"Invalid YAML syntax: {e}"]
    
    for svc, cfg in (doc.get("services") or {}).items():
        if cfg.get("privileged"):
            issues.append(f"Service '{svc}' requests privileged mode -- vetoed")
        if cfg.get("network_mode") == "host":
            issues.append(f"Service '{svc}' requests host networking -- vetoed")
        vols = " ".join(str(v) for v in cfg.get("volumes", []))
        if "docker.sock" in vols:
            issues.append(f"Service '{svc}' attempts to mount docker.sock -- vetoed")
    
    return (len(issues) == 0), issues
