"""
Constants for Phishing Detection Backend
Includes trusted domains, keywords, and static configurations
"""

from typing import Dict, List, Set, Tuple

# =============================================================================
# HIGH TRUST DOMAINS (Tech Giants, Major Banks, Government)
# These domains have the highest trust score
# =============================================================================

HIGH_TRUST_DOMAINS: Set[str] = {
    # Tech Giants
    "google.com", "google.co.uk", "google.de", "google.fr", "google.es",
    "google.it", "google.ca", "google.com.au", "google.co.jp", "google.com.br",
    "google.co.in", "google.ru", "google.cn", "google.com.tw", "google.com.mx",
    "youtube.com", "gmail.com", "android.com", "chromium.org",
    "microsoft.com", "windows.com", "office.com", "azure.com", "live.com",
    "outlook.com", "bing.com", "linkedin.com", "github.com", "visualstudio.com",
    "apple.com", "icloud.com", "itunes.com",
    "amazon.com", "amazon.co.uk", "amazon.de", "amazon.fr", "amazon.co.jp",
    "amazon.ca", "amazon.com.au", "amazon.in", "aws.amazon.com", "amazonaws.com",
    "facebook.com", "fb.com", "instagram.com", "whatsapp.com", "messenger.com",
    "twitter.com", "x.com",
    "netflix.com", "spotify.com",
    "paypal.com", "ebay.com",
    "adobe.com", "salesforce.com", "oracle.com", "ibm.com", "cisco.com",
    "intel.com", "nvidia.com", "amd.com", "dell.com", "hp.com", "lenovo.com",
    "dropbox.com", "box.com", "zoom.us", "slack.com", "notion.so",
    "cloudflare.com", "fastly.com", "akamai.com",
    
    # Major Banks (Global)
    "chase.com", "bankofamerica.com", "wellsfargo.com", "citibank.com",
    "usbank.com", "capitalone.com", "pnc.com", "tdbank.com",
    "hsbc.com", "barclays.co.uk", "lloydsbank.com", "natwest.com",
    "deutschebank.de", "bnpparibas.com", "credit-agricole.fr",
    "santander.com", "ing.com", "ubs.com", "credit-suisse.com",
    
    # Major E-commerce
    "alibaba.com", "aliexpress.com", "taobao.com", "tmall.com", "jd.com",
    "ebay.com", "walmart.com", "target.com", "bestbuy.com",
    "shopify.com", "etsy.com", "rakuten.com", "flipkart.com",
    
    # News & Media
    "cnn.com", "bbc.com", "bbc.co.uk", "nytimes.com", "washingtonpost.com",
    "theguardian.com", "reuters.com", "bloomberg.com", "forbes.com",
    "wsj.com", "ft.com", "economist.com", "time.com", "newsweek.com",
    
    # Education
    "wikipedia.org", "wikimedia.org", "britannica.com",
    "coursera.org", "edx.org", "udemy.com", "khanacademy.org",
    "mit.edu", "stanford.edu", "harvard.edu", "berkeley.edu", "oxford.ac.uk",
}

# =============================================================================
# MEDIUM TRUST DOMAINS (Popular but smaller sites)
# =============================================================================

MEDIUM_TRUST_DOMAINS: Set[str] = {
    # Tech & Development
    "stackoverflow.com", "stackexchange.com", "reddit.com", "quora.com",
    "medium.com", "dev.to", "hackernews.com", "producthunt.com",
    "gitlab.com", "bitbucket.org", "sourceforge.net",
    "npmjs.com", "pypi.org", "rubygems.org", "packagist.org",
    "docker.com", "kubernetes.io", "terraform.io",
    
    # Communication
    "discord.com", "telegram.org", "signal.org", "skype.com",
    "viber.com", "wechat.com", "line.me",
    
    # Entertainment
    "twitch.tv", "vimeo.com", "dailymotion.com", "tiktok.com",
    "soundcloud.com", "bandcamp.com", "deezer.com",
    "imdb.com", "rottentomatoes.com", "metacritic.com",
    "steam.com", "epicgames.com", "ea.com", "ubisoft.com",
    
    # Utilities
    "weather.com", "accuweather.com",
    "indeed.com", "glassdoor.com", "monster.com",
    "airbnb.com", "booking.com", "expedia.com", "tripadvisor.com",
    "uber.com", "lyft.com",
    
    # Regional Popular Sites
    "baidu.com", "weibo.com", "qq.com", "163.com", "sohu.com",
    "naver.com", "daum.net", "yahoo.co.jp",
    "yandex.ru", "mail.ru", "vk.com",
}

