import feedparser

FEEDS = [
    ("https://krebsonsecurity.com/feed/", "threat-intel", "Krebs on Security", "krebsonsecurity.com"),
    ("https://feeds.feedburner.com/TheHackersNews", "threat-intel", "The Hacker News", "thehackernews.com"),
    ("https://www.bleepingcomputer.com/feed/", "threat-intel", "BleepingComputer", "bleepingcomputer.com"),
    ("https://www.schneier.com/feed/atom/", "cryptography", "Schneier on Security", "schneier.com"),
    ("https://portswigger.net/research/rss", "web-security", "PortSwigger Research", "portswigger.net"),
    ("https://aws.amazon.com/blogs/security/feed/", "cloud-security", "AWS Security Blog", "aws.amazon.com"),
    ("https://isc.sans.edu/rssfeed.xml", "network-security", "SANS Internet Storm Center", "isc.sans.edu"),
    ("https://www.darkreading.com/rss.xml", "threat-intel", "Dark Reading", "darkreading.com"),
    ("https://www.securityweek.com/feed/", "threat-intel", "SecurityWeek", "securityweek.com"),
    ("https://feeds.feedburner.com/GoogleOnlineSecurityBlog", "cloud-security", "Google Online Security Blog", "google.com"),
    ("https://www.microsoft.com/en-us/security/blog/feed/", "enterprise-security", "Microsoft Security Blog", "microsoft.com"),
    ("https://blog.talosintelligence.com/feed/", "threat-intel", "Cisco Talos Intelligence", "talosintelligence.com"),
    ("https://unit42.paloaltonetworks.com/feed/", "threat-intel", "Palo Alto Networks Unit 42", "paloaltonetworks.com"),
    ("https://www.sentinelone.com/labs/feed/", "malware-analysis", "SentinelOne Labs", "sentinelone.com"),
    ("https://www.crowdstrike.com/blog/feed/", "threat-intel", "CrowdStrike Blog", "crowdstrike.com"),
    ("https://blog.rapid7.com/rss/", "vulnerability-management", "Rapid7 Blog", "rapid7.com"),
    ("https://therecord.media/feed", "threat-intel", "The Record by Recorded Future", "therecord.media"),
    ("https://www.malwarebytes.com/blog/feed/", "malware-analysis", "Malwarebytes Labs", "malwarebytes.com"),
    ("https://www.tripwire.com/state-of-security/feed/", "enterprise-security", "Tripwire State of Security", "tripwire.com"),
    ("https://blog.qualys.com/feed/", "vulnerability-management", "Qualys Security Blog", "qualys.com"),
    ("https://www.cisa.gov/cybersecurity-advisories/all.xml", "vulnerability-management", "CISA Advisories", "cisa.gov"),
    ("https://www.helpnetsecurity.com/feed/", "threat-intel", "Help Net Security", "helpnetsecurity.com"),
    ("https://www.welivesecurity.com/feed/", "malware-analysis", "ESET WeLiveSecurity", "welivesecurity.com"),
    ("https://redcanary.com/blog/feed/", "red-canary", "Red Canary Blog", "redcanary.com"),
    ("https://www.troyhunt.com/rss/", "web-security", "Troy Hunt Blog", "troyhunt.com"),
]

def test_all():
    healthy = 0
    failing = 0
    for url, cat, name, domain in FEEDS:
        try:
            feed = feedparser.parse(url)
            entries = len(feed.entries)
            if entries > 0 or feed.get("feed", {}).get("title"):
                print(f"[OK] {name} ({domain}): {entries} entries")
                healthy += 1
            else:
                print(f"[WARN/EMPTY] {name} ({domain}): 0 entries")
                failing += 1
        except Exception as e:
            print(f"[FAIL] {name} ({domain}): {e}")
            failing += 1
    print(f"Total: {len(FEEDS)}, Healthy: {healthy}, Failing: {failing}")

if __name__ == "__main__":
    test_all()
