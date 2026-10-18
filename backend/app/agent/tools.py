"""Tools / Skills Registry (MCP-style, in-process) with role-based permissions and enterprise-grade Docker lab generation."""

import re
import yaml
import uuid
from app.db import db

# ---------------------------------------------------------------- MCP Tools Manifest
MCP_TOOLS = [
    {
        "name": "search_knowledge",
        "description": "Query the Spark-clustered MongoDB security corpus for articles, docs, and advisories.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keyword or phrase"},
                "category": {"type": "string", "description": "Optional category filter"}
            },
            "required": ["query"]
        },
        "permissions": ["planner", "researcher", "orchestrator"]
    },
    {
        "name": "validate_tool_whitelist",
        "description": "Validate containerized security tools against approved security whitelist.",
        "parameters": {
            "type": "object",
            "properties": {
                "tools": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["tools"]
        },
        "permissions": ["architect", "orchestrator"]
    },
    {
        "name": "build_enterprise_lab",
        "description": "Generate a professional CTF lab with target machine (10.10.X.X), vulnerable services, and a dual-mode Attack Box (Web Shell + SSH).",
        "parameters": {
            "type": "object",
            "properties": {
                "tools": {"type": "array", "items": {"type": "string"}},
                "difficulty": {"type": "string", "enum": ["beginner", "intermediate", "advanced", "expert"]},
                "target_ip": {"type": "string", "description": "Virtual IP for the target machine"}
            },
            "required": ["tools", "target_ip"]
        },
        "permissions": ["architect", "orchestrator"]
    }
]

def get_mcp_manifest():
    return MCP_TOOLS

# ---------------------------------------------------------------- Retrieval Tool
def search_knowledge(query: str, category: str | None = None, limit: int = 5) -> list[dict]:
    flt: dict = {"$or": [
        {"title": {"$regex": re.escape(query), "$options": "i"}},
        {"summary": {"$regex": re.escape(query), "$options": "i"}},
        {"tags": {"$regex": re.escape(query), "$options": "i"}},
    ]}
    if category:
        flt["category"] = category
    cur = (db.resources.find(flt, {"title": 1, "url": 1, "summary": 1,
                                   "category": 1, "cluster_slug": 1})
           .sort("bookmark_count", -1).limit(limit))
    return [{"title": r["title"], "url": r["url"], "summary": r.get("summary", "")[:240],
             "category": r["category"], "cluster": r.get("cluster_slug", "")}
            for r in cur]

# ---------------------------------------------------------------- Docker Whitelist (Non-Conflicting Ports)
WHITELIST = [
    {"image": "tsl0922/ttyd:latest", "name": "attack-box",
     "planets": ["tools-labs"],
     "purpose": "Web-based Terminal (Attack Box) with pre-installed pentest tools",
     "command": "docker exec -it attack-box bash"},
    {"image": "kalilinux/kali-rolling", "name": "kali",
     "planets": ["tools-labs", "network-security"],
     "purpose": "Full Kali Linux suite (nmap, metasploit, etc.)",
     "command": "docker run --rm -it kalilinux/kali-rolling bash"},
    {"image": "instrumentisto/nmap", "name": "nmap",
     "planets": ["network-security"],
     "purpose": "Port scanning & enumeration",
     "command": "docker run --rm instrumentisto/nmap -sV <target>"},
    {"image": "secsi/ffuf", "name": "ffuf",
     "planets": ["web-security"],
     "purpose": "Fast Web Fuzzer",
     "command": "docker run --rm secsi/ffuf -u <url>/FUZZ -w /wordlists/common.txt"},
    {"image": "bkimminich/juice-shop", "name": "target-web",
     "planets": ["web-security"],
     "purpose": "Vulnerable Web Application (Juice Shop)",
     "command": "docker run --rm -p 3001:3000 bkimminich/juice-shop"},
    {"image": "vulnerables/web-dvwa", "name": "target-dvwa",
     "planets": ["web-security"],
     "purpose": "Damn Vulnerable Web App",
     "command": "docker run --rm -p 8081:80 vulnerables/web-dvwa"},
]

# Names the UI / older code may send -> canonical whitelist names.
TOOL_ALIASES = {"juice-shop": "target-web", "dvwa": "target-dvwa"}

# Tools that have no image of their own; they are installed in the attack box.
ATTACK_BOX_PACKAGES = {"sqlmap", "john", "hydra", "metasploit-framework", "wireshark", "ffuf", "nmap", "curl"}
PACKAGE_ALIASES = {"metasploit": "metasploit-framework"}


def validate_image_selection(names: list[str]) -> list[dict]:
    by_name = {w["name"]: w for w in WHITELIST}
    picked, seen = [], set()
    for n in names:
        n = TOOL_ALIASES.get(n, n)
        if n in by_name and n not in seen:
            picked.append(by_name[n])
            seen.add(n)
    return picked


def extra_packages(names: list[str]) -> list[str]:
    """Selected names that are plain apt packages for the attack box."""
    out = []
    for n in names:
        n = PACKAGE_ALIASES.get(n, n)
        if n in ATTACK_BOX_PACKAGES and n not in out:
            out.append(n)
    return out


def tool_groups() -> dict[str, list[str]]:
    """Picker groups for the UI -- built from what the backend can really provision."""
    return {
        "Attack box": ["kali", "attack-box"],
        "Recon": ["nmap", "ffuf"],
        "Exploitation": ["sqlmap", "hydra", "john", "metasploit"],
        "Targets": ["target-web", "target-dvwa"],
    }


def build_compose(images: list[dict], difficulty: str = "intermediate",
                  target_ip: str = "10.10.10.10", packages: list[str] | None = None) -> tuple[str, list[str]]:
    services, warnings = {}, []
    pkgs = sorted(set(["nmap", "curl", "ffuf"] + list(packages or [])))

    # Attack box (use `docker compose exec attack-box bash`)
    services["attack-box"] = {
        "image": "kalilinux/kali-rolling",
        "container_name": "secstack-attack-box",
        "command": f"bash -c 'apt-get update && apt-get install -y {' '.join(pkgs)} && tail -f /dev/null'",
        "networks": {"ctf-net": {"ipv4_address": "10.10.10.2"}},
        "cap_add": ["NET_RAW"],
        "mem_limit": "2g",
    }

    # Target machine: must be a vulnerable app image, never a scanner/attack tool.
    target_image = next((w for w in images if w["name"].startswith("target")), None)
    if target_image is None:
        target_image = next(w for w in WHITELIST if w["name"] == "target-web")
        warnings.append("No target selected; defaulted to Juice Shop.")
    services["target-machine"] = {
        "image": target_image["image"],
        "container_name": "secstack-target",
        "networks": {"ctf-net": {"ipv4_address": target_ip}},
        "mem_limit": "1g",
    }
    if target_image["name"] == "target-web":
        services["target-machine"]["ports"] = ["3001:3000"]
    elif target_image["name"] == "target-dvwa":
        services["target-machine"]["ports"] = ["8081:80"]

    compose = {
        "networks": {"ctf-net": {"driver": "bridge",
                                 "ipam": {"config": [{"subnet": "10.10.10.0/24"}]}}},
        "services": services,
    }
    return yaml.safe_dump(compose, sort_keys=False), warnings