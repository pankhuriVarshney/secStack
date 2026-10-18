"""SecStack seed dataset.

CURATED: real, well-known cybersecurity learning resources (blogs, docs,
courses, labs, videos). FILLER: procedurally generated demo entries so the
galaxy visualization has volume on day one -- replace them over time with
live RSS/YouTube ingestion (scripts/ingest_rss.py).
"""

import random
import datetime as dt

CATEGORIES = [
    {"slug": "network-security",  "name": "Network Security",  "color": "#00f0ff",
     "description": "Protocols, traffic analysis, firewalls, WiFi and perimeter defense."},
    {"slug": "web-security",      "name": "Web Security",      "color": "#ff2d95",
     "description": "OWASP, injection, XSS, API security and bug bounty tradecraft."},
    {"slug": "cloud-security",    "name": "Cloud Security",    "color": "#7c3aed",
     "description": "AWS/Azure/GCP hardening, IAM, Kubernetes and serverless defense."},
    {"slug": "cryptography",      "name": "Cryptography",      "color": "#facc15",
     "description": "Ciphers, PKI, TLS, authentication protocols and crypto attacks."},
    {"slug": "certification-prep","name": "Certification Prep","color": "#22ff88",
     "description": "Security+, CEH, CISSP, OSCP and other exam study tracks."},
    {"slug": "threat-intel",      "name": "Threat Intelligence","color": "#ff6b1a",
     "description": "APT tracking, malware analysis, CVEs and detection engineering."},
    {"slug": "career-guides",     "name": "Career Guides",     "color": "#4f8ef7",
     "description": "Breaking into security, resumes, interviews and salary data."},
    {"slug": "tools-labs",        "name": "Tools & Labs",      "color": "#e879f9",
     "description": "Hands-on platforms, CTFs, tool documentation and practice ranges."},
]

CAT_COLORS = {c["slug"]: c["color"] for c in CATEGORIES}
CAT_NAMES = {c["slug"]: c["name"] for c in CATEGORIES}

