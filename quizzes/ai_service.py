import json
import logging
import random
import re
import requests
from django.conf import settings
from .topics import get_topic_by_id

logger = logging.getLogger(__name__)


# High-quality scenario-based starter/fallback question pool for the 8 topics
# Tailored for Middle and High School students (ages 11-18)
FALLBACK_QUESTIONS = {
    "phishing": [
        {
            "question_text": "You receive an urgent email from 'School-Admin-Support' saying: 'Your student account will be deleted in 30 minutes! Click here immediately to verify your password.' What should you do?",
            "option_a": "Click the link immediately so you don't lose your homework files.",
            "option_b": "Reply to the email asking if this is a real message.",
            "option_c": "Do not click any links; report the email to your school IT teacher or staff.",
            "option_d": "Forward the email to all your classmates to warn them to click it too.",
            "correct_option": "C",
            "explanation": "Urgency and fear of account deletion are hallmark signs of phishing. Legitimate school administrators will never demand password verification through an urgent email link."
        },
        {
            "question_text": "While playing an online game, a stranger in chat messages you: 'Congrats! You won 5,000 free in-game currency! Just login at steam-giftcards-giveaway.xyz with your account to claim it.' What is the safest move?",
            "option_a": "Enter your login credentials quickly before the promo code expires.",
            "option_b": "Ignore the message and report the user for sending malicious phishing links.",
            "option_c": "Give them your friend's login details instead to test if it works.",
            "option_d": "Ask the user to send their password first to prove they are legit.",
            "correct_option": "B",
            "explanation": "Free currency giveaways on unofficial domains (.xyz, lookalike domains) are designed to steal your gaming accounts and inventory."
        },
        {
            "question_text": "You get a direct message on Instagram from an account with your friend's profile picture saying: 'Hey, I'm locked out of my account, can you tap this link to vote for my photo contest?' What should you do?",
            "option_a": "Tap the link and enter your phone number to help your friend.",
            "option_b": "Check with your friend through a different channel (in person or phone call) before clicking.",
            "option_c": "Share the link on your story to get more votes.",
            "option_d": "Send your password so they can vote from your account.",
            "correct_option": "B",
            "explanation": "Compromised accounts often send 'vote for my contest' links to hijack more accounts. Always verify independently with your friend."
        }
    ],
    "otp_scams": [
        {
            "question_text": "A caller claiming to be from your mobile network company says: 'We are upgrading your 5G tower. We just sent an SMS code to your phone. Read it aloud to us now or your SIM card will be deactivated.' What should you do?",
            "option_a": "Quickly read the numbers aloud so your phone keeps working.",
            "option_b": "Hang up immediately. Never share OTPs or verification codes with any caller.",
            "option_c": "Text the code to them instead of reading it out loud.",
            "option_d": "Ask them to hold while you share the code with a classmate.",
            "correct_option": "B",
            "explanation": "Service providers never ask for OTPs over calls. Sharing an SMS verification code allows attackers to hijack accounts or your SIM card."
        },
        {
            "question_text": "You are selling an old textbook online. A buyer messages: 'I want to send you money via digital wallet, but first you need to approve the request and enter your UPI PIN / OTP on the screen.' What is happening?",
            "option_a": "This is normal procedure for receiving payments.",
            "option_b": "This is a payment fraud trick; receiving money NEVER requires entering your PIN or sharing an OTP.",
            "option_c": "You should ask the buyer to double the amount first.",
            "option_d": "You must send the book before entering the PIN.",
            "correct_option": "B",
            "explanation": "You only enter a PIN or OTP when SENDING money, never when receiving money. Scammers use fake approval requests to drain balances."
        },
        {
            "question_text": "You receive an unsolicited WhatsApp message with an authentication code for an account you didn't touch, followed by a message from an unknown number: 'Sorry, I entered your number by mistake, please send me the 6-digit code!' What should you do?",
            "option_a": "Be polite and send them the 6-digit code.",
            "option_b": "Delete the message and ignore them; never share verification codes with anyone.",
            "option_c": "Call the number and give them only the first 3 digits.",
            "option_d": "Post the code online to see whose account it belongs to.",
            "correct_option": "B",
            "explanation": "An attacker is trying to log into YOUR account or reset your password. Sharing that code gives them complete access."
        }
    ],
    "fake_websites": [
        {
            "question_text": "You want to buy concert tickets and search on Google. Which of the following web addresses is the MOST suspicious?",
            "option_a": "https://www.ticketmaster.com/events",
            "option_b": "https://tickets.official-event-center.org",
            "option_c": "https://ticketmaster-cheap-tickets-claim.free-site.ru/login",
            "option_d": "https://support.ticketmaster.com/faq",
            "correct_option": "C",
            "explanation": "Notice the subdomains and abnormal top-level domain (.ru, .free-site). Attackers use lookalike prefixes to trick users into thinking it's the real domain."
        },
        {
            "question_text": "A website shows a green padlock icon next to its URL. Does this guarantee the website is 100% honest, safe, and not a scam?",
            "option_a": "Yes, the padlock means the business has been legally verified as honest.",
            "option_b": "No, the padlock only means the connection is encrypted (HTTPS); scammers can easily get SSL certificates too.",
            "option_c": "Yes, it means the government approved the site.",
            "option_d": "Yes, hackers cannot obtain padlocks.",
            "correct_option": "B",
            "explanation": "HTTPS encryption protects against eavesdropping in transit, but scammers can easily set up encrypted fake websites. Always verify the domain itself."
        },
        {
            "question_text": "You visit an online sneaker shop offering 90% off brand-new $200 sneakers. The site only accepts payment through direct gift card codes or wire transfer. What should you conclude?",
            "option_a": "It's an amazing clearance sale; buy multiple pairs before they sell out.",
            "option_b": "It is almost certainly a counterfeit or scam site trying to steal untraceable money.",
            "option_c": "The site is safe because it has flashy countdown timers.",
            "option_d": "You should enter your debit card info instead.",
            "correct_option": "B",
            "explanation": "Prices that are too good to be true and untraceable payment methods (gift cards, wire transfers, crypto) are classic indicators of fraudulent storefronts."
        }
    ],
    "cyberbullying": [
        {
            "question_text": "In a competitive online multiplayer game, a player starts repeatedly posting hurtful messages, personal insults, and threatening to leak another player's private photos. What is the most effective first response?",
            "option_a": "Insult them back with even worse language to show you are not afraid.",
            "option_b": "Mute, block, screenshot the abusive chat for evidence, and report them through the platform's moderation tools.",
            "option_c": "Give them your phone number to settle the dispute privately.",
            "option_d": "Delete your game account and never play online games again.",
            "correct_option": "B",
            "explanation": "Engaging or retaliating escalates harassment. Taking screenshots, blocking the abuser, and utilizing platform report tools protects your peace of mind and holds bullies accountable."
        },
        {
            "question_text": "Someone creates a fake Instagram account mocking a student in your school grade and posts embarrassing edited photos. What should you do?",
            "option_a": "Follow the account and share it with friends so everyone can laugh.",
            "option_b": "Comment on the posts encouraging the creator to post more.",
            "option_c": "Report the fake profile to Instagram for impersonation/harassment, support the targeted classmate, and inform a trusted teacher or school counselor.",
            "option_d": "Pretend you didn't see anything and stay silent.",
            "correct_option": "C",
            "explanation": "Being an active upstander by reporting abusive accounts and letting school staff know protects your peers and stops harassment campaigns."
        },
        {
            "question_text": "What does 'doxxing' mean in digital safety?",
            "option_a": "Playing a multiplayer match without wearing a gaming headset.",
            "option_b": "Publishing someone's private personal information (like home address, real name, or school) online with malicious intent.",
            "option_c": "Updating your antivirus software definitions.",
            "option_d": "Sending animated stickers in a group chat.",
            "correct_option": "B",
            "explanation": "Doxxing is the malicious release of private identifying details to intimidate or invite harassment against a victim."
        }
    ],
    "social_privacy": [
        {
            "question_text": "You are on a family vacation away from home for two weeks. When is the safest time to post public photos and tag your location?",
            "option_a": "The minute you arrive at the airport with live location tags.",
            "option_b": "Every morning detailing your daily schedule and when your hotel room is empty.",
            "option_c": "After you return home, or only in a private story restricted to trusted close friends.",
            "option_d": "Live-stream your empty house while traveling.",
            "correct_option": "C",
            "explanation": "Broadcasting live vacation photos and location tags alerts criminals that your home is vacant and tracks your physical movements."
        },
        {
            "question_text": "A popular social media trend asks you to answer: 'Your first pet name + mother's maiden name + high school mascot is your superhero name!' Why is participating in this risky?",
            "option_a": "It wastes too much battery power.",
            "option_b": "These answers are commonly used as security questions to reset passwords on your email and banking accounts.",
            "option_c": "The superhero name might not sound cool.",
            "option_d": "It violates social media photo formatting rules.",
            "correct_option": "B",
            "explanation": "Viral 'quiz' trends are frequently engineered by threat actors to harvest answers to common password recovery security questions."
        },
        {
            "question_text": "What is the recommended setting for your social media profile if you are a teenager?",
            "option_a": "Completely public so anyone worldwide can message you and view your stories.",
            "option_b": "Private account, only accepting follow requests from people you actually know in real life.",
            "option_c": "Public account with your school name, birthdate, and phone number in your bio.",
            "option_d": "Sharing your live GPS location with all app users.",
            "correct_option": "B",
            "explanation": "Setting accounts to private and vetting followers ensures strangers and predators cannot harvest your photos, daily routines, or contact details."
        }
    ],
    "qr_scams": [
        {
            "question_text": "At a public parking meter or restaurant table, you notice a paper QR code sticker is placed directly on top of the original printed code. What should you do?",
            "option_a": "Scan it immediately and proceed with paying.",
            "option_b": "Be highly suspicious of sticker tampering; inform the staff and use an official app or manual website instead.",
            "option_c": "Peel the sticker off and eat it.",
            "option_d": "Share the QR code image with all your contacts.",
            "correct_option": "B",
            "explanation": "Scammers place fake QR code stickers over genuine parking meters or menus to redirect users to credential-stealing or payment-harvesting malicious websites."
        },
        {
            "question_text": "When your smartphone camera scans a QR code, what should you always do before tapping 'Open Link'?",
            "option_a": "Close your eyes and tap as fast as possible.",
            "option_b": "Preview the full URL domain on your screen to ensure it points to the genuine, official website.",
            "option_c": "Turn off your Wi-Fi and bluetooth.",
            "option_d": "Enter your credit card number into the camera preview.",
            "correct_option": "B",
            "explanation": "Modern phone scanners show the destination URL preview. Always verify the domain spelling before allowing the browser to navigate."
        },
        {
            "question_text": "You see a flyer on a school bulletin board claiming: 'Scan this QR code to download an exclusive game cheat APK!' What is the primary danger?",
            "option_a": "Your phone's screen brightness will drop.",
            "option_b": "The QR code can trigger the download of malicious sideloaded APK software containing spyware or trojans.",
            "option_c": "The game developers will send you a gift card.",
            "option_d": "There is no danger with QR codes.",
            "correct_option": "B",
            "explanation": "Sideloading unverified APKs or executable files from random QR codes is a leading vector for mobile malware and keyloggers."
        }
    ],
    "ai_misinformation": [
        {
            "question_text": "You see a viral video on social media of a world leader announcing a sudden war outbreak. The lips look slightly blurry, and the voice sounds slightly robotic and monotonous. What should you do?",
            "option_a": "Panic and repost it immediately to all your group chats.",
            "option_b": "Cross-check major reputable news organizations and official government channels before sharing; it could be an AI deepfake.",
            "option_c": "Believe it because video cannot be manipulated.",
            "option_d": "Comment with your credit card info to support relief efforts.",
            "correct_option": "B",
            "explanation": "Generative AI can create convincing synthetic video and voice deepfakes. If a major world event is real, established global news agencies will verify and cover it."
        },
        {
            "question_text": "A grandparent receives a phone call with a voice that sounds exactly like their grandchild, crying and saying: 'I got in trouble, wire $1,000 immediately to this account!' What safety protocol helps protect against this AI voice clone scam?",
            "option_a": "Having an agreed family secret codeword to verify true identity in emergencies.",
            "option_b": "Immediately wiring the money without asking questions.",
            "option_c": "Posting about the call publicly.",
            "option_d": "Hanging up and never speaking to the grandchild again.",
            "correct_option": "A",
            "explanation": "AI voice cloning can replicate someone's voice from just a 5-second audio snippet. A pre-arranged family codeword stops voice impersonation fraud in its tracks."
        },
        {
            "question_text": "When an AI chatbot gives you an answer about a critical medical or scientific topic, what should your mindset be?",
            "option_a": "Treat AI output as 100% infallible truth.",
            "option_b": "Remember AI can 'hallucinate' plausible-sounding falsehoods; verify important factual claims with credible primary sources.",
            "option_c": "Assume all AI output is completely made up and never use it.",
            "option_d": "Copy-paste it directly into homework without reading.",
            "correct_option": "B",
            "explanation": "Large language models generate text based on probability patterns and can confidently hallucinate inaccuracies. Critical verification is essential."
        }
    ],
    "passwords_2fa": [
        {
            "question_text": "Which of the following is considered the STRONGEST password strategy for protecting your email or game account?",
            "option_a": "Your pet's name followed by '123!' (e.g., Fluffy123!)",
            "option_b": "A long, random passphrase of 4+ unrelated words (e.g., 'cactus-orbit-purple-blanket-89')",
            "option_c": "A short 6-character sequence like 'Abc$12'",
            "option_d": "The same password you use across all 15 of your other online accounts.",
            "correct_option": "B",
            "explanation": "Length is the most critical factor against brute-force attacks. Multi-word passphrases are easy to remember but take supercomputers centuries to crack."
        },
        {
            "question_text": "What is Two-Factor Authentication (2FA) and why is it so effective?",
            "option_a": "It means you have to type your password twice every time you log in.",
            "option_b": "It requires a second proof of identity (like a code from an authenticator app) in addition to your password, blocking hackers even if they steal your password.",
            "option_c": "It allows two people to share the same account simultaneously.",
            "option_d": "It replaces passwords with face scans only.",
            "correct_option": "B",
            "explanation": "2FA combines something you know (password) with something you have (phone/authenticator token). Even if your password is leaked in a data breach, hackers cannot log in."
        },
        {
            "question_text": "Why should you NEVER reuse the same password across multiple websites (like your school portal, Discord, and online games)?",
            "option_a": "Browsers will refuse to save duplicate passwords.",
            "option_b": "If one small, insecure website suffers a data breach, attackers will use that password to break into all your other accounts (credential stuffing).",
            "option_c": "Your keyboard keys will wear out faster.",
            "option_d": "It makes your internet connection slower.",
            "correct_option": "B",
            "explanation": "In credential stuffing attacks, hackers take leaked email/password combinations from compromised sites and run automated scripts against popular platforms like Google, Steam, and Instagram."
        }
    ]
}


