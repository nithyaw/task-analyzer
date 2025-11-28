from datetime import date, timedelta
from django.test import TestCase

from .scoring import calculate_task_score


class ScoringTests(TestCase):
    def test_overdue_task_has_higher_score_than_future(self):
        today = date.today()
        overdue = {
            "title": "Overdue",
            "due_date": (today - timedelta(days=2)).strftime("%Y-%m-%d"),
            "estimated_hours": 2,
            "importance": 5,
            "dependencies": [],
        }
        future = {
            "title": "Future",
            "due_date": (today + timedelta(days=5)).strftime("%Y-%m-%d"),
            "estimated_hours": 2,
            "importance": 5,
            "dependencies": [],
        }

        score_overdue, _ = calculate_task_score(overdue, strategy="smart_balance")
        score_future, _ = calculate_task_score(future, strategy="smart_balance")

        self.assertGreater(score_overdue, score_future)

    def test_missing_importance_defaults_to_5(self):
        today = date.today()
        task = {
            "title": "No importance",
            "due_date": (today + timedelta(days=1)).strftime("%Y-%m-%d"),
            "estimated_hours": 2,
            # importance missing
            "dependencies": [],
        }

        score, explanation = calculate_task_score(task, strategy="smart_balance")
        self.assertIn("Importance 5 ×", explanation)

    def test_fastest_wins_prefers_quick_task(self):
        today = date.today()
        quick = {
            "title": "Quick",
            "due_date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            "estimated_hours": 1,
            "importance": 5,
            "dependencies": [],
        }
        long = {
            "title": "Long",
            "due_date": (today + timedelta(days=2)).strftime("%Y-%m-%d"),
            "estimated_hours": 8,
            "importance": 5,
            "dependencies": [],
        }

        score_quick, _ = calculate_task_score(quick, strategy="fastest_wins")
        score_long, _ = calculate_task_score(long, strategy="fastest_wins")

        self.assertGreater(score_quick, score_long)