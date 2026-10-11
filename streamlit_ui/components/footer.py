"""
CyberSimulator - Footer & Marquee Components.
"""
import streamlit as st


def render_marquee_ticker() -> None:
    """Renders the continuous telemetry marquee ticker across the platform."""
    marquee_html = """
    <div style="width: 100%; padding: 14px 0; background: #080812; border-top: 1px solid rgba(255,255,255,0.05); border-bottom: 1px solid rgba(255,255,255,0.05); overflow: hidden; white-space: nowrap; margin: 40px 0 50px 0;">
        <div class="animate-marquee font-mono" style="font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.2em; color: #9898b8;">
            <span style="margin: 0 20px; color: #e8ff47; font-weight: bold;">&bull; INTERACTIVE LEARNING</span>
            <span style="margin: 0 20px;">PHISHING DETECTION</span>
            <span style="margin: 0 20px; color: #ff6b35;">&bull; PASSWORD SECURITY</span>
            <span style="margin: 0 20px;">SOCIAL MEDIA PRIVACY</span>
            <span style="margin: 0 20px; color: #e8ff47;">&bull; AI DEEPFAKE DEFENSE</span>
            <span style="margin: 0 20px;">SAFE BROWSING HABITS</span>
            <span style="margin: 0 20px; color: #ffffff;">&bull; ZERO PASSWORDS REQUIRED</span>
            <span style="margin: 0 20px;">POWERED BY GPT-5</span>
            <span style="margin: 0 20px; color: #e8ff47; font-weight: bold;">&bull; INTERACTIVE LEARNING</span>
            <span style="margin: 0 20px;">PHISHING DETECTION</span>
            <span style="margin: 0 20px; color: #ff6b35;">&bull; PASSWORD SECURITY</span>
            <span style="margin: 0 20px;">SOCIAL MEDIA PRIVACY</span>
            <span style="margin: 0 20px; color: #e8ff47;">&bull; AI DEEPFAKE DEFENSE</span>
            <span style="margin: 0 20px;">SAFE BROWSING HABITS</span>
            <span style="margin: 0 20px; color: #ffffff;">&bull; ZERO PASSWORDS REQUIRED</span>
            <span style="margin: 0 20px;">POWERED BY GPT-5</span>
        </div>
    </div>
    """
    if hasattr(st, "html"):
        st.html(marquee_html)
    else:
        st.markdown(marquee_html, unsafe_allow_html=True)


def render_footer() -> None:
    """Renders the standard platform footer with NIST compliance notice."""
    footer_html = """
    <footer style="margin-top: 80px; padding: 40px 0 20px 0; border-top: 1px solid rgba(255, 255, 255, 0.06); text-align: center; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">
        <div style="display: flex; align-items: center; justify-content: center; gap: 8px; margin-bottom: 12px;">
            <div style="width: 8px; height: 8px; border-radius: 50%; background: #e8ff47;"></div>
            <span style="color: #ffffff; font-weight: bold; font-family: 'Clash Display', sans-serif; letter-spacing: 0.05em;">CYBERSHIELD DEFENSE PLATFORM</span>
        </div>
        <p style="margin: 0 0 6px 0;">Certified K-12 Cybersecurity Curriculum &bull; NIST SP 800-181 Aligned &bull; Dual Architecture</p>
        <p style="margin: 0; color: #666680;">&copy; 2026 CyberSimulator Threat Laboratory. All simulation drills encrypted.</p>
    </footer>
    """
    if hasattr(st, "html"):
        st.html(footer_html)
    else:
        st.markdown(footer_html, unsafe_allow_html=True)
