"""
CyberSimulator - Classroom Leaderboard Page Component.
Displays class rankings, top 3 podium cards, and student honor roll.
"""
import html
from typing import Optional, List
import streamlit as st
from users.models import Student
from quizzes.services.analytics_service import AnalyticsService
from streamlit_ui.styles import render_html


def render_leaderboard(all_students: Optional[List[Student]] = None) -> None:
    """Renders the 1:1 leaderboard matching leaderboard.html."""
    render_html("""
    <div class="nexus-card" style="text-align: center; padding: 36px 20px; margin-bottom: 32px; position: relative; overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #e8ff47, #b8cc38, #e8ff47);"></div>
        <div class="cyber-pill cyber-pill-signal" style="margin-bottom: 12px;">
            <span style="width: 6px; height: 6px; background: #e8ff47; border-radius: 50%;"></span>
            <span>CLASS STANDINGS</span>
        </div>
        <h1 style="font-size: clamp(2.4rem, 5vw, 4rem); font-weight: 700; margin: 4px 0 10px 0;">
            Classroom Leaderboard
        </h1>
        <p style="color: #9898b8; max-width: 600px; margin: 0 auto; font-size: 0.95rem; line-height: 1.6;">
            Compare class performance, celebrate student achievements, and track rankings across all classes.
        </p>
    </div>
    """)

    # Delegate all domain aggregation and sorting to AnalyticsService
    leaderboard_data = AnalyticsService.get_leaderboard_data()
    class_stats = leaderboard_data['class_rankings']
    ranked_students = leaderboard_data['student_rankings']

    # Top 3 Podium (1:1 with leaderboard.html)
    if len(class_stats) >= 3:
        render_html("""
        <div style="text-align: center; margin-bottom: 20px;">
            <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; text-transform: uppercase; letter-spacing: 0.15em; font-weight: bold; margin-bottom: 4px;">Top Performing Classes</p>
            <h2 style="font-size: 2rem; font-weight: 700; color: #ffffff; margin: 0;">Class Rankings</h2>
        </div>
        """)

        c1, c2, c3 = st.columns(3)
        with c1:
            render_html(f"""
            <div class="nexus-card" style="border-color: rgba(255, 255, 255, 0.15); text-align: center; padding: 24px;">
                <div style="width: 44px; height: 44px; border-radius: 50%; background: #080812; border: 1px solid rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-weight: bold; margin: 0 auto 12px auto; color: #ffffff;">02</div>
                <div style="color: #9898b8; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em;">2ND PLACE</div>
                <h3 style="margin: 6px 0; font-size: 1.4rem;">{html.escape(class_stats[1]['class_name'])}</h3>
                <div style="background: #080812; border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 14px; margin-top: 12px;">
                    <div style="font-size: 2.2rem; font-weight: 700; color: #ffffff; font-family: 'Clash Display', sans-serif;">{class_stats[1]['avg_accuracy']}%</div>
                    <div style="color: #9898b8; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; margin-top: 4px;">{class_stats[1]['total_attempts']} Quizzes &bull; {class_stats[1]['student_count']} Students</div>
                </div>
            </div>
            """)
        with c2:
            render_html(f"""
            <div class="nexus-card-active" style="border-color: #e8ff47; text-align: center; padding: 28px; transform: scale(1.03);">
                <div style="width: 52px; height: 52px; border-radius: 50%; background: #e8ff47; color: #04040a; display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-weight: 900; margin: 0 auto 12px auto; font-size: 1.15rem; box-shadow: 0 0 15px rgba(232,255,71,0.5);">01</div>
                <div style="color: #e8ff47; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: bold; text-transform: uppercase; letter-spacing: 0.1em;">1ST PLACE</div>
                <h3 style="margin: 6px 0; font-size: 1.6rem; color: #e8ff47;">{html.escape(class_stats[0]['class_name'])}</h3>
                <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8; margin: 0 0 12px 0;">Top Class Score</p>
                <div style="background: #080812; border: 1px solid rgba(232,255,71,0.3); border-radius: 16px; padding: 16px;">
                    <div style="font-size: 2.8rem; font-weight: 700; color: #e8ff47; font-family: 'Clash Display', sans-serif;">{class_stats[0]['avg_accuracy']}%</div>
                    <div style="color: #c4c4d8; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; margin-top: 4px;">{class_stats[0]['total_attempts']} Quizzes &bull; {class_stats[0]['student_count']} Students</div>
                </div>
            </div>
            """)
        with c3:
            render_html(f"""
            <div class="nexus-card" style="border-color: rgba(255, 107, 53, 0.4); text-align: center; padding: 24px;">
                <div style="width: 44px; height: 44px; border-radius: 50%; background: #080812; border: 1px solid rgba(255,107,53,0.4); display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-weight: bold; margin: 0 auto 12px auto; color: #ff6b35;">03</div>
                <div style="color: #ff6b35; font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.1em;">3RD PLACE</div>
                <h3 style="margin: 6px 0; font-size: 1.4rem;">{html.escape(class_stats[2]['class_name'])}</h3>
                <div style="background: #080812; border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 14px; margin-top: 12px;">
                    <div style="font-size: 2.2rem; font-weight: 700; color: #ffffff; font-family: 'Clash Display', sans-serif;">{class_stats[2]['avg_accuracy']}%</div>
                    <div style="color: #9898b8; font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; margin-top: 4px;">{class_stats[2]['total_attempts']} Quizzes &bull; {class_stats[2]['student_count']} Students</div>
                </div>
            </div>
            """)

    # Individual Student Honor Roll Table (Exact 1:1 with leaderboard.html)
    st.markdown("<div style='margin-top: 40px;'></div>", unsafe_allow_html=True)

    table_rows = []
    for rank, s in enumerate(ranked_students, start=1):
        rank_bg = "#e8ff47" if rank == 1 else ("rgba(255,255,255,0.2)" if rank == 2 else ("rgba(255,107,53,0.2)" if rank == 3 else "#080812"))
        rank_color = "#04040a" if rank == 1 else ("#ffffff" if rank == 2 else ("#ff6b35" if rank == 3 else "#9898b8"))
        unlocked = sum(1 for b in s.get_earned_badges() if b['earned'])
        s_initials = s.name[:2].upper() if s.name else "AL"

        table_rows.append(f"""
        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.05); transition: background 0.2s;">
            <td style="padding: 16px 20px; font-family: 'JetBrains Mono', monospace;">
                <span style="width: 28px; height: 28px; border-radius: 50%; background: {rank_bg}; color: {rank_color}; display: inline-flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.75rem;">
                    0{rank}
                </span>
            </td>
            <td style="padding: 16px 20px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    <div style="width: 32px; height: 32px; border-radius: 50%; background: #080812; border: 1px solid rgba(255,255,255,0.15); display: flex; align-items: center; justify-content: center; font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; font-weight: bold; color: #e8ff47;">
                        {s_initials}
                    </div>
                    <span style="font-weight: 700; color: #ffffff; font-size: 0.95rem;">{html.escape(s.name)}</span>
                </div>
            </td>
            <td style="padding: 16px 20px; font-family: 'JetBrains Mono', monospace; color: #c4c4d8; font-size: 0.8rem;">
                {html.escape(s.class_name)} &bull; Roll #{html.escape(s.roll_number)}
            </td>
            <td style="padding: 16px 20px; font-family: 'JetBrains Mono', monospace;">
                <span style="background: rgba(232, 255, 71, 0.12); color: #e8ff47; border: 1px solid rgba(232, 255, 71, 0.3); padding: 3px 10px; border-radius: 9999px; font-size: 0.72rem; font-weight: bold;">
                    {unlocked} Badges
                </span>
            </td>
            <td style="padding: 16px 20px; font-family: 'JetBrains Mono', monospace; color: #c4c4d8; font-size: 0.8rem;">
                {s.total_attempts} / 8 Topics
            </td>
            <td style="padding: 16px 20px; text-align: right; font-family: 'JetBrains Mono', monospace; font-weight: bold; color: #e8ff47; font-size: 1rem;">
                {s.total_score} pts
            </td>
        </tr>
        """)

    render_html(f"""
    <div style="background: #0b0b18; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.5);">
        <div style="padding: 20px 24px; background: #080812; border-bottom: 1px solid rgba(255,255,255,0.06); display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h3 style="margin: 0; font-size: 1.2rem; font-weight: 700;">Student Leaderboard</h3>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8;">Ranked by total quizzes passed and badge mastery</span>
            </div>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #e8ff47; background: #0d0d1f; border: 1px solid rgba(255,255,255,0.1); padding: 3px 10px; border-radius: 9999px;">
                Top {len(ranked_students)} Students
            </span>
        </div>
        <table style="width: 100%; border-collapse: collapse; text-align: left;">
            <thead>
                <tr style="background: #080812; border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #9898b8; text-transform: uppercase; letter-spacing: 0.1em;">
                    <th style="padding: 14px 20px;">RANK</th>
                    <th style="padding: 14px 20px;">STUDENT NAME</th>
                    <th style="padding: 14px 20px;">CLASS & ROLL</th>
                    <th style="padding: 14px 20px;">BADGES</th>
                    <th style="padding: 14px 20px;">QUIZZES TAKEN</th>
                    <th style="padding: 14px 20px; text-align: right;">TOTAL POINTS</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
    </div>
    """)