# (category, title, url, source, media_type, difficulty, tags)
CURATED = [
    # ---------- web-security ----------
    ("web-security","PortSwigger Web Security Academy","https://portswigger.net/web-security","PortSwigger","course","beginner","xss,sqli,csrf, labs"),
    ("web-security","OWASP Top 10 (2021)","https://owasp.org/Top10/","OWASP","documentation","beginner","owasp, risk, checklist"),
    ("web-security","OWASP Cheat Sheet Series","https://cheatsheetseries.owasp.org/","OWASP","cheatsheet","intermediate","cheatsheet, hardening"),
    ("web-security","OWASP Juice Shop","https://owasp.org/www-project-juice-shop/","OWASP","lab","beginner","ctf, vulnerable app"),
    ("web-security","WebGoat - OWASP vulnerable app","https://owasp.org/www-project-webgoat/","OWASP","lab","beginner","training, java"),
    ("web-security","PortSwigger XSS Cheat Sheet","https://portswigger.net/web-security/cross-site-scripting/cheat-sheet","PortSwigger","cheatsheet","intermediate","xss, payloads"),
    ("web-security","SSRF cheatsheet by Maxence Schmitt","https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html","OWASP","cheatsheet","intermediate","ssrf, prevention"),
    ("web-security","OWASP API Security Top 10","https://owasp.org/API-Security/","OWASP","documentation","intermediate","api, rest, graphql"),
    ("web-security","MDN Web Security documentation","https://developer.mozilla.org/en-US/docs/Web/Security","MDN","documentation","beginner","browser, headers, cors"),
    ("web-security","HackerOne Hacktivity","https://hackerone.com/hacktivity","HackerOne","article","intermediate","bug bounty, disclosures"),
    ("web-security","Bugcrowd blog","https://www.bugcrowd.com/blog/","Bugcrowd","article","intermediate","bug bounty, research"),
    ("web-security","Intigriti blog","https://blog.intigriti.com/","Intigriti","article","intermediate","bug bounty, web"),
    # ---------- network-security ----------
    ("network-security","Wireshark User Guide","https://www.wireshark.org/docs/wsug_html/","Wireshark","documentation","beginner","pcap, analysis, protocol"),
    ("network-security","Wireshark sample captures","https://wiki.wireshark.org/SampleCaptures","Wireshark","documentation","beginner","pcap, samples"),
    ("network-security","tcpdump examples (Daniel Miessler)","https://danielmiessler.com/blog/tcpdump/","Daniel Miessler","article","beginner","cli, packets, forensics"),
    ("network-security","Practical Networking YouTube channel","https://www.youtube.com/@PracticalNetworking","YouTube","video","beginner","routing, switching, ccna"),
    ("network-security","Jeremy's IT Lab CCNA course","https://www.youtube.com/@JeremysITLab","YouTube","video","beginner","ccna, cisco, labs"),
    ("network-security","Cisco Networking Academy","https://www.netacad.com/","Cisco","course","beginner","networking, cisco"),
    ("network-security","Nmap reference guide","https://nmap.org/book/man.html","Nmap","documentation","beginner","scanning, recon"),
    ("network-security","Cloudflare Learning Center (DNS/DDoS)","https://www.cloudflare.com/learning/","Cloudflare","article","beginner","dns, ddos, cdn"),
    ("network-security","RFC 8446 - TLS 1.3","https://www.rfc-editor.org/rfc/rfc8446","IETF RFC","documentation","advanced","tls, handshake, protocol"),
    ("network-security","DNSSEC guide (ICANN)","https://www.icann.org/resources/pages/dnssec-what-is-it-01-2019-en","ICANN","documentation","intermediate","dns, dnssec"),
    ("network-security","Aircrack-ng documentation","https://www.aircrack-ng.org/documentation.html","Aircrack-ng","documentation","intermediate","wifi, wireless, cracking"),
    # ---------- cloud-security ----------
    ("cloud-security","AWS Security Blog","https://aws.amazon.com/blogs/security/","AWS","article","intermediate","aws, iam, cloud"),
    ("cloud-security","AWS Well-Architected Security Pillar","https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/","AWS","documentation","intermediate","aws, architecture, review"),
    ("cloud-security","Microsoft Learn: Azure security","https://learn.microsoft.com/en-us/azure/security/","Microsoft Learn","documentation","intermediate","azure, cloud, defender"),
    ("cloud-security","Cloud Security Alliance CCM","https://cloudsecurityalliance.org/research/cloud-controls-matrix","CSA","documentation","intermediate","compliance, controls"),
    ("cloud-security","Kubernetes security documentation","https://kubernetes.io/docs/concepts/security/","Kubernetes","documentation","intermediate","kubernetes, hardening"),
    ("cloud-security","Falco - runtime security docs","https://falco.org/docs/","Falco","documentation","intermediate","runtime, eBPF, detection"),
    ("cloud-security","Prowler - AWS security best practices","https://github.com/prowler-cloud/prowler","GitHub","documentation","intermediate","aws, auditing, oss"),
    ("cloud-security","ScoutSuite - multi-cloud auditing","https://github.com/nccgroup/ScoutSuite","GitHub","documentation","intermediate","aws, azure, gcp, audit"),
    ("cloud-security","Pacu - AWS exploitation framework","https://github.com/RhinoSecurityLabs/pacu","GitHub","documentation","advanced","aws, red team"),
    ("cloud-security","Wazuh documentation","https://documentation.wazuh.com/","Wazuh","documentation","intermediate","siem, xdr, hids"),
    # ---------- cryptography ----------
    ("cryptography","Cryptohack - interactive crypto challenges","https://cryptohack.org/","Cryptohack","lab","intermediate","math, ciphers, ctf"),
    ("cryptography","CryptoPals challenges","https://cryptopals.com/","CryptoPals","lab","advanced","aes, rsa, mtc"),
    ("cryptography","Dan Boneh: Cryptography I (Coursera)","https://www.coursera.org/learn/crypto","Coursera","course","intermediate","theory, symmetric, public key"),
    ("cryptography","Schneier on Security blog","https://www.schneier.com/","Bruce Schneier","article","intermediate","crypto, policy, analysis"),
    ("cryptography","JWT.io - JSON Web Token introduction","https://jwt.io/introduction","Auth0","documentation","beginner","jwt, tokens, auth"),
    ("cryptography","Auth0 blog: OAuth 2.0 and OpenID Connect","https://auth0.com/blog/","Auth0","article","intermediate","oauth, oidc, identity"),
    ("cryptography","passkeys.dev","https://passkeys.dev/","passkeys.dev","documentation","intermediate","passkeys, webauthn, phishing"),
    ("cryptography","Let's Encrypt documentation (ACME/PKI)","https://letsencrypt.org/docs/","Let's Encrypt","documentation","beginner","pki, certificates, acme"),
    ("cryptography","OpenSSL documentation","https://docs.openssl.org/","OpenSSL","documentation","intermediate","cli, certificates, tls"),
    ("cryptography","WireGuard whitepaper","https://www.wireguard.com/papers/wireguard.pdf","WireGuard","documentation","advanced","vpn, protocol, noise"),
    # ---------- certification-prep ----------
    ("certification-prep","Professor Messer - Security+ SY0-701","https://www.professormesser.com/security-plus/sy0-701/sy0-701-video/","Professor Messer","video","beginner","comptia, security+, free"),
    ("certification-prep","Professor Messer - Network+ N10-009","https://www.professormesser.com/network-plus/n10-009/n10-009-video/","Professor Messer","video","beginner","comptia, network+"),
    ("certification-prep","CompTIA Security+ SY0-701 exam objectives (PDF)","https://www.comptia.org/certifications/security","CompTIA","documentation","beginner","comptia, exam objectives"),
    ("certification-prep","ISC2 Certified in Cybersecurity - free course & exam","https://www.isc2.org/landing/1mcc","ISC2","course","beginner","isc2, cc, entry level"),
    ("certification-prep","CISSP study resources (ISC2)","https://www.isc2.org/certifications/cissp","ISC2","documentation","advanced","cissp, isc2, domains"),
    ("certification-prep","OffSec OSCP certification","https://www.offsec.com/courses/pen-200/","OffSec","course","advanced","oscp, pentest, lab"),
    ("certification-prep","EC-Council CEH program","https://www.eccouncil.org/train-certify/certified-ethical-hacker-ceh/","EC-Council","course","intermediate","ceh, ethical hacking"),
    ("certification-prep","Microsoft SC-200 security operations study path","https://learn.microsoft.com/en-us/credentials/certifications/security-operations-analyst-associate/","Microsoft Learn","course","intermediate","azure, sentinel, soc"),
    ("certification-prep","ExamTopics SY0-701 practice discussions","https://www.examtopics.com/exams/comptia/sy0-701/","ExamTopics","article","intermediate","practice questions, comptia"),
    ("certification-prep","Cybrary free courses","https://www.cybrary.it/","Cybrary","course","beginner","free, multiple vendors"),
    # ---------- threat-intel ----------
    ("threat-intel","MITRE ATT&CK knowledge base","https://attack.mitre.org/","MITRE","documentation","intermediate","apt, tactics, techniques"),
    ("threat-intel","MITRE D3FEND","https://d3fend.mitre.org/","MITRE","documentation","intermediate","detection, countermeasures"),
    ("threat-intel","Krebs on Security","https://krebsonsecurity.com/","Brian Krebs","article","intermediate","investigations, breaches"),
    ("threat-intel","The Hacker News","https://thehackernews.com/","The Hacker News","article","beginner","news, vulnerabilities"),
    ("threat-intel","BleepingComputer","https://www.bleepingcomputer.com/","BleepingComputer","article","beginner","news, ransomware, malware"),
    ("threat-intel","Dark Reading","https://www.darkreading.com/","Dark Reading","article","intermediate","news, analysis"),
    ("threat-intel","Google Project Zero","https://googleprojectzero.blogspot.com/","Google Project Zero","article","advanced","0day, vuln research"),
    ("threat-intel","Microsoft Security Response Center","https://msrc.microsoft.com/blog","MSRC","article","intermediate","vulns, advisories"),
    ("threat-intel","CISA known exploited vulnerabilities catalog","https://www.cisa.gov/known-exploited-vulnerabilities-catalog","CISA","documentation","intermediate","cve, kev, patching"),
    ("threat-intel","NVD - National Vulnerability Database","https://nvd.nist.gov/","NIST","documentation","intermediate","cve, scoring"),
    ("threat-intel","SANS Internet Storm Center","https://isc.sans.edu/","SANS ISC","article","intermediate","diaries, sensors, trends"),
    ("threat-intel","Mandiant M-Trends report","https://www.mandiant.com/resources/m-trends","Mandiant","article","intermediate","apt, ir, metrics"),
    ("threat-intel","Unit 42 threat research","https://unit42.paloaltonetworks.com/","Palo Alto Unit 42","article","intermediate","apt, malware"),
    ("threat-intel","VirusTotal blog","https://blog.virustotal.com/","VirusTotal","article","intermediate","malware, hunting"),
    ("threat-intel","YARA documentation","https://yara.readthedocs.io/","YARA","documentation","intermediate","yara, detection, malware"),
    ("threat-intel","Sigma rule format specification","https://sigmahq.io/docs/basics/rules.html","SigmaHQ","documentation","intermediate","sigma, detection, siem"),
    ("threat-intel","Atomic Red Team","https://github.com/redcanaryco/atomic-red-team","Red Canary","documentation","intermediate","mitre, emulation, detection"),
    ("threat-intel","Microsoft Digital Defense Report","https://www.microsoft.com/en-us/security/security-insider/microsoft-digital-defense-report","Microsoft","article","intermediate","report, statistics"),
    # ---------- career-guides ----------
    ("career-guides","r/cybersecurity wiki - getting started","https://www.reddit.com/r/cybersecurity/wiki/index/","Reddit","article","beginner","roadmap, community, faq"),
    ("career-guides","TCM Security - affordable training","https://tcm-sec.com/","TCM Security","course","beginner","pnpt, affordable, practical"),
    ("career-guides","So you want to work in security? (isfdb)","https://medium.com/@magoo/","Medium","article","beginner","advice, culture"),
    ("career-guides","Daniel Miessler: How to build a successful Infosec career","https://danielmiessler.com/blog/building-a-successful-infosec-career/","Daniel Miessler","article","beginner","career, strategy"),
    ("career-guides","HackerSploit career & red team roadmap videos","https://www.youtube.com/@HackerSploit","YouTube","video","beginner","roadmap, blue team"),
    ("career-guides","Cybersecurity resume guide (Springboard)","https://www.springboard.com/blog/cybersecurity/cybersecurity-resume/","Springboard","article","beginner","resume, interviews"),
    ("career-guides","National Cybersecurity Workforce Framework (NICE)","https://www.nist.gov/itl/applied-cybersecurity/nice/nice-framework-resource-center","NIST NICE","documentation","intermediate","work roles, skills"),
    ("career-guides","LetsDefend blue team career path","https://letsdefend.io/","LetsDefend","course","beginner","soc analyst, blue team"),
    # ---------- tools-labs ----------
    ("tools-labs","Hack The Box Academy","https://academy.hackthebox.com/","Hack The Box","lab","intermediate","htb, modules, certs"),
    ("tools-labs","TryHackMe learning paths","https://tryhackme.com/","TryHackMe","lab","beginner","rooms, guided"),
    ("tools-labs","CyberDefenders blue team challenges","https://cyberdefenders.org/","CyberDefenders","lab","intermediate","dfir, blue team, challenges"),
    ("tools-labs","Metasploit Unleashed","https://www.offsec.com/metasploit-unleashed/","OffSec","course","intermediate","metasploit, exploitation"),
    ("tools-labs","Burp Suite documentation","https://portswigger.net/burp/documentation","PortSwigger","documentation","beginner","proxy, testing, web"),
    ("tools-labs","PayloadsAllTheThings","https://github.com/swisskyrepo/PayloadsAllTheThings","GitHub","documentation","intermediate","payloads, web, xss, sqli"),
    ("tools-labs","HackTricks","https://book.hacktricks.xyz/","HackTricks","documentation","intermediate","pentest, red team, reference"),
    ("tools-labs","GTFOBins","https://gtfobins.github.io/","GTFOBins","documentation","intermediate","linux, privesc, suid"),
    ("tools-labs","LOLBAS","https://lolbas-project.github.io/","LOLBAS","documentation","intermediate","windows, lolbins, evasion"),
    ("tools-labs","SecLists","https://github.com/danielmiessler/SecLists","GitHub","documentation","beginner","wordlists, fuzzing"),
    ("tools-labs","LiveOverflow YouTube","https://www.youtube.com/@LiveOverflow","YouTube","video","intermediate","ctf, reversing, web"),
    ("tools-labs","IppSec YouTube (HTB writeups)","https://www.youtube.com/@ippsec","YouTube","video","intermediate","htb, walkthroughs"),
    ("tools-labs","John Hammond YouTube","https://www.youtube.com/@_JohnHammond","YouTube","video","beginner","ctf, malware, tools"),
    ("tools-labs","NetworkChuck - learn hacking","https://www.youtube.com/@NetworkChuck","YouTube","video","beginner","networking, hacking, fun"),
    ("tools-labs","osquery documentation","https://osquery.readthedocs.io/","osquery","documentation","intermediate","edr, inventory, sql"),
    ("tools-labs","Velociraptor DFIR docs","https://docs.velociraptor.app/","Velociraptor","documentation","intermediate","dfir, forensics, hunting"),
    ("tools-labs","Have I Been Pwned","https://haveibeenpwned.com/","Troy Hunt","tool","beginner","breaches, passwords"),
    ("tools-labs","Shodan search engine docs","https://shodan.readthedocs.io/","Shodan","documentation","intermediate","recon, iot, internet scanning"),
    ("tools-labs","Splunk Security Content","https://github.com/splunk/security_content","GitHub","documentation","intermediate","detections, splunk, soc"),
]

