"""SecStack seed dataset with authoritative canonical 15 cybersecurity taxonomy.
"""

import random
import datetime as dt

CATEGORIES = [
    {
        "slug": "threat-intelligence",
        "name": "Threat Intelligence & Vulnerability Research",
        "color": "#ff6b1a",
        "description": "CVE advisories, vulnerability disclosures, exploits, threat actors, TTPs, ransomware, zero-days, APTs.",
        "major_domain": "Threat & Vulnerability"
    },
    {
        "slug": "network-security",
        "name": "Network Security",
        "color": "#00f0ff",
        "description": "Protocols, traffic analysis, firewalls, DNS security, routing and perimeter defense.",
        "major_domain": "Network & Infrastructure"
    },
    {
        "slug": "web-security",
        "name": "Application & Web Security",
        "color": "#ff2d95",
        "description": "OWASP Top 10, SQL injection, XSS, CSRF, auth flaws, API security and WAFs.",
        "major_domain": "Application & Cloud"
    },
    {
        "slug": "cloud-security",
        "name": "Cloud Security",
        "color": "#7c3aed",
        "description": "AWS/Azure/GCP hardening, IAM policies, containers, Kubernetes and serverless security.",
        "major_domain": "Application & Cloud"
    },
    {
        "slug": "cryptography",
        "name": "Cryptography",
        "color": "#facc15",
        "description": "Encryption, key management, TLS/SSL, PKI, hashing, digital signatures and post-quantum crypto.",
        "major_domain": "Identity & Access"
    },
    {
        "slug": "endpoint-malware-analysis",
        "name": "Endpoint & Malware Analysis",
        "color": "#38bdf8",
        "description": "EDR/AV, malware reverse engineering, spyware, trojans, ransomware analysis and sandboxing.",
        "major_domain": "Threat & Vulnerability"
    },
    {
        "slug": "iam",
        "name": "Identity & Access Management (IAM)",
        "color": "#a855f7",
        "description": "Authentication, authorization, SSO, MFA, PAM, identity governance and zero trust.",
        "major_domain": "Identity & Access"
    },
    {
        "slug": "incident-response",
        "name": "Incident Response & Digital Forensics",
        "color": "#fb7185",
        "description": "Incident handling, evidence collection, memory forensics, log analysis and investigation.",
        "major_domain": "Operations & Response"
    },
    {
        "slug": "grc",
        "name": "Governance, Risk & Compliance (GRC)",
        "color": "#34d399",
        "description": "Security policies, risk assessment, ISO 27001, NIST CSF, GDPR, PCI-DSS and audits.",
        "major_domain": "Governance & Compliance"
    },
    {
        "slug": "security-operations",
        "name": "Security Operations (SOC)",
        "color": "#60a5fa",
        "description": "SIEM, alert triage, detection engineering, SOC workflows and security monitoring.",
        "major_domain": "Operations & Response"
    },
    {
        "slug": "ot-ics-security",
        "name": "OT/ICS Security",
        "color": "#fbbf24",
        "description": "SCADA, PLCs, industrial protocols, industrial control systems and critical infrastructure.",
        "major_domain": "Network & Infrastructure"
    },
    {
        "slug": "career-certification",
        "name": "Career & Certification",
        "color": "#4f8ef7",
        "description": "Career guides, CISSP/CEH/OSCP preparation, learning roadmaps and skills development.",
        "major_domain": "Career & Learning"
    },
    {
        "slug": "security-awareness",
        "name": "Security Awareness & Human Factors",
        "color": "#f472b6",
        "description": "Phishing, social engineering, insider threats, security awareness and human risk.",
        "major_domain": "Governance & Compliance"
    },
    {
        "slug": "ai-security",
        "name": "AI Security",
        "color": "#c084fc",
        "description": "Adversarial ML, deepfakes, LLM security, prompt injection, AI red teaming and model security.",
        "major_domain": "AI & Emerging Tech"
    },
    {
        "slug": "tools-labs",
        "name": "Tools & Labs",
        "color": "#e879f9",
        "description": "Hands-on platforms, CTFs, tool documentation and practice ranges.",
        "major_domain": "Career & Learning"
    },
]

CAT_COLORS = {c["slug"]: c["color"] for c in CATEGORIES}
CAT_NAMES = {c["slug"]: c["name"] for c in CATEGORIES}

