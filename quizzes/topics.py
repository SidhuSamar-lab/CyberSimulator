"""
Definition of the 8 core cybersecurity awareness topics.
Each topic includes metadata for UI display, student guidance, and AI prompt context.
"""

CYBER_TOPICS = [
    {
        "id": "phishing",
        "title": "Phishing Scams",
        "tagline": "Spot deceptive emails, fake urgency, and dangerous links.",
        "icon": "shield-alert",
        "color": "rose",
        "description": "Learn to detect urgent emails claiming your account is banned, fake teacher messages, and spoofed website links designed to steal your credentials.",
        "key_concepts": [
            "Urgent call-to-action tactics",
            "Mismatched domain names and spoofed headers",
            "Malicious file attachments and hyperlinks",
        ],
    },
    {
        "id": "otp_scams",
        "title": "OTP & Verification Scams",
        "tagline": "Protect your one-time passwords from fraud callers and impostors.",
        "icon": "key-round",
        "color": "amber",
        "description": "Understand why legitimate banks, game platforms, and tech services NEVER ask for your SMS/WhatsApp One-Time Passwords over phone or chat.",
        "key_concepts": [
            "Never share OTPs with anyone",
            "Impersonation of bank officials or game mods",
            "SIM swap and social engineering tactics",
        ],
    },
    {
        "id": "fake_websites",
        "title": "Fake & Spoofed Websites",
        "tagline": "Inspect URLs, detect typo-squatting, and avoid counterfeit stores.",
        "icon": "globe",
        "color": "cyan",
        "description": "Identify fraudulent websites disguised as popular gaming stores, streaming sites, or school login portals that harvest passwords and credit cards.",
        "key_concepts": [
            "Checking URL spellings (e.g., paypa1.com vs paypal.com)",
            "SSL locks don't always mean trusted content",
            "Lookalike checkout forms and fake discount sites",
        ],
    },
    {
        "id": "cyberbullying",
        "title": "Cyberbullying & Online Safety",
        "tagline": "Handle toxic players, protect personal boundaries, and report safely.",
        "icon": "users",
        "color": "purple",
        "description": "Build safe online habits in gaming Discord servers, multiplayer lobbies, and class groups while knowing when and how to block, report, and seek help.",
        "key_concepts": [
            "Recognizing cyberbullying and harassment",
            "Preserving evidence (screenshots) and reporting",
            "Protecting friends and standing up against doxxing",
        ],
    },
    {
        "id": "social_privacy",
        "title": "Social Media Privacy",
        "tagline": "Control your digital footprint, geotags, and personal exposure.",
        "icon": "eye-off",
        "color": "indigo",
        "description": "Master privacy settings on Instagram, TikTok, and Snapchat. Prevent strangers from tracking your daily routine through location tags and public stories.",
        "key_concepts": [
            "Limiting profile visibility to verified friends",
            "Disabling precise location/geotagging on public posts",
            "Avoiding oversharing home, school, or routine details",
        ],
    },
    {
        "id": "qr_scams",
        "title": "QR Code Scams (Quishing)",
        "tagline": "Identify tampered stickers, parking meters, and payment traps.",
        "icon": "qr-code",
        "color": "emerald",
        "description": "Examine how attackers paste fraudulent QR codes over real signs in restaurants, public transport, or contest posters to redirect you to malware.",
        "key_concepts": [
            "Inspecting physical stickers covering real QR codes",
            "Previewing destination URLs before opening",
            "Verifying payment recipients on UPI / digital wallets",
        ],
    },
    {
        "id": "ai_misinformation",
        "title": "AI Misinformation & Deepfakes",
        "tagline": "Detect voice clones, synthetic media, and generative fakes.",
        "icon": "cpu",
        "color": "fuchsia",
        "description": "Learn to critically evaluate sensational AI-generated news videos, voice clones pretending to be relatives in distress, and deepfake imagery.",
        "key_concepts": [
            "Verifying viral news with trusted, primary sources",
            "Spotting deepfake video glitches and robotic voice cues",
            "Establishing a 'family codeword' for emergency phone calls",
        ],
    },
    {
        "id": "passwords_2fa",
        "title": "Password Security & 2FA",
        "tagline": "Build bulletproof passphrases and activate multi-factor defense.",
        "icon": "lock",
        "color": "blue",
        "description": "Discover why 'Password123' fails instantly, how to generate strong memorizable passphrases, and why Two-Factor Authentication stops 99% of account hacks.",
        "key_concepts": [
            "Using long multi-word passphrases over complex short words",
            "Never reusing identical passwords across accounts",
            "Enabling Authenticator Apps (2FA) on all core services",
        ],
    },
]

TOPICS_BY_ID = {topic["id"]: topic for topic in CYBER_TOPICS}


def get_topic_by_id(topic_id: str):
    """Retrieve topic metadata or return None."""
    return TOPICS_BY_ID.get(topic_id)