# Filler topic/aspect pools per category -> realistic demo volume
FILLER = {
    "network-security": {
        "topics": ["TLS handshake deep dive", "DNS tunneling detection", "BGP hijacking case study",
                   "802.11 WPA3 analysis", "IDS evasion techniques", "Firewall rule auditing",
                   "Netflow anomaly detection", "VPN protocols compared", "Packet crafting with Scapy",
                   "Network segmentation strategies", "DDoS mitigation playbooks", "Zero Trust networking"],
        "sources": [("Packet Pushers", "https://packetpushers.net/"), ("NANOG mailing list", "https://www.nanog.org/"),
                    ("APNIC blog", "https://blog.apnic.net/")],
        "media": ["article", "article", "article", "podcast", "documentation"]},
    "web-security": {
        "topics": ["GraphQL authorization bypass", "JWT algorithm confusion", "CSP bypass techniques",
                   "Mass assignment vulnerabilities", "Race conditions in web apps", "DOM clobbering",
                   "Prototype pollution", "Cache poisoning", "WebSocket security", "SAML misconfigurations",
                   "OAuth redirect URI tricks", "IDOR hunting methodology"],
        "sources": [("PortSwigger Research", "https://portswigger.net/research"), ("Orange Tsai blog", "https://blog.orange.tw/"),
                    ("Assetnote blog", "https://www.assetnote.io/resources/research")],
        "media": ["article", "article", "cheatsheet", "lab"]},
    "cloud-security": {
        "topics": ["IAM privilege escalation paths", "S3 bucket misconfigurations", "Lambda injection pitfalls",
                   "Kubernetes RBAC hardening", "Container escape case studies", "Azure AD attack paths",
                   "GCP service account abuse", "Secrets management patterns", "CloudTrail forensics",
                   "Serverless security checklist", "IaC scanning with Checkov", "Metadata service attacks"],
        "sources": [("Rhino Security Labs blog", "https://rhinosecuritylabs.com/blog/"), ("Wiz blog", "https://www.wiz.io/blog"),
                    ("Sysdig blog", "https://sysdig.com/blog/")],
        "media": ["article", "article", "documentation", "cheatsheet"]},
    "cryptography": {
        "topics": ["Padding oracle attacks explained", "RSA fault injection", "ECDSA nonce reuse",
                   "AES-GCM nonce misuse", "Homomorphic encryption primer", "Post-quantum migration",
                   "Password hashing at scale", "HSM operational practices", "Side-channel basics",
                   "Certificate transparency monitoring", "Threshold signatures", "ZK-SNARK intuition"],
        "sources": [("Cryptography Engineering blog", "https://blog.cryptographyengineering.com/"),
                    ("Cloudflare crypto blog", "https://blog.cloudflare.com/tag/crypto/"),
                    ("Trail of Bits crypto", "https://blog.trailofbits.com/")],
        "media": ["article", "article", "documentation", "lab"]},
    "certification-prep": {
        "topics": ["Security+ practice exam walkthrough", "CISSP domain 5 deep dive", "OSCP lab strategy",
                   "CEH v13 module review", "CISM governance crash course", "CompTIA CySA+ study plan",
                   "CCSP cloud cert guide", "eJPT exam experience", "PNPT review and tips",
                   "AWS Security Specialty notes", "AZ-500 study checklist", "SC-100 architecture prep"],
        "sources": [("ExamCompass", "https://www.examcompass.com/"), ("Certification Station (Medium)", "https://medium.com/tag/certification"),
                    ("Destination Certification", "https://www.destinationcertification.com/")],
        "media": ["article", "video", "cheatsheet", "course"]},
    "threat-intel": {
        "topics": ["Ransomware group TTP roundup", "Phishing kit teardown", "C2 infrastructure tracking",
                   "Supply chain compromise analysis", "Loader malware evolution", "Living-off-the-land review",
                   "ICS threat landscape", "Android spyware analysis", "Initial access broker trends",
                   "CVE exploitation in the wild", "Darkweb market monitoring", "State-sponsored campaign review"],
        "sources": [("The Record", "https://therecord.media/"), ("SecurityWeek", "https://www.securityweek.com/"),
                    ("Sophos X-Ops", "https://news.sophos.com/en-us/category/threat-research/")],
        "media": ["article", "article", "article", "podcast"]},
    "career-guides": {
        "topics": ["From helpdesk to SOC analyst", "Building a home lab on a budget", "Security portfolio projects",
                   "Interview questions: blue team", "Interview questions: red team", "Certification ROI analysis",
                   "Cybersecurity degree vs certifications", "Freelancing in security", "Mentorship in infosec",
                   "Salary negotiation playbook", "First 90 days as a SOC analyst", "Transitioning from development"],
        "sources": [("SimplyCyber", "https://www.simplycyber.io/"), ("StationX blog", "https://www.stationx.net/blog/"),
                    ("InfoSec Pat Medium", "https://medium.com/tag/cybersecurity")],
        "media": ["article", "video", "article", "podcast"]},
    "tools-labs": {
        "topics": ["BloodHound attack path analysis", "CrackMapExec practical guide", "Ghidra reverse engineering basics",
                   "Frida instrumentation workshop", "Nuclei template writing", "Impacket lateral movement",
                   "Chisel pivoting deep dive", "Wireshark filters for IR", "Volatility memory forensics",
                   "Hashcat rule-based attacks", "Cobalt Strike C2 tradecraft", "Semgrep SAST pipelines"],
        "sources": [("0xdf hacks stuff", "https://0xdf.gitlab.io/"), ("HackTricks news", "https://news.hacktricks.xyz/"),
                    ("Pentest Diary", "https://pentestdiary.blogspot.com/")],
        "media": ["article", "lab", "video", "documentation"]},
}