ALIASES = {
    "threat-intel": "threat-intelligence",
    "threat_intel": "threat-intelligence",
    "threat-intelligence": "threat-intelligence",
    "certification-prep": "career-certification",
    "career-guides": "career-certification",
    "career_guides": "career-certification",
    "tools-labs": "tools-labs",
    "tools_labs": "tools-labs",
    "network-security": "network-security",
    "web-security": "web-security",
    "cloud-security": "cloud-security",
    "cryptography": "cryptography",
    "endpoint-malware-analysis": "endpoint-malware-analysis",
    "iam": "iam",
    "incident-response": "incident-response",
    "grc": "grc",
    "security-operations": "security-operations",
    "ot-ics-security": "ot-ics-security",
    "security-awareness": "security-awareness",
    "ai-security": "ai-security",
}

def normalize_category(cat: str) -> str:
    if not cat:
        return "threat-intelligence"
    key = cat.strip().lower()
    return ALIASES.get(key, key if key in CAT_NAMES else "threat-intelligence")

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
    # ---------- career-certification ----------
    ("career-certification","Professor Messer - Security+ SY0-701","https://www.professormesser.com/security-plus/sy0-701/sy0-701-video/","Professor Messer","video","beginner","comptia, security+, free"),
    ("career-certification","Professor Messer - Network+ N10-009","https://www.professormesser.com/network-plus/n10-009/n10-009-video/","Professor Messer","video","beginner","comptia, network+"),
    ("career-certification","CompTIA Security+ SY0-701 exam objectives (PDF)","https://www.comptia.org/certifications/security","CompTIA","documentation","beginner","comptia, exam objectives"),
    ("career-certification","ISC2 Certified in Cybersecurity - free course & exam","https://www.isc2.org/landing/1mcc","ISC2","course","beginner","isc2, cc, entry level"),
    ("career-certification","CISSP study resources (ISC2)","https://www.isc2.org/certifications/cissp","ISC2","documentation","advanced","cissp, isc2, domains"),
    ("career-certification","OffSec OSCP certification","https://www.offsec.com/courses/pen-200/","OffSec","course","advanced","oscp, pentest, lab"),
    ("career-certification","EC-Council CEH program","https://www.eccouncil.org/train-certify/certified-ethical-hacker-ceh/","EC-Council","course","intermediate","ceh, ethical hacking"),
    ("career-certification","Microsoft SC-200 security operations study path","https://learn.microsoft.com/en-us/credentials/certifications/security-operations-analyst-associate/","Microsoft Learn","course","intermediate","azure, sentinel, soc"),
    ("career-certification","ExamTopics SY0-701 practice discussions","https://www.examtopics.com/exams/comptia/sy0-701/","ExamTopics","article","intermediate","practice questions, comptia"),
    ("career-certification","Cybrary free courses","https://www.cybrary.it/","Cybrary","course","beginner","free, multiple vendors"),
    ("career-certification","r/cybersecurity wiki - getting started","https://www.reddit.com/r/cybersecurity/wiki/index/","Reddit","article","beginner","roadmap, community, faq"),
    ("career-certification","TCM Security - affordable training","https://tcm-sec.com/","TCM Security","course","beginner","pnpt, affordable, practical"),
    # ---------- threat-intelligence ----------
    ("threat-intelligence","MITRE ATT&CK knowledge base","https://attack.mitre.org/","MITRE","documentation","intermediate","apt, tactics, techniques"),
    ("threat-intelligence","MITRE D3FEND","https://d3fend.mitre.org/","MITRE","documentation","intermediate","detection, countermeasures"),
    ("threat-intelligence","Krebs on Security","https://krebsonsecurity.com/","Brian Krebs","article","intermediate","investigations, breaches"),
    ("threat-intelligence","The Hacker News","https://thehackernews.com/","The Hacker News","article","beginner","news, vulnerabilities"),
    ("threat-intelligence","BleepingComputer","https://www.bleepingcomputer.com/","BleepingComputer","article","beginner","news, ransomware, malware"),
    ("threat-intelligence","Dark Reading","https://www.darkreading.com/","Dark Reading","article","intermediate","news, analysis"),
    ("threat-intelligence","Google Project Zero","https://googleprojectzero.blogspot.com/","Google Project Zero","article","advanced","0day, vuln research"),
    ("threat-intelligence","Microsoft Security Response Center","https://msrc.microsoft.com/blog","MSRC","article","intermediate","vulns, advisories"),
    ("threat-intelligence","CISA known exploited vulnerabilities catalog","https://www.cisa.gov/known-exploited-vulnerabilities-catalog","CISA","documentation","intermediate","cve, kev, patching"),
    ("threat-intelligence","NVD - National Vulnerability Database","https://nvd.nist.gov/","NIST","documentation","intermediate","cve, scoring"),
    ("threat-intelligence","SANS Internet Storm Center","https://isc.sans.edu/","SANS ISC","article","intermediate","diaries, sensors, trends"),
    ("threat-intelligence","Mandiant M-Trends report","https://www.mandiant.com/resources/m-trends","Mandiant","article","intermediate","apt, ir, metrics"),
    ("threat-intelligence","Unit 42 threat research","https://unit42.paloaltonetworks.com/","Palo Alto Unit 42","article","intermediate","apt, malware"),
    ("threat-intelligence","VirusTotal blog","https://blog.virustotal.com/","VirusTotal","article","intermediate","malware, hunting"),
    ("threat-intelligence","YARA documentation","https://yara.readthedocs.io/","YARA","documentation","intermediate","yara, detection, malware"),
    ("threat-intelligence","Sigma rule format specification","https://sigmahq.io/docs/basics/rules.html","SigmaHQ","documentation","intermediate","sigma, detection, siem"),
    ("threat-intelligence","Atomic Red Team","https://github.com/redcanaryco/atomic-red-team","Red Canary","documentation","intermediate","mitre, emulation, detection"),
    # ---------- endpoint-malware-analysis ----------
    ("endpoint-malware-analysis","VirusTotal documentation","https://docs.virustotal.com/","VirusTotal","documentation","intermediate","vt, api, analysis"),
    ("endpoint-malware-analysis","Mandiant FLARE team blog","https://www.mandiant.com/resources/blog/flare-team","Mandiant","article","advanced","reversing, malware, flare"),
    ("endpoint-malware-analysis","CyberChef - the Cyber Swiss Army Knife","https://gchq.github.io/CyberChef/","GCHQ","tool","beginner","decoding, crypto, analysis"),
    # ---------- iam ----------
    ("iam","OWASP Authentication Cheat Sheet","https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html","OWASP","cheatsheet","intermediate","auth, passwords, mfa"),
    ("iam","NIST Digital Identity Guidelines (SP 800-63)","https://pages.nist.gov/800-63-3/","NIST","documentation","advanced","identity, guidelines, nist"),
    # ---------- incident-response ----------
    ("incident-response","SANS DFIR Cheat Sheets","https://www.sans.org/poster/category/dfir","SANS","cheatsheet","intermediate","dfir, forensics, IR"),
    ("incident-response","Autopsy forensic browser docs","https://www.autopsy.com/support/documentation/","Autopsy","documentation","intermediate","disk, forensics, dfir"),
    # ---------- grc ----------
    ("grc","NIST Cybersecurity Framework (CSF 2.0)","https://www.nist.gov/cyberframework","NIST","documentation","intermediate","csf, governance, risk"),
    ("grc","ISO/IEC 27001 standard overview","https://www.iso.org/isoiec-27001-information-security.html","ISO","documentation","advanced","iso27001, compliance"),
    # ---------- security-operations ----------
    ("security-operations","Elastic Security documentation","https://www.elastic.co/guide/en/security/current/index.html","Elastic","documentation","intermediate","siem, detection, ecs"),
    ("security-operations","SOC Analysts Handbook","https://www.sans.org/reading-room/","SANS","article","intermediate","soc, triage, monitoring"),
    # ---------- ot-ics-security ----------
    ("ot-ics-security","CISA ICS advisories","https://www.cisa.gov/news-events/cybersecurity-advisories","CISA","documentation","intermediate","ics, scada, ot"),
    ("ot-ics-security","SANS ICS security resources","https://www.sans.org/ics-security/","SANS ICS","documentation","advanced","ics, scada, grid"),
    # ---------- security-awareness ----------
    ("security-awareness","SANS OUCH! Security Awareness Newsletter","https://www.sans.org/security-awareness-training/ouch-newsletter","SANS","article","beginner","awareness, phishing"),
    # ---------- ai-security ----------
    ("ai-security","OWASP Top 10 for Large Language Model Applications","https://owasp.org/www-project-top-10-for-large-language-model-applications/","OWASP","documentation","intermediate","ai, llm, prompt injection"),
    ("ai-security","NIST AI Risk Management Framework","https://www.nist.gov/itl/ai-risk-management-framework","NIST","documentation","advanced","ai, rmf, governance"),
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
    ("tools-labs","Have I Been Pwned","https://haveibeenpwned.com/","Troy Hunt","tool","beginner","breaches, passwords"),
    ("tools-labs","Shodan search engine docs","https://shodan.readthedocs.io/","Shodan","documentation","intermediate","recon, iot, internet scanning"),
]

