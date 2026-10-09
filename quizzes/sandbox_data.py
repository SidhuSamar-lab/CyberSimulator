"""
Interactive Phishing Inbox & URL Inspector Simulation Scenarios.
Designed for Middle & High School students to examine realistic digital messages,
inspect sender headers, hover over links to reveal spoofed domains, and detect social engineering.
"""

SANDBOX_EMAILS = [
    {
        "id": "email-1",
        "sender_name": "School IT Helpdesk",
        "sender_email": "admin@sch00l-district9.org",
        "sender_verified": False,
        "subject": "⚠️ CRITICAL: Your Student Account Will Be Deleted in 2 Hours",
        "timestamp": "10 minutes ago",
        "category": "School Portal",
        "body_html": """
            <p class="mb-3">Dear Student,</p>
            <p class="mb-3">Our automated security scanner detected abnormal activity on your school Google/Microsoft account. If you do not verify your login credentials immediately, all your homework submissions and school email access will be <strong>permanently purged</strong> today at 5:00 PM.</p>
            <p class="mb-4">Click the secure authentication link below to preserve your access:</p>
            <p class="mb-4">
                <a href="#" class="sandbox-link inline-block px-5 py-2.5 rounded-xl bg-rose-600 text-white font-bold text-xs" data-target-url="https://portal-login.sch00l-district9.org.attacker-hosted.ru/auth/verify">
                    Verify School Account Now &rarr;
                </a>
            </p>
            <p class="text-xs text-slate-400">IT Systems Security Group &bull; District Secondary Schools</p>
        """,
        "hover_url": "https://portal-login.sch00l-district9.org.attacker-hosted.ru/auth/verify",
        "raw_headers": {
            "From": "School IT Helpdesk <admin@sch00l-district9.org>",
            "Reply-To": "data-stealer-89@external-mail.ru",
            "SPF-Check": "FAIL (Domain 'sch00l-district9.org' not authorized)",
            "DMARC": "FAIL",
            "Return-Path": "<bounce@external-mail.ru>",
        },
        "is_phishing": True,
        "red_flags": [
            "Look closely at the sender domain: 'sch00l' with double zeros instead of 'school'.",
            "Artificial urgency: threatening to delete homework in 2 hours to cause panic.",
            "Destination URL directs to a Russian top-level domain (.ru) masquerading behind a subdomain.",
            "Reply-To address does not match the school's official IT staff."
        ],
        "explanation": "This is a classic 'credential harvesting' attack. Attackers use zero typosquatting ('sch00l') and panic tactics so students type their school passwords before checking the URL."
    },
    {
        "id": "email-2",
        "sender_name": "Discord Community Gifts",
        "sender_email": "notifications@discorcl-nitro-promo.xyz",
        "sender_verified": False,
        "subject": "🎉 You won 3 Months of Free Discord Nitro from Server Giveaway!",
        "timestamp": "45 minutes ago",
        "category": "Gaming & Chat",
        "body_html": """
            <p class="mb-3">Hey Gamer!</p>
            <p class="mb-3">Congratulations! You were randomly selected as the lucky winner of our <strong>Community Nitro Giveaway</strong>! You get 3 free months of Nitro Boost, custom animated emojis, and 500MB uploads.</p>
            <p class="mb-4">Claim expires in 15 minutes! Tap below and authorize your Discord account:</p>
            <p class="mb-4">
                <a href="#" class="sandbox-link inline-block px-5 py-2.5 rounded-xl bg-purple-600 text-white font-bold text-xs" data-target-url="https://discorcl-nitro-promo.xyz/claim/gift?token=9284819">
                    Claim Free 3-Month Nitro &rarr;
                </a>
            </p>
            <p class="text-xs text-slate-400">Discord Official Rewards Team &bull; San Francisco, CA</p>
        """,
        "hover_url": "https://discorcl-nitro-promo.xyz/claim/gift?token=9284819",
        "raw_headers": {
            "From": "Discord Community Gifts <notifications@discorcl-nitro-promo.xyz>",
            "Reply-To": "harvest@discorcl-nitro-promo.xyz",
            "SPF-Check": "NEUTRAL",
            "DMARC": "NONE",
            "Originating-IP": "185.220.101.5",
        },
        "is_phishing": True,
        "red_flags": [
            "Typosquatting: 'discorcl' with an 'cl' instead of 'd' (discord.com).",
            "Free Nitro giveaways in random DMs or emails are almost always token grabbers.",
            "Fake countdown timer: 'Claim expires in 15 minutes'.",
            "Unofficial top-level domain (.xyz)."
        ],
        "explanation": "Attackers run Discord token grabbers. If you log in through their fake site, they steal your Discord session token and use your account to spam all your friends."
    },
    {
        "id": "email-3",
        "sender_name": "Lincoln High Library",
        "sender_email": "library@lincolnhigh.edu",
        "sender_verified": True,
        "subject": "Reminder: 'To Kill a Mockingbird' is due on Friday",
        "timestamp": "3 hours ago",
        "category": "School Notice",
        "body_html": """
            <p class="mb-3">Hello,</p>
            <p class="mb-3">This is a routine friendly reminder from the Lincoln High Media Center that your borrowed library book <em>To Kill a Mockingbird</em> is due for return on <strong>Friday, October 16</strong>.</p>
            <p class="mb-3">You can renew the book online via our official library catalog or return it to the drop box outside Room 204.</p>
            <p class="mb-4">
                <a href="#" class="sandbox-link inline-block px-5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-cyan-400 font-bold text-xs" data-target-url="https://library.lincolnhigh.edu/my-account/loans">
                    View Your Library Loans &rarr;
                </a>
            </p>
            <p class="text-xs text-slate-400">Lincoln High School Media Center &bull; library@lincolnhigh.edu</p>
        """,
        "hover_url": "https://library.lincolnhigh.edu/my-account/loans",
        "raw_headers": {
            "From": "Lincoln High Library <library@lincolnhigh.edu>",
            "Reply-To": "library@lincolnhigh.edu",
            "SPF-Check": "PASS (Domain 'lincolnhigh.edu' authorized)",
            "DMARC": "PASS",
            "TLS-Encryption": "Enforced",
        },
        "is_phishing": False,
        "red_flags": [],
        "explanation": "This is a legitimate email. The sender domain matches the official school domain (.edu), SPF/DMARC checks passed, there is no artificial panic or request for passwords, and the link points to the true school domain."
    },
    {
        "id": "email-4",
        "sender_name": "Steam Account Guard",
        "sender_email": "security-alert@steampowered-community-support.net",
        "sender_verified": False,
        "subject": "Unauthorized Trade Request of $185.00 Detected on Your Account",
        "timestamp": "Yesterday",
        "category": "Gaming & Inventory",
        "body_html": """
            <p class="mb-3">Dear Steam User,</p>
            <p class="mb-3">A trade offer transferring 4 CS:GO/Valorant skins to user <strong>[Player_984]</strong> was initiated from an IP in Bucharest, Romania. If this was NOT you, cancel the trade offer within 30 minutes before items are transferred permanently.</p>
            <p class="mb-4">
                <a href="#" class="sandbox-link inline-block px-5 py-2.5 rounded-xl bg-cyan-600 text-white font-bold text-xs" data-target-url="https://steamcommunity.com.trade-cancellation-portal.net/cancel?id=83921">
                    Cancel Fraudulent Trade &rarr;
                </a>
            </p>
            <p class="text-xs text-slate-400">Valve Corporation &bull; Steam Support Security</p>
        """,
        "hover_url": "https://steamcommunity.com.trade-cancellation-portal.net/cancel?id=83921",
        "raw_headers": {
            "From": "Steam Account Guard <security-alert@steampowered-community-support.net>",
            "Reply-To": "support@trade-cancellation-portal.net",
            "SPF-Check": "FAIL",
            "DMARC": "FAIL",
            "Return-Path": "<phish@trade-cancellation-portal.net>",
        },
        "is_phishing": True,
        "red_flags": [
            "Subdomain deception: 'steamcommunity.com' is actually just a subdomain prefix of 'trade-cancellation-portal.net'.",
            "Official Steam emails come from 'steampowered.com', never external hyphenated domains.",
            "Fear of losing expensive game items induces quick, unthinking clicks."
        ],
        "explanation": "Attackers prey on valuable game inventories. Notice the URL trick: browsers read the domain from right to left! The real domain is 'trade-cancellation-portal.net', not Steam."
    }
]
