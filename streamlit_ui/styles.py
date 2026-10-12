"""
Nexus Studio Cyber Aesthetic CSS Stylesheet.
Injected globally into Streamlit for 1:1 parity with Django Tailwind.
"""
import textwrap
import streamlit as st

NEXUS_STUDIO_CSS = '''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://api.fontshare.com/v2/css?f[]=clash-display@400,500,600,700&f[]=cabinet-grotesk@400,500,700,800&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap" rel="stylesheet"/>
<style>
    /* Direct Fontshare CDN @font-face Rules for 100% Reliable Rendering */
    @font-face {
        font-family: 'Clash Display';
        src: url('https://cdn.fontshare.com/wf/FPDAZ2S6SW4QMSRIIKNNGTPM6VIXYMKO/5HNPQ453FRLIQWV2FNOBUU3FKTDZQVSG/Z3MGHFHX6DCTLQ55LJYRJ5MDCZPMFZU6.woff2') format('woff2');
        font-weight: 600;
        font-display: swap;
        font-style: normal;
    }
    @font-face {
        font-family: 'Clash Display';
        src: url('https://cdn.fontshare.com/wf/BFBSY7LX5W2U2EROCLVVTQP4VS7S4PC3/IIUX4FGTMD2LK2VWD3RVTAS4SSMUN7B5/53RZKGODFYDW3QHTIL7IPOWTBCSUEZK7.woff2') format('woff2');
        font-weight: 700;
        font-display: swap;
        font-style: normal;
    }
    @font-face {
        font-family: 'Cabinet Grotesk';
        src: url('https://cdn.fontshare.com/wf/LAFFD4SDUCDVQEXFPDC7C53EQ4ZELWQI/PXCT3G6LO6ICM5I3NTYENYPWJAECAWDD/GHM6WVH6MILNYOOCXHXB5GTSGNTMGXZR.woff2') format('woff2');
        font-weight: 700;
        font-display: swap;
        font-style: normal;
    }
    @font-face {
        font-family: 'Cabinet Grotesk';
        src: url('https://cdn.fontshare.com/wf/TTX2Z3BF3P6Y5BQT3IV2VNOK6FL22KUT/7QYRJOI3JIMYHGY6CH7SOIFRQLZOLNJ6/KFIAZD4RUMEZIYV6FQ3T3GP5PDBDB6JY.woff2') format('woff2');
        font-weight: 400;
        font-display: swap;
        font-style: normal;
    }

    /* Material Symbols font family assignment */
    .material-symbols-outlined {
        font-family: 'Material Symbols Outlined' !important;
        font-weight: normal !important;
        font-style: normal !important;
        font-size: 20px;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-smoothing: antialiased;
        vertical-align: middle;
        overflow: hidden !important;
        text-overflow: clip !important;
        max-width: 100% !important;
        user-select: none;
    }

    /* Global reset to Obsidian deep canvas */
    html, body, [class*="css"], .stApp {
        background-color: #04040a !important;
        font-family: 'Cabinet Grotesk', -apple-system, BlinkMacSystemFont, sans-serif !important;
        color: #f0f0f8 !important;
        margin: 0 !important;
    }

    /* Ambient Glow Blobs & Grid Lines (Exact Localhost Signature) */
    .stApp {
        background-image: 
            radial-gradient(circle at 25% 10%, rgba(232, 255, 71, 0.08) 0%, transparent 45%),
            radial-gradient(circle at 80% 40%, rgba(255, 107, 53, 0.07) 0%, transparent 45%),
            linear-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255, 255, 255, 0.03) 1px, transparent 1px) !important;
        background-size: 100% 100%, 100% 100%, 60px 60px, 60px 60px !important;
    }

    /* Hide standard Streamlit header and footer */
    header[data-testid="stHeader"] {
        display: none !important;
    }
    #MainMenu, footer {
        visibility: hidden !important;
    }

    /* Main Container Padding to clear fixed header */
    .block-container {
        padding-top: 5rem !important;
        padding-bottom: 5rem !important;
        max-width: 1280px !important;
        margin: 0 auto !important;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-top: 7.2rem !important;
            padding-bottom: 7.5rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
    }

    /* Typography */
    h1, h2, h3, h4, .font-display, .font-serif-title {
        font-family: 'Clash Display', 'Cabinet Grotesk', sans-serif !important;
        color: #ffffff !important;
        letter-spacing: -0.025em !important;
    }
    p, span, div, label, input, select {
        font-family: 'Cabinet Grotesk', sans-serif;
    }
    .font-mono, code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Text-stroke effect (1:1 with Django Tailwind hover:text-signal) */
    .text-stroke {
        -webkit-text-stroke: 1.5px rgba(255, 255, 255, 0.4);
        color: transparent !important;
        transition: color 0.4s ease, -webkit-text-stroke 0.4s ease, text-shadow 0.4s ease;
        display: block;
        cursor: pointer;
    }
    .text-stroke:hover {
        color: #e8ff47 !important;
        -webkit-text-stroke: 1.5px #e8ff47 !important;
        text-shadow: 0 0 30px rgba(232, 255, 71, 0.45) !important;
    }

    /* Marquee Animation */
    @keyframes marquee {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-50%); }
    }
    .animate-marquee {
        display: inline-block;
        white-space: nowrap;
        animation: marquee 28s linear infinite;
    }

    /* Exact Fixed Edge-to-Edge Top Navbar (1:1 with templates/base.html) */
    .fixed-navbar {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        height: 64px !important;
        background: rgba(4, 4, 10, 0.88) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.06) !important;
        z-index: 999999 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5) !important;
    }
    .fixed-navbar-inner {
        max-width: 1280px !important;
        width: 100% !important;
        height: 100% !important;
        padding: 0 24px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 16px !important;
    }
    .brand-link {
        display: flex;
        align-items: center;
        gap: 10px;
        text-decoration: none;
        color: #ffffff;
    }
    .brand-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #e8ff47;
    }
    .brand-title {
        font-family: 'Clash Display', sans-serif;
        font-weight: 700;
        font-size: 1.15rem;
        letter-spacing: -0.02em;
        color: #ffffff;
    }
    .brand-status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #e8ff47;
        box-shadow: 0 0 10px #e8ff47;
    }
    .nav-links {
        display: flex;
        align-items: center;
        gap: 24px;
    }
    .nav-link {
        font-family: 'Cabinet Grotesk', sans-serif;
        font-size: 0.92rem;
        font-weight: 500;
        color: #9898b8;
        text-decoration: none;
        padding: 6px 0;
        position: relative;
        transition: color 0.2s ease;
    }
    .nav-link:hover {
        color: #ffffff;
    }
    .nav-link.active {
        color: #ffffff;
        font-weight: 600;
    }
    .nav-link.active::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        right: 0;
        height: 2px;
        background: #e8ff47;
        border-radius: 2px;
    }
    .nav-right {
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .system-status-pill {
        display: flex;
        align-items: center;
        gap: 6px;
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 4px 12px;
        border-radius: 9999px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #9898b8;
    }
    .system-status-pill .status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #e8ff47;
        box-shadow: 0 0 8px #e8ff47;
    }
    .teacher-toggle-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 9999px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #c4c4d8;
        background: #0d0d1f;
        text-decoration: none;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        transition: all 0.2s;
    }
    .teacher-toggle-btn:hover {
        border-color: rgba(232, 255, 71, 0.35);
        color: #e8ff47;
    }
    .student-avatar-pill {
        display: flex;
        align-items: center;
        gap: 8px;
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 4px 12px 4px 4px;
        border-radius: 9999px;
        text-decoration: none;
    }
    .avatar-circle {
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: #e8ff47;
        color: #04040a;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        font-size: 0.7rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .avatar-name {
        font-family: 'Cabinet Grotesk', sans-serif;
        font-weight: 600;
        font-size: 0.8rem;
        color: #ffffff;
    }
    .avatar-meta {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #e8ff47;
        margin-left: 4px;
    }
    .logout-pill-btn {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 5px 12px;
        border-radius: 9999px;
        background: rgba(255, 107, 53, 0.1);
        border: 1px solid rgba(255, 107, 53, 0.35);
        color: #ff6b35 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-decoration: none;
        transition: all 0.2s ease;
        cursor: pointer;
    }
    .logout-pill-btn:hover {
        background: rgba(255, 107, 53, 0.25);
        border-color: #ff6b35;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(255, 107, 53, 0.3);
    }
    .btn-signin-student {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        border-radius: 9999px;
        background: #e8ff47;
        border: 1px solid #e8ff47;
        color: #04040a !important;
        font-family: 'Clash Display', 'Cabinet Grotesk', sans-serif;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-decoration: none;
        transition: all 0.2s ease;
        box-shadow: 0 0 15px rgba(232, 255, 71, 0.25);
    }
    .btn-signin-student:hover {
        background: #f4ff9e;
        box-shadow: 0 0 25px rgba(232, 255, 71, 0.45);
        transform: translateY(-1px);
    }
    .btn-signin-teacher {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 9999px;
        background: rgba(52, 211, 153, 0.12);
        border: 1px solid rgba(52, 211, 153, 0.35);
        color: #34d399 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-decoration: none;
        transition: all 0.2s ease;
    }
    .btn-signin-teacher:hover {
        background: rgba(52, 211, 153, 0.25);
        border-color: #34d399;
        box-shadow: 0 0 15px rgba(52, 211, 153, 0.3);
        transform: translateY(-1px);
    }
    .teacher-avatar-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 4px 12px 4px 4px;
        border-radius: 9999px;
        text-decoration: none;
    }
    .teacher-circle {
        background: #10b981 !important;
        color: #04040a !important;
    }

    /* Two-Tier Responsive Mobile Navbar (<= 768px) */
    @media (max-width: 768px) {
        .fixed-navbar {
            height: auto !important;
            min-height: 96px !important;
            padding: 8px 0 6px 0 !important;
        }
        .fixed-navbar-inner {
            flex-wrap: wrap !important;
            padding: 0 16px !important;
            gap: 6px 10px !important;
            justify-content: space-between !important;
        }
        .nav-brand-wrapper {
            order: 1 !important;
            flex: 0 0 auto !important;
        }
        .nav-brand-wrapper .brand-title {
            font-size: 1rem !important;
        }
        .nav-right {
            order: 2 !important;
            flex: 0 0 auto !important;
            gap: 6px !important;
        }
        .system-status-pill {
            display: none !important;
        }
        .btn-signin-teacher, .btn-signin-student {
            padding: 5px 10px !important;
            font-size: 0.68rem !important;
            letter-spacing: 0.02em !important;
        }
        .student-avatar-pill, .teacher-avatar-pill {
            padding: 3px 8px 3px 3px !important;
        }
        .avatar-name {
            font-size: 0.75rem !important;
            max-width: 80px !important;
            white-space: nowrap !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
        }
        .avatar-meta {
            display: none !important;
        }
        .logout-pill-btn {
            padding: 4px 8px !important;
            font-size: 0.68rem !important;
        }
        .nav-links {
            order: 3 !important;
            width: 100% !important;
            flex: 1 1 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            gap: 16px !important;
            padding: 6px 0 2px 0 !important;
            border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }
        .nav-link {
            font-size: 0.82rem !important;
            padding: 4px 4px !important;
            white-space: nowrap !important;
        }
    }

    /* Buttons */
    .btn-primary {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #e8ff47;
        color: #04040a !important;
        font-family: 'Clash Display', sans-serif;
        font-weight: 700;
        font-size: 0.92rem;
        padding: 13px 26px;
        border-radius: 9999px;
        text-decoration: none;
        box-shadow: 0 0 25px rgba(232, 255, 71, 0.25);
        transition: all 0.25s ease;
    }
    .btn-primary:hover {
        background: #d4ec33;
        transform: translateY(-2px);
        box-shadow: 0 0 35px rgba(232, 255, 71, 0.4);
    }
    .btn-secondary {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: transparent;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        padding: 13px 24px;
        border-radius: 9999px;
        text-decoration: none;
        transition: all 0.25s ease;
    }
    .btn-secondary:hover {
        border-color: rgba(232, 255, 71, 0.5);
        color: #e8ff47 !important;
        background: rgba(232, 255, 71, 0.05);
    }
    .btn-ghost {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        color: #9898b8 !important;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.78rem;
        padding: 13px 18px;
        text-decoration: none;
        transition: color 0.2s;
    }
    .btn-ghost:hover {
        color: #ffffff !important;
    }

    /* Bento Grid Layout */
    .bento-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
    }
    @media (max-width: 900px) {
        .bento-grid {
            grid-template-columns: 1fr;
        }
    }
    .bento-span-2 {
        grid-column: span 2;
    }
    .bento-span-3 {
        grid-column: span 3;
    }
    @media (max-width: 900px) {
        .bento-span-2, .bento-span-3 {
            grid-column: span 1;
        }
    }

    .bento-card {
        background: #0b0b18;
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 26px;
        text-decoration: none;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        min-height: 250px;
    }
    .bento-card:hover {
        border-color: rgba(232, 255, 71, 0.35);
        background: #0d0d1f;
        transform: translateY(-3px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
    }
    .bento-top {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 20px;
    }
    .bento-num {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: #9898b8;
    }
    .bento-icon {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: #080812;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        color: rgba(255, 255, 255, 0.7);
        transition: all 0.2s;
    }
    .bento-card:hover .bento-icon {
        color: #e8ff47;
        border-color: rgba(232, 255, 71, 0.4);
        transform: scale(1.08);
    }
    .bento-title {
        font-family: 'Clash Display', sans-serif;
        font-size: 1.35rem;
        font-weight: 500;
        color: #ffffff;
        margin: 0 0 8px 0;
        transition: color 0.2s;
    }
    .bento-card:hover .bento-title {
        color: #e8ff47;
    }
    .bento-desc {
        font-family: 'Cabinet Grotesk', sans-serif;
        font-size: 0.88rem;
        color: #9898b8;
        line-height: 1.5;
        margin: 0;
    }
    .bento-bottom {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 24px;
        padding-top: 14px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
    }
    .bento-action {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #e8ff47;
        font-weight: 600;
        letter-spacing: 0.05em;
    }

    /* Cards */
    .nexus-card {
        background: #0d0d1f;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    .nexus-card-active {
        background: linear-gradient(145deg, #0d0d1f 0%, #12122e 100%);
        border: 1px solid rgba(232, 255, 71, 0.4);
        border-radius: 20px;
        padding: 28px;
        box-shadow: 0 0 40px rgba(232, 255, 71, 0.12);
    }
    .cyber-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: #080812;
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #9898b8;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        padding: 5px 14px;
        border-radius: 9999px;
    }
    .cyber-pill-signal {
        background: rgba(232, 255, 71, 0.12);
        border-color: rgba(232, 255, 71, 0.35);
        color: #e8ff47;
    }

    /* Student Dashboard Topic Card & Action Links */
    .student-topic-card {
        background: #0b0b18;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 20px;
        margin-bottom: 18px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        min-height: 230px;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        position: relative;
    }
    .student-topic-card:hover {
        border-color: rgba(232, 255, 71, 0.35);
        background: #0e0e22;
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.45);
    }
    .topic-icon-box {
        width: 42px;
        height: 42px;
        min-width: 42px;
        max-width: 42px;
        border-radius: 12px;
        background: #080812;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        align-items: center;
        justify-content: center;
        overflow: hidden !important;
        flex-shrink: 0;
        transition: all 0.2s ease;
    }
    .student-topic-card:hover .topic-icon-box {
        border-color: rgba(232, 255, 71, 0.4);
        transform: scale(1.05);
    }
    .topic-btn {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 16px;
        border-radius: 9999px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        font-weight: 700;
        text-decoration: none !important;
        transition: all 0.2s ease;
        cursor: pointer;
        line-height: 1.4;
    }
    .topic-btn-start {
        background: #e8ff47;
        color: #04040a !important;
        border: 1px solid #e8ff47;
        box-shadow: 0 0 15px rgba(232, 255, 71, 0.25);
    }
    .topic-btn-start:hover {
        background: #d4ec33;
        transform: translateY(-1px);
        box-shadow: 0 0 25px rgba(232, 255, 71, 0.45);
    }
    .topic-btn-retry {
        background: #ff6b35;
        color: #ffffff !important;
        border: 1px solid #ff6b35;
        box-shadow: 0 0 15px rgba(255, 107, 53, 0.25);
    }
    .topic-btn-retry:hover {
        background: #f05a24;
        transform: translateY(-1px);
        box-shadow: 0 0 25px rgba(255, 107, 53, 0.45);
    }
    .topic-btn-review {
        background: #080812;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .topic-btn-review:hover {
        background: #121226;
        border-color: rgba(232, 255, 71, 0.5);
        color: #e8ff47 !important;
    }

    /* Streamlit Radio Override - Interactive Cyber Option Cards */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 12px !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] {
        background: #080812 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        margin: 0 !important;
        transition: all 0.2s ease !important;
        cursor: pointer !important;
        width: 100% !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:hover {
        border-color: rgba(232, 255, 71, 0.5) !important;
        background: #0d0d1f !important;
        box-shadow: 0 0 20px rgba(232, 255, 71, 0.1) !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"] div[data-testid="stMarkdownContainer"] p {
        font-family: 'Cabinet Grotesk', sans-serif !important;
        font-size: 1rem !important;
        color: #f0f0f8 !important;
        line-height: 1.5 !important;
    }
    div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) {
        border-color: #e8ff47 !important;
        background: rgba(232, 255, 71, 0.08) !important;
        box-shadow: 0 0 25px rgba(232, 255, 71, 0.15) !important;
    }

    /* Streamlit Buttons & Form Submit Buttons */
    .stButton > button,
    div[data-testid="stFormSubmitButton"] > button,
    button[data-testid="baseButton-primary"],
    button[kind="primary"] {
        background: #e8ff47 !important;
        color: #04040a !important;
        font-family: 'Clash Display', sans-serif !important;
        font-weight: 700 !important;
        border-radius: 9999px !important;
        border: none !important;
        padding: 0.75rem 2.2rem !important;
        box-shadow: 0 0 25px rgba(232, 255, 71, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button *,
    div[data-testid="stFormSubmitButton"] > button *,
    button[data-testid="baseButton-primary"] *,
    button[kind="primary"] *,
    div[data-testid="stFormSubmitButton"] p,
    div[data-testid="stFormSubmitButton"] span,
    div[data-testid="stFormSubmitButton"] div,
    button[data-testid="baseButton-primary"] p,
    button[data-testid="baseButton-primary"] span,
    button[data-testid="baseButton-primary"] div,
    button[kind="primary"] p,
    button[kind="primary"] span,
    button[kind="primary"] div {
        color: #04040a !important;
        font-family: 'Clash Display', sans-serif !important;
        font-weight: 700 !important;
    }
    .stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover,
    button[data-testid="baseButton-primary"]:hover,
    button[kind="primary"]:hover {
        background: #d4ec33 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 0 35px rgba(232, 255, 71, 0.45) !important;
    }

    /* Streamlit Secondary Buttons */
    .stButton > button[kind="secondary"],
    button[data-testid="baseButton-secondary"],
    button[kind="secondary"] {
        background: #080812 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: none !important;
    }
    .stButton > button[kind="secondary"] *,
    button[data-testid="baseButton-secondary"] *,
    button[kind="secondary"] * {
        color: #ffffff !important;
        font-family: 'Cabinet Grotesk', sans-serif !important;
        font-weight: 600 !important;
    }
    .stButton > button[kind="secondary"]:hover,
    button[data-testid="baseButton-secondary"]:hover,
    button[kind="secondary"]:hover {
        background: #121226 !important;
        border-color: rgba(232, 255, 71, 0.5) !important;
        color: #e8ff47 !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button[kind="secondary"]:hover *,
    button[data-testid="baseButton-secondary"]:hover *,
    button[kind="secondary"]:hover * {
        color: #e8ff47 !important;
    }

    /* Form Inputs & Selectboxes */
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        background-color: #080812 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
    }
    div[data-baseweb="select"] > div:hover,
    div[data-baseweb="input"] > div:hover {
        border-color: rgba(232, 255, 71, 0.5) !important;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        background-color: #080812 !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        margin-bottom: 14px !important;
    }

    /* Topic Filter Segmented Control Tabs (1:1 with student_dashboard.html) */
    div[data-testid="stSegmentedControl"] {
        background: #080812 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 9999px !important;
        padding: 4px !important;
        display: inline-flex !important;
        justify-content: flex-end !important;
        margin-left: auto !important;
        width: fit-content !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4) !important;
    }
    div[data-testid="stSegmentedControl"] > div {
        background: transparent !important;
        border: none !important;
        gap: 4px !important;
        padding: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
    }
    div[data-testid="stSegmentedControl"] button {
        background: transparent !important;
        color: #9898b8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        border-radius: 9999px !important;
        border: none !important;
        padding: 4px 12px !important;
        min-height: 28px !important;
        height: 28px !important;
        box-shadow: none !important;
        transform: none !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stSegmentedControl"] button:hover {
        background: rgba(255, 255, 255, 0.06) !important;
        color: #ffffff !important;
        transform: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stSegmentedControl"] button[data-selected="true"],
    div[data-testid="stSegmentedControl"] button[aria-checked="true"],
    div[data-testid="stSegmentedControl"] button[data-state="on"],
    div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
    div[data-testid="stSegmentedControl"] button[data-variant="segmented_control"][data-selected] {
        background: #e8ff47 !important;
        color: #04040a !important;
        font-weight: 700 !important;
        box-shadow: 0 0 15px rgba(232, 255, 71, 0.3) !important;
    }
    div[data-testid="stSegmentedControl"] button[data-selected="true"]:hover,
    div[data-testid="stSegmentedControl"] button[aria-checked="true"]:hover,
    div[data-testid="stSegmentedControl"] button[data-state="on"]:hover,
    div[data-testid="stSegmentedControl"] button[data-variant="segmented_control"][data-selected]:hover {
        background: #d4ec33 !important;
        color: #04040a !important;
        transform: none !important;
    }

    /* Minimalist 4px Scrollbar */
    ::-webkit-scrollbar {
        width: 4px;
        height: 4px;
    }
    ::-webkit-scrollbar-track {
        background: #080812;
    }
    ::-webkit-scrollbar-thumb {
        background: #e8ff47;
        border-radius: 9999px;
    }

    /* Streamlit Auto-Stacking Columns on Mobile Viewports (<= 768px) */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            flex-direction: column !important;
            gap: 14px !important;
        }
        div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
            width: 100% !important;
            min-width: 100% !important;
            flex: 1 1 100% !important;
        }
        /* Touch target minimum size on mobile */
        .stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            min-height: 44px !important;
            padding: 0.75rem 1.4rem !important;
        }
    }

    /* Responsive 4-Column Stats Grid (Home Page) */
    .stats-grid-4 {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 32px;
        padding: 28px 0;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin: 30px 0 20px 0;
    }
    @media (max-width: 768px) {
        .stats-grid-4 {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 20px 16px !important;
            padding: 20px 0 !important;
        }
    }
    @media (max-width: 480px) {
        .stats-grid-4 {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 16px 12px !important;
        }
    }

    /* Teacher Metrics Grid (4 Top Metric Cards) */
    .teacher-metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    @media (max-width: 900px) {
        .teacher-metrics-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 14px !important;
        }
    }
    @media (max-width: 480px) {
        .teacher-metrics-grid {
            grid-template-columns: 1fr !important;
            gap: 12px !important;
        }
    }

    /* Certificate Stats Grid */
    .cert-stats-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 10px;
        max-width: 700px;
        margin: 0 auto 32px auto;
        position: relative;
        z-index: 10;
        font-family: 'JetBrains Mono', monospace;
    }
    @media (max-width: 768px) {
        .cert-stats-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 10px !important;
        }
    }

    /* Answer Comparison Grid in Quiz Arena */
    .answer-comparison-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin-bottom: 14px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
    }
    @media (max-width: 480px) {
        .answer-comparison-grid {
            grid-template-columns: 1fr !important;
            gap: 8px !important;
        }
    }

    /* Responsive Table Wrapper for Horizontally Scrolling Data Tables */
    .responsive-table-wrap {
        width: 100% !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        border-radius: 0 0 20px 20px;
    }
    .responsive-table-wrap table {
        min-width: 640px !important;
    }
</style>
'''


def inject_nexus_styles() -> None:
    """Injects the Nexus Studio font links, resets, and cyber CSS tokens into Streamlit."""
    st.markdown(NEXUS_STUDIO_CSS, unsafe_allow_html=True)


def render_html(html_str: str) -> None:
    """Renders raw HTML safely in Streamlit."""
    clean = textwrap.dedent(html_str).strip()
    if hasattr(st, "html"):
        st.html(clean)
    else:
        st.markdown(clean, unsafe_allow_html=True)
