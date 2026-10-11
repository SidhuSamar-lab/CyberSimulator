"""
CyberSimulator - Educator Analytics & Telemetry Service.
Computes platform analytics, student progress metrics, and CSV audit reports.
"""
import io
import csv
from typing import Dict, List, Any, Optional
from django.db.models import Avg, Count
from users.models import Student
from quizzes.models import QuizAttempt
from quizzes.topics import CYBER_TOPICS, get_topic_by_id


class AnalyticsService:
    """Service providing aggregated telemetry for educators and student dashboards."""

    @classmethod
    def get_teacher_overview_metrics(cls) -> Dict[str, Any]:
        """
        Computes high-level class metrics for the Teacher Dashboard.
        Uses single aggregation queries for optimal performance.
        """
        total_students = Student.objects.count()
        total_attempts = QuizAttempt.objects.count()
        attempts = QuizAttempt.objects.all()

        if not attempts.exists():
            return {
                "total_students": total_students,
                "total_attempts": 0,
                "average_score": 0.0,
                "pass_rate": 0.0,
                "weakest_topic": "None (No drills recorded yet)",
                "weakest_topic_id": "",
                "grade_breakdown": {},
                "topic_analytics": [],
            }

        # Average score and pass rate
        total_score_sum = sum(a.score for a in attempts)
        total_possible_sum = sum(a.total_questions for a in attempts)
        avg_score = round((total_score_sum / total_possible_sum * 100), 1) if total_possible_sum > 0 else 0.0

        passed_count = sum(1 for a in attempts if (a.score / a.total_questions) >= 0.66 if a.total_questions > 0)
        pass_rate = round((passed_count / total_attempts * 100), 1) if total_attempts > 0 else 0.0

        # Grade / Class breakdown
        grade_breakdown: Dict[str, int] = {}
        for s in Student.objects.values('class_name').annotate(cadet_count=Count('id')):
            grade_breakdown[s['class_name']] = s['cadet_count']

        # Topic-level performance
        topic_stats: Dict[str, Dict[str, Any]] = {}
        for t in CYBER_TOPICS:
            topic_stats[t["id"]] = {
                "id": t["id"],
                "title": t["title"],
                "icon": t.get("icon", "shield"),
                "attempts_count": 0,
                "total_score": 0,
                "total_possible": 0,
                "passed_count": 0,
            }

        for a in attempts:
            t_id = a.topic_id
            if t_id not in topic_stats:
                topic_stats[t_id] = {
                    "id": t_id,
                    "title": a.topic_title or t_id,
                    "icon": "shield",
                    "attempts_count": 0,
                    "total_score": 0,
                    "total_possible": 0,
                    "passed_count": 0,
                }
            topic_stats[t_id]["attempts_count"] += 1
            topic_stats[t_id]["total_score"] += a.score
            topic_stats[t_id]["total_possible"] += a.total_questions
            if a.total_questions > 0 and (a.score / a.total_questions) >= 0.66:
                topic_stats[t_id]["passed_count"] += 1

        topic_analytics = []
        for t_id, st in topic_stats.items():
            t_possible = st["total_possible"]
            t_avg = round((st["total_score"] / t_possible * 100), 1) if t_possible > 0 else 0.0
            t_att = st["attempts_count"]
            t_pass_rate = round((st["passed_count"] / t_att * 100), 1) if t_att > 0 else 0.0
            topic_analytics.append({
                **st,
                "average_score": t_avg,
                "pass_rate": t_pass_rate,
            })

        # Identify weakest topic among those with attempts
        attempted_topics = [t for t in topic_analytics if t["attempts_count"] > 0]
        if attempted_topics:
            weakest = min(attempted_topics, key=lambda x: x["average_score"])
            weakest_topic_title = f"{weakest['title']} ({weakest['average_score']}% avg)"
            weakest_topic_id = weakest["id"]
        else:
            weakest_topic_title = "None (No attempts recorded)"
            weakest_topic_id = ""

        return {
            "total_students": total_students,
            "total_attempts": total_attempts,
            "average_score": avg_score,
            "pass_rate": pass_rate,
            "weakest_topic": weakest_topic_title,
            "weakest_topic_id": weakest_topic_id,
            "grade_breakdown": grade_breakdown,
            "topic_analytics": topic_analytics,
        }

    @classmethod
    def get_student_curriculum_progress(cls, student: Student) -> Dict[str, Any]:
        """
        Calculates curriculum progress, mastery state, and topic breakdown for a single student.
        """
        attempts = list(student.attempts.all())
        attempts_by_topic: Dict[str, List[QuizAttempt]] = {}
        for a in attempts:
            attempts_by_topic.setdefault(a.topic_id, []).append(a)

        total_topics = len(CYBER_TOPICS)
        topics_with_progress = []

        for t in CYBER_TOPICS:
            t_id = t["id"]
            t_attempts = attempts_by_topic.get(t_id, [])
            has_attempts = len(t_attempts) > 0
            best_score = max((a.score for a in t_attempts), default=0)
            best_total = max((a.total_questions for a in t_attempts), default=3)
            best_pct = int((best_score / best_total) * 100) if best_total > 0 else 0
            is_completed = (best_pct >= 66)

            topics_with_progress.append({
                **t,
                "has_attempts": has_attempts,
                "attempts_count": len(t_attempts),
                "best_score": best_score,
                "best_total": best_total,
                "best_percentage": best_pct,
                "is_completed": is_completed,
            })

        completed_count = sum(1 for t in topics_with_progress if t["is_completed"])
        completion_percentage = int((completed_count / total_topics) * 100) if total_topics > 0 else 0
        active_count = sum(1 for t in topics_with_progress if not t["is_completed"])
        pending_count = sum(1 for t in topics_with_progress if not t["has_attempts"])

        return {
            "total_topics": total_topics,
            "completed_count": completed_count,
            "completion_percentage": completion_percentage,
            "active_count": active_count,
            "pending_count": pending_count,
            "topics": topics_with_progress,
        }

    @classmethod
    def generate_csv_telemetry_export(cls) -> str:
        """
        Generates CSV audit report of all student attempts across the institution.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "Attempt ID",
            "Student Name",
            "Roll Number",
            "Class",
            "Topic ID",
            "Topic Title",
            "Score",
            "Total Questions",
            "Accuracy %",
            "Status",
            "Date (UTC)",
        ])

        attempts = QuizAttempt.objects.select_related('student').order_by('-completed_at')
        for a in attempts:
            pct = round((a.score / a.total_questions * 100), 1) if a.total_questions > 0 else 0.0
            status = "Mastered" if pct >= 66.0 else "In Progress"
            writer.writerow([
                a.id,
                a.student.name if a.student else "Unknown",
                a.student.roll_number if a.student else "N/A",
                a.student.class_name if a.student else "N/A",
                a.topic_id,
                a.topic_title,
                a.score,
                a.total_questions,
                f"{pct}%",
                status,
                a.completed_at.strftime("%Y-%m-%d %H:%M:%S") if a.completed_at else "",
            ])

        return output.getvalue()

    @classmethod
    def get_leaderboard_data(cls) -> Dict[str, Any]:
        """
        Calculates ranked class performance and individual student honor roll.
        """
        all_students = list(Student.objects.all().prefetch_related('attempts'))

        class_groups: Dict[str, List[Student]] = {}
        for s in all_students:
            class_groups.setdefault(s.class_name, []).append(s)

        class_stats = []
        for c_name, members in class_groups.items():
            total_attempts = sum(m.total_attempts for m in members)
            avg_acc = round(sum(m.average_score for m in members) / len(members), 1) if members else 0.0
            class_stats.append({
                'class_name': c_name,
                'student_count': len(members),
                'total_attempts': total_attempts,
                'avg_accuracy': avg_acc,
            })
        class_stats.sort(key=lambda x: x['avg_accuracy'], reverse=True)

        ranked_students = sorted(all_students, key=lambda s: (s.total_score, s.average_score), reverse=True)

        return {
            'class_rankings': class_stats,
            'student_rankings': ranked_students,
        }