FILLER = {
    "network-security": {
        "topics": ["TLS handshake deep dive", "DNS tunneling detection", "BGP hijacking case study",
                   "802.11 WPA3 analysis", "IDS evasion techniques", "Firewall rule auditing"],
        "sources": [("Packet Pushers", "https://packetpushers.net/"), ("APNIC blog", "https://blog.apnic.net/")],
        "media": ["article", "documentation"]},
    "web-security": {
        "topics": ["GraphQL authorization bypass", "JWT algorithm confusion", "CSP bypass techniques",
                   "Mass assignment vulnerabilities", "Race conditions in web apps", "DOM clobbering"],
        "sources": [("PortSwigger Research", "https://portswigger.net/research"), ("Assetnote blog", "https://www.assetnote.io/")],
        "media": ["article", "cheatsheet", "lab"]},
    "cloud-security": {
        "topics": ["IAM privilege escalation paths", "S3 bucket misconfigurations", "Lambda injection pitfalls",
                   "Kubernetes RBAC hardening", "Container escape case studies", "Azure AD attack paths"],
        "sources": [("Rhino Security Labs", "https://rhinosecuritylabs.com/"), ("Wiz blog", "https://www.wiz.io/")],
        "media": ["article", "documentation"]},
    "cryptography": {
        "topics": ["Padding oracle attacks explained", "RSA fault injection", "ECDSA nonce reuse",
                   "AES-GCM nonce misuse", "Post-quantum migration", "Password hashing at scale"],
        "sources": [("Cloudflare crypto", "https://blog.cloudflare.com/"), ("Trail of Bits", "https://blog.trailofbits.com/")],
        "media": ["article", "documentation"]},
    "career-certification": {
        "topics": ["Security+ exam walkthrough", "CISSP domain review", "OSCP lab strategy",
                   "CEH module review", "CISM governance crash course", "CompTIA CySA+ study plan"],
        "sources": [("ExamCompass", "https://www.examcompass.com/"), ("Destination Certification", "https://www.destinationcertification.com/")],
        "media": ["article", "video", "cheatsheet"]},
    "threat-intelligence": {
        "topics": ["Ransomware group TTP roundup", "Phishing kit teardown", "C2 infrastructure tracking",
                   "Supply chain compromise analysis", "Loader malware evolution", "Living-off-the-land review"],
        "sources": [("The Record", "https://therecord.media/"), ("SecurityWeek", "https://www.securityweek.com/")],
        "media": ["article", "podcast"]},
    "endpoint-malware-analysis": {
        "topics": ["Malware unpacking techniques", "YARA rule tuning", "Memory dump analysis",
                   "Ransomware encryption routines", "Packed executable heuristics", "Debugger evasion detection"],
        "sources": [("Mandiant Blog", "https://www.mandiant.com/"), ("VirusTotal", "https://blog.virustotal.com/")],
        "media": ["article", "documentation"]},
    "iam": {
        "topics": ["OAuth 2.1 updates", "Passkeys enterprise rollout", "MFA fatigue attacks",
                   "Zero trust identity architecture", "Federated identity risks", "Machine identity secrets"],
        "sources": [("Auth0 Blog", "https://auth0.com/blog/"), ("Microsoft Identity", "https://techcommunity.microsoft.com/")],
        "media": ["article", "cheatsheet"]},
    "incident-response": {
        "topics": ["Memory forensics with Volatility", "Triage timeline analysis", "Cloud incident containment",
                   "Log artifact preservation", "IR playbook automation", "Malware artifact recovery"],
        "sources": [("SANS DFIR", "https://www.sans.org/"), ("DFIR Divas", "https://dfirdivas.com/")],
        "media": ["article", "documentation"]},
    "grc": {
        "topics": ["NIST CSF 2.0 transition", "ISO 27001 audit preparation", "GDPR compliance checks",
                   "Third-party risk management", "PCI-DSS v4.0 requirements", "Security metrics reporting"],
        "sources": [("ISACA Journal", "https://www.isaca.org/"), ("NIST News", "https://www.nist.gov/")],
        "media": ["article", "documentation"]},
    "security-operations": {
        "topics": ["SIEM alert tuning", "SOC metrics and KPIs", "EDR triage workflow",
                   "Threat hunting hypotheses", "Automation with SOAR", "Incident post-mortem analysis"],
        "sources": [("Elastic Security", "https://www.elastic.co/"), ("Splunk Security", "https://www.splunk.com/")],
        "media": ["article", "documentation"]},
    "ot-ics-security": {
        "topics": ["SCADA network hardening", "Modbus protocol security", "PLC firmware verification",
                   "Critical infrastructure monitoring", "ICS incident response", "Industrial firewall tuning"],
        "sources": [("Dragos Blog", "https://www.dragos.com/"), ("CISA ICS", "https://www.cisa.gov/")],
        "media": ["article", "documentation"]},
    "security-awareness": {
        "topics": ["Phishing simulation metrics", "Social engineering trends", "Insider threat awareness",
                   "Security training gamification", "Human risk management", "Password hygiene campaigns"],
        "sources": [("SANS Security Awareness", "https://www.sans.org/"), ("KnowBe4 Blog", "https://blog.knowbe4.com/")],
        "media": ["article", "video"]},
    "ai-security": {
        "topics": ["LLM prompt injection defense", "Adversarial machine learning", "AI red teaming frameworks",
                   "Model extraction attacks", "Data poisoning in training sets", "AI governance frameworks"],
        "sources": [("OpenAI Research", "https://openai.com/research/"), ("Anthropic Research", "https://anthropic.com/research/")],
        "media": ["article", "documentation"]},
    "tools-labs": {
        "topics": ["BloodHound enterprise analysis", "Ghidra reverse engineering", "Nuclei template writing",
                   "Impacket lateral movement", "Volatility memory forensics", "Hashcat rule tuning"],
        "sources": [("HackTricks", "https://book.hacktricks.xyz/"), ("0xdf hacks stuff", "https://0xdf.gitlab.io/")],
        "media": ["article", "lab"]},
}