class AzureAIFoundryClient:
    """
    Client for communicating with Azure AI Foundry endpoints.
    Supports both:
    1. Azure AI Agents (e.g., CyberQuizAgent running gpt-5 via protocols/openai/responses?api-version=v1)
    2. Standard Azure OpenAI / Model Inference chat completions endpoints.
    """

    def __init__(self):
        self.endpoint = settings.AZURE_AI_ENDPOINT
        self.api_key = settings.AZURE_AI_KEY
        self.deployment = settings.AZURE_AI_DEPLOYMENT_NAME or "gpt-5"
        self.api_version = settings.AZURE_AI_API_VERSION or "v1"

    @property
    def is_configured(self) -> bool:
        return bool(self.endpoint and self.api_key)

    @property
    def is_agent_responses_endpoint(self) -> bool:
        """Checks if the endpoint is an Azure AI Agent protocols/openai/responses endpoint."""
        return "protocols/openai/responses" in self.endpoint or "/agents/" in self.endpoint

    def _get_api_url(self) -> str:
        """Determines the appropriate REST URL for Azure AI Agent or Azure OpenAI."""
        clean_endpoint = self.endpoint.rstrip('/')

        # 1. Azure AI Agent Protocols endpoint (CyberQuizAgent)
        if self.is_agent_responses_endpoint:
            if "api-version=" not in clean_endpoint:
                version = self.api_version or "v1"
                return f"{clean_endpoint}?api-version={version}"
            return clean_endpoint

        # 2. Azure OpenAI standard completions endpoint
        if "openai.azure.com" in clean_endpoint:
            version = self.api_version or "2024-06-01"
            return f"{clean_endpoint}/openai/deployments/{self.deployment}/chat/completions?api-version={version}"

        if "/chat/completions" in clean_endpoint:
            return clean_endpoint

        # 3. Model Inference standard endpoint
        version = self.api_version or "2024-06-01"
        return f"{clean_endpoint}/models/chat/completions?api-version={version}"

    def _call_azure(self, prompt: str, system_prompt: str = "") -> str:
        """
        Executes a call to Azure AI Foundry, seamlessly handling either
        the Azure AI Agent responses protocol or standard chat completions.
        """
        if not self.is_configured:
            raise ValueError("Azure AI Foundry credentials are not configured in settings/environment.")

        url = self._get_api_url()
        headers = {
            "Content-Type": "application/json",
            "api-key": self.api_key,
        }

        # Case A: Azure AI Agent endpoint (e.g., CyberQuizAgent running gpt-5)
        if self.is_agent_responses_endpoint:
            combined_input = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
            payload = {
                "model": self.deployment or "gpt-5",
                "input": combined_input,
            }
            response = requests.post(url, headers=headers, json=payload, timeout=35)
            response.raise_for_status()
            data = response.json()

            # Extract assistant text from output messages
            for item in data.get("output", []):
                if item.get("type") == "message" and item.get("role") == "assistant":
                    for c in item.get("content", []):
                        if c.get("type") == "output_text":
                            return c.get("text", "")
            return ""

        # Case B: Standard Chat Completions endpoint
        else:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1500,
            }
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    def _clean_json_string(self, text: str) -> str:
        """Strips markdown code blocks and whitespace to extract clean JSON."""
        cleaned = text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()

    def generate_quiz_questions(self, topic_id: str, count: int = 3) -> list:
        """
        Dynamically generates `count` MCQ questions for the given topic using Azure AI Foundry / CyberQuizAgent.
        """
        topic = get_topic_by_id(topic_id)
        topic_title = topic["title"] if topic else topic_id

        if self.is_configured:
            try:
                system_prompt = (
                    "You are an expert cybersecurity educator creating engaging, scenario-based multiple-choice "
                    "quizzes for Middle and High School students (ages 11-18). "
                    "Focus on realistic teenage scenarios: gaming platforms, social media (TikTok, Instagram, Discord, Snapchat), "
                    "school portals, mobile SMS/WhatsApp, and friends. "
                    "You must output ONLY valid JSON matching this schema: "
                    '{"questions": [{"question_text": "...", "option_a": "...", "option_b": "...", "option_c": "...", "option_d": "...", "correct_option": "A/B/C/D", "explanation": "..."}]}'
                )

                prompt = (
                    f"Generate exactly {count} distinct multiple-choice questions for the topic: '{topic_title}'.\n"
                    f"Topic description: {topic.get('description', '')}\n"
                    f"Key learning concepts: {', '.join(topic.get('key_concepts', []))}\n\n"
                    "Requirements:\n"
                    "1. Exactly 4 plausible options for each question (option_a, option_b, option_c, option_d).\n"
                    "2. One unambiguously correct answer (correct_option must be 'A', 'B', 'C', or 'D').\n"
                    "3. Include an educational explanation clarifying why the correct choice keeps the student safe.\n"
                    "4. Output format must be strict JSON with a top-level 'questions' array. Do not include markdown code blocks or extra text."
                )

                raw_content = self._call_azure(prompt=prompt, system_prompt=system_prompt)
                clean_content = self._clean_json_string(raw_content)
                parsed = json.loads(clean_content)
                questions = parsed.get("questions", [])
                if len(questions) >= count:
                    logger.info(f"Successfully generated {len(questions)} questions from Azure AI for {topic_id}")
                    return questions[:count]
            except Exception as e:
                logger.warning(f"Azure AI question generation failed ({e}). Falling back to curated bank.")

        # Fallback to curated realistic question pool
        pool = FALLBACK_QUESTIONS.get(topic_id, [])
        if not pool:
            pool = [
                {
                    "question_text": f"What is the safest action when encountering an unknown message regarding {topic_title}?",
                    "option_a": "Click on any provided link immediately.",
                    "option_b": "Never click unknown links; verify through official sources.",
                    "option_c": "Send your password to verify your account.",
                    "option_d": "Turn off your computer monitor only.",
                    "correct_option": "B",
                    "explanation": "Verifying messages through trusted channels prevents falling victim to online scams."
                }
            ]
        selected = list(pool)
        random.shuffle(selected)
        return selected[:count]

    def generate_feedback(self, student_name: str, topic_title: str, score: int, total: int, items_review: list) -> str:
        """
        Generates supportive, personalized feedback for a student based on their quiz performance using CyberQuizAgent.
        """
        percentage = round((score / total) * 100) if total > 0 else 0

        if self.is_configured:
            try:
                system_prompt = (
                    "You are an encouraging, supportive cybersecurity teacher reviewing a student's quiz attempt. "
                    "Your tone is warm, inspiring, and actionable for a teenager. "
                    "Congratulate them on what they did well, clearly and gently explain why any incorrect choices they made "
                    "were dangerous in the real world, and give 2 practical safety tips they can remember."
                )

                user_prompt = (
                    f"Student: {student_name}\n"
                    f"Topic: {topic_title}\n"
                    f"Score: {score}/{total} ({percentage}%)\n\n"
                    f"Question Breakdown:\n"
                )

                for idx, item in enumerate(items_review, start=1):
                    user_prompt += (
                        f"Question {idx}: {item.get('question_text')}\n"
                        f" - Student selected: Option {item.get('student_selected')}\n"
                        f" - Correct option: Option {item.get('correct_option')}\n"
                        f" - Result: {'CORRECT' if item.get('is_correct') else 'INCORRECT'}\n"
                        f" - Context: {item.get('explanation', '')}\n\n"
                    )

                user_prompt += (
                    "Please provide an encouraging feedback review for the student:\n"
                    "1. A warm opening acknowledging their score and effort.\n"
                    "2. A gentle explanation of any mistakes and why that cyber threat is dangerous.\n"
                    "3. 2 golden cybersecurity rules for this specific topic."
                )

                review = self._call_azure(prompt=user_prompt, system_prompt=system_prompt)
                if review and len(review.strip()) > 30:
                    return review.strip()
            except Exception as e:
                logger.warning(f"Azure AI feedback generation failed ({e}). Falling back to local mentor engine.")

        # Fallback educational review generator
        return self._generate_fallback_feedback(student_name, topic_title, score, total, items_review)

    def _generate_fallback_feedback(self, student_name: str, topic_title: str, score: int, total: int, items_review: list) -> str:
        """Constructs rich, encouraging mentor feedback locally."""
        percentage = round((score / total) * 100) if total > 0 else 0

        if score == total:
            praise = f"🌟 Outstanding work, {student_name}! You scored a perfect {score}/{total} (100%) on {topic_title}!"
            body = (
                "You demonstrated a sharp cybersecurity instinct and spotted every trick! "
                "You understand the tactics threat actors use and know exactly how to stay safe.\n\n"
                "🛡️ Pro-Tips to keep your streak going:\n"
                "• Share what you learned with friends who might not know how to spot these scams.\n"
                "• Keep your software, apps, and defenses updated across all your devices."
            )
        elif score >= (total / 2):
            praise = f"👏 Good effort, {student_name}! You scored {score}/{total} ({percentage}%) on {topic_title}."
            incorrect_notes = []
            for item in items_review:
                if not item.get("is_correct"):
                    incorrect_notes.append(
                        f"• On Question: \"{item.get('question_text')[:75]}...\"\n"
                        f"  Remember: {item.get('explanation')}"
                    )
            mistakes_text = "\n".join(incorrect_notes) if incorrect_notes else "Review the topics you hesitated on."
            body = (
                f"You have a solid foundation in digital safety, but there are a couple of subtle traps to watch out for:\n\n"
                f"{mistakes_text}\n\n"
                f"💡 Real-World Safety Rule: Whenever you feel rushed, urged, or offered free perks online, pause for 10 seconds and verify through an independent channel!"
            )
        else:
            praise = f"💪 Great start, {student_name}! You scored {score}/{total} ({percentage}%) on {topic_title}."
            incorrect_notes = []
            for item in items_review:
                if not item.get("is_correct"):
                    incorrect_notes.append(
                        f"• Focus Point: {item.get('explanation')}"
                    )
            mistakes_text = "\n".join(incorrect_notes)
            body = (
                f"Cyber threats are designed specifically to trick people, so don't get discouraged! This is how we learn and level up.\n\n"
                f"Key Takeaways for this topic:\n{mistakes_text}\n\n"
                f"🚀 Action Step: Try taking this topic quiz again to see how much faster you spot the red flags!"
            )

        return f"{praise}\n\n{body}"


# Singleton instance
ai_client = AzureAIFoundryClient()