DIFFICULTIES = ["beginner", "beginner", "intermediate", "intermediate", "advanced"]
MEDIA_READ = {"article": 8, "video": 18, "documentation": 12, "course": 45, "lab": 30,
              "podcast": 40, "cheatsheet": 5, "tool": 3, "book": 120}


def _random_date(rng: random.Random):
    """15% of items fall in the last 7 days (feeds the weekly newsletter)."""
    if rng.random() < 0.15:
        days_ago = rng.randint(0, 6)
    else:
        days_ago = rng.randint(7, 364)
    d = dt.date.today() - dt.timedelta(days=days_ago)
    return d.isoformat(), d.strftime("%G-W%V")


def _mk_summary(title, cat_slug, source, media):
    return (f"{title} -- curated {media} resource on "
            f"{CAT_NAMES[cat_slug].lower()}, from {source}.")


def build_seed(total: int = 600, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    items, seen_urls = [], set()

    for cat, title, url, source, media, diff, tags in CURATED:
        day, week = _random_date(rng)
        items.append({
            "title": title, "url": url, "source": source,
            "source_domain": url.split("/")[2].replace("www.", ""),
            "author": "", "summary": _mk_summary(title, cat, source, media),
            "category": cat, "media_type": media, "difficulty": diff,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "published_at": day, "published_day": day, "week": week,
            "read_time_min": MEDIA_READ.get(media, 10),
            "bookmark_count": rng.randint(0, 40),
            "origin": "curated",
        })
        seen_urls.add(url)

    # ---- filler ----
    per_cat = (total - len(items)) // len(CATEGORIES) + 1
    n = 0
    for cat, cfg in FILLER.items():
        topics = cfg["topics"]
        for i in range(per_cat):
            topic = topics[i % len(topics)]
            variant = i // len(topics)  # 2nd pass => "Part 2", etc.
            title = f"{topic}" if variant == 0 else f"{topic}, Part {variant + 1}"
            src_name, src_base = cfg["sources"][i % len(cfg["sources"])]
            slug = "".join(c if c.isalnum() else "-" for c in title.lower()).strip("-")[:60]
            url = f"{src_base.rstrip('/')}/{slug}-{rng.randint(1000,9999)}"
            if url in seen_urls:
                continue
            seen_urls.add(url)
            media = cfg["media"][i % len(cfg["media"])]
            day, week = _random_date(rng)
            items.append({
                "title": title, "url": url, "source": src_name,
                "source_domain": src_base.split("/")[2].replace("www.", ""),
                "author": "", "summary": _mk_summary(title, cat, src_name, media),
                "category": cat, "media_type": media,
                "difficulty": DIFFICULTIES[rng.randrange(len(DIFFICULTIES))],
                "tags": [t for t in topic.lower().replace(",", "").split() if len(t) > 3][:5],
                "published_at": day, "published_day": day, "week": week,
                "read_time_min": MEDIA_READ.get(media, 10),
                "bookmark_count": rng.randint(0, 40),
                "origin": "generated-demo",
            })
            n += 1
    rng.shuffle(items)
    return items[:total]