DIFFICULTIES = ["beginner", "beginner", "intermediate", "intermediate", "advanced"]
MEDIA_READ = {"article": 8, "video": 18, "documentation": 12, "course": 45, "lab": 30,
              "podcast": 40, "cheatsheet": 5, "tool": 3, "book": 120}


def _random_date(rng: random.Random):
    if rng.random() < 0.15:
        days_ago = rng.randint(0, 6)
    else:
        days_ago = rng.randint(7, 364)
    d = dt.date.today() - dt.timedelta(days=days_ago)
    return d.isoformat(), d.strftime("%G-W%V")


def _mk_summary(title, cat_slug, source, media):
    cat_name = CAT_NAMES.get(cat_slug, cat_slug)
    return f"{title} -- curated {media} resource on {cat_name.lower()}, from {source}."


def build_seed(total: int = 750, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    items, seen_urls = [], set()

    for cat, title, url, source, media, diff, tags in CURATED:
        norm_cat = normalize_category(cat)
        day, week = _random_date(rng)
        items.append({
            "title": title, "url": url, "source": source,
            "source_domain": url.split("/")[2].replace("www.", ""),
            "author": "", "summary": _mk_summary(title, norm_cat, source, media),
            "category": norm_cat, "media_type": media, "difficulty": diff,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "published_at": day, "published_day": day, "week": week,
            "read_time_min": MEDIA_READ.get(media, 10),
            "bookmark_count": rng.randint(0, 40),
            "origin": "curated",
        })
        seen_urls.add(url)

    cat_slugs = list(FILLER.keys())
    idx = 0
    while len(items) < total:
        cat = rng.choice(cat_slugs)
        pool = FILLER[cat]
        topic = rng.choice(pool["topics"])
        src_name, src_url = rng.choice(pool["sources"])
        media = rng.choice(pool["media"])
        diff = rng.choice(DIFFICULTIES)
        idx += 1
        title = f"{topic} #{idx} ({src_name})"
        base_domain = src_url.split("/")[2] if len(src_url.split("/")) > 2 else "secstack.internal"
        url = f"{src_url.rstrip('/')}/item-{idx}-{abs(hash(title))}"
        if url in seen_urls:
            continue
        seen_urls.add(url)
        day, week = _random_date(rng)
        items.append({
            "title": title, "url": url, "source": src_name,
            "source_domain": base_domain.replace("www.", ""),
            "author": "", "summary": _mk_summary(title, cat, src_name, media),
            "category": cat, "media_type": media, "difficulty": diff,
            "tags": [w for w in topic.lower().split() if len(w) > 4][:4],
            "published_at": day, "published_day": day, "week": week,
            "read_time_min": MEDIA_READ.get(media, 10),
            "bookmark_count": rng.randint(0, 25),
            "origin": "filler",
        })
    return items