# =============================================================================
# GOVERNMENT DOMAINS (High Trust)
# =============================================================================

GOVERNMENT_TLD_PATTERNS: Set[str] = {
    ".gov", ".gov.uk", ".gov.au", ".gov.ca", ".gov.in",
    ".gov.br", ".gov.cn", ".gov.jp", ".gov.de", ".gov.fr",
    ".mil", ".edu",
    ".sa.gov", ".mc.gov",  # Saudi Arabia government domains
}

# Specific government domains
GOVERNMENT_DOMAINS: Set[str] = {
    "usa.gov", "whitehouse.gov", "irs.gov", "ssa.gov",
    "gov.uk", "nhs.uk", "dwp.gov.uk",
    "service-public.fr", "gouvernement.fr",
    "bund.de", "bundesregierung.de",
    "gob.mx", "sat.gob.mx",
}

# =============================================================================
# TRUSTED KEYWORDS
# If URL contains these keywords in domain, add trust bonus
# =============================================================================

HIGH_TRUST_KEYWORDS: List[str] = [
    "google", "microsoft", "apple", "amazon", "facebook", "meta",
    "twitter", "netflix", "spotify", "paypal", "ebay",
    "github", "linkedin", "youtube", "instagram", "whatsapp",
]

MEDIUM_TRUST_KEYWORDS: List[str] = [
    "bank", "banking", "finance", "insurance",
    "gov", "government", "official",
    "edu", "university", "college", "school",
    "healthcare", "hospital", "medical", "health",
]

# Keywords that may indicate phishing when combined with legitimate brand names
SUSPICIOUS_KEYWORDS: List[str] = [
    "login", "signin", "sign-in", "account", "verify", "verification",
    "secure", "security", "update", "confirm", "validate",
    "suspended", "locked", "alert", "urgent", "warning",
    "password", "credential", "authenticate",
    "free", "prize", "winner", "congratulations", "gift",
    "limited", "expire", "act-now", "immediate",
]

# =============================================================================
# PHISHING INDICATORS
# =============================================================================

PHISHING_TLD_PATTERNS: Set[str] = {
    ".tk", ".ml", ".ga", ".cf", ".gq",  # Free domains often used for phishing
    ".xyz", ".top", ".work", ".click", ".link",
    ".loan", ".men", ".party", ".racing", ".review",
}

PHISHING_SUBSTRINGS: List[str] = [
    "login-", "-login", "signin-", "-signin",
    "account-", "-account", "secure-", "-secure",
    "verify-", "-verify", "update-", "-update",
    "confirm-", "-confirm", "support-", "-support",
    "help-", "-help", "service-", "-service",
]

# =============================================================================
# URL FEATURE THRESHOLDS
# =============================================================================

URL_THRESHOLDS: Dict[str, float] = {
    "max_safe_length": 100,
    "suspicious_length": 150,
    "dangerous_length": 200,
    "max_safe_subdomains": 3,
    "suspicious_subdomains": 5,
    "max_safe_digits_ratio": 0.3,
    "max_safe_special_chars_ratio": 0.2,
    "min_safe_entropy": 2.5,
    "max_safe_entropy": 4.5,
}

# =============================================================================
# TOP MILLION DOMAINS (Tranco List Categories)
# In production, this would be loaded from a file
# =============================================================================

TOP_1K_DOMAINS_SAMPLE: Set[str] = {
    # This is a sample - in production, load from tranco-list.eu
    "google.com", "youtube.com", "facebook.com", "twitter.com",
    "instagram.com", "linkedin.com", "wikipedia.org", "amazon.com",
    "apple.com", "microsoft.com", "netflix.com", "reddit.com",
    "yahoo.com", "tiktok.com", "live.com", "office.com",
    "zoom.us", "bing.com", "microsoftonline.com", "github.com",
}

# Trust levels mapping
TRUST_LEVELS: Dict[str, Tuple[float, str]] = {
    "highest": (1.0, "Verified trusted domain (Top global site)"),
    "high": (0.8, "Known trusted domain"),
    "medium": (0.5, "Popular domain with moderate trust"),
    "low": (0.2, "Unknown domain with basic trust"),
    "suspicious": (0.0, "Domain shows suspicious patterns"),
    "dangerous": (-0.5, "Domain matches known phishing patterns"),
}

# =============================================================================
# API RESPONSE CODES
# =============================================================================

class PhishingStatus:
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    PHISHING = "phishing"
    UNKNOWN = "unknown"

class RiskLevel:
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
