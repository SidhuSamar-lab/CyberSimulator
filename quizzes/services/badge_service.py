"""
CyberSimulator - Badge & Achievement Service.
Standardizes badge metadata, mastery criteria, and cadet military ranks across the platform.
"""
from typing import Dict, List, Any


class BadgeService:
    """Service for badge evaluation, ranking, and gamified achievements."""

    BADGE_DEFINITIONS: List[Dict[str, str]] = [
        {
            "id": "phishing",
            "title": "Phishing Hunter",
            "icon": "🎣",
            "material_icon": "mark_email_unread",
            "desc": "Master of spotting deceptive links & spoofed mail"
        },
        {
            "id": "otp_scams",
            "title": "OTP Sentinel",
            "icon": "🔑",
            "material_icon": "key",
            "desc": "Defends one-time verification codes against callers"
        },
        {
            "id": "fake_websites",
            "title": "Domain Sleuth",
            "icon": "🌐",
            "material_icon": "travel_explore",
            "desc": "Inspects SSL, typosquatting & fraudulent portals"
        },
        {
            "id": "cyberbullying",
            "title": "Anti-Harassment Shield",
            "icon": "🛡️",
            "material_icon": "favorite",
            "desc": "Champions digital kindness & evidence reporting"
        },
        {
            "id": "social_privacy",
            "title": "Privacy Guardian",
            "icon": "👁️",
            "material_icon": "visibility_off",
            "desc": "Controls geotagging, personal data & friend circles"
        },
        {
            "id": "qr_scams",
            "title": "Quishing Buster",
            "icon": "📱",
            "material_icon": "qr_code_scanner",
            "desc": "Detects tampered stickers & fraudulent QR codes"
        },
        {
            "id": "ai_misinformation",
            "title": "Deepfake Detective",
            "icon": "🤖",
            "material_icon": "psychology",
            "desc": "Uncovers synthetic voice clones & AI fakes"
        },
        {
            "id": "passwords_2fa",
            "title": "2FA Sentinel",
            "icon": "🔒",
            "material_icon": "phonelink_lock",
            "desc": "Master of strong passphrases and authenticators"
        },
    ]

    MASTERY_SCORE_THRESHOLD: int = 2  # At least 2/3 correct

    @classmethod
    def get_badge_definitions(cls) -> List[Dict[str, str]]:
        """Returns immutable list of all badge definitions."""
        return list(cls.BADGE_DEFINITIONS)

    @classmethod
    def get_rank_title(cls, completed_topics_count: int) -> str:
        """Determines cadet operational rank title from distinct completed topics."""
        if completed_topics_count >= 8:
            return "Master Cyber Defender"
        elif completed_topics_count >= 5:
            return "Security Specialist"
        elif completed_topics_count >= 2:
            return "Cyber Scout"
        elif completed_topics_count >= 1:
            return "Safety Apprentice"
        return "Digital Cadet"

    @classmethod
    def evaluate_badges_for_attempts(cls, attempts: Any) -> List[Dict[str, Any]]:
        """
        Evaluates which badges are earned from a collection/iterable of QuizAttempts.
        """
        passed_topics = set()
        for attempt in attempts:
            if getattr(attempt, 'score', 0) >= cls.MASTERY_SCORE_THRESHOLD:
                passed_topics.add(getattr(attempt, 'topic_id', ''))

        badges = []
        for b in cls.BADGE_DEFINITIONS:
            is_earned = b["id"] in passed_topics
            badges.append({
                **b,
                "earned": is_earned,
            })
        return badges
