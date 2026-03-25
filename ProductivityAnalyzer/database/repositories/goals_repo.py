# database/repositories/goals_repo.py
"""
Repository for goals table operations.
"""

from database.connection import DatabasePool
from database.models import ProductivityGoal
from utils.logger import setup_logger

logger = setup_logger("repo.goals")


class GoalsRepository:
    def __init__(self, db_pool: DatabasePool):
        self.db = db_pool

    def create_goal(self, goal: ProductivityGoal) -> int | None:
        """Create a new goal. Returns the new goal ID."""
        query = """
            INSERT INTO goals (title, target_hours, period, current_progress, is_active, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            RETURNING id
        """
        result = self.db.execute_query_returning(
            query,
            (goal.title, goal.target_hours, goal.period.value, goal.current_progress, goal.is_active),
        )
        if result:
            logger.info(f"Goal created: '{goal.title}' (id={result})")
        return result

    def get_active_goals(self) -> list[ProductivityGoal]:
        """Get all active goals."""
        query = """
            SELECT id, title, target_hours, period, current_progress, is_active, created_at
            FROM goals
            WHERE is_active = TRUE
            ORDER BY created_at DESC
        """
        rows = self.db.fetch_all(query)
        return [ProductivityGoal.from_db_row(row) for row in rows]

    def get_all_goals(self) -> list[ProductivityGoal]:
        """Get all goals including inactive."""
        query = """
            SELECT id, title, target_hours, period, current_progress, is_active, created_at
            FROM goals
            ORDER BY created_at DESC
        """
        rows = self.db.fetch_all(query)
        return [ProductivityGoal.from_db_row(row) for row in rows]

    def get_goal_by_id(self, goal_id: int) -> ProductivityGoal | None:
        """Get a specific goal by ID."""
        query = """
            SELECT id, title, target_hours, period, current_progress, is_active, created_at
            FROM goals
            WHERE id = %s
        """
        row = self.db.fetch_one(query, (goal_id,))
        if row:
            return ProductivityGoal.from_db_row(row)
        return None

    def update_progress(self, goal_id: int, progress_hours: float) -> bool:
        """Update the current progress of a goal."""
        query = "UPDATE goals SET current_progress = %s WHERE id = %s"
        return self.db.execute_query(query, (progress_hours, goal_id))

    def update_goal(self, goal: ProductivityGoal) -> bool:
        """Update all fields of a goal."""
        query = """
            UPDATE goals
            SET title = %s, target_hours = %s, period = %s,
                current_progress = %s, is_active = %s
            WHERE id = %s
        """
        return self.db.execute_query(
            query,
            (
                goal.title,
                goal.target_hours,
                goal.period.value,
                goal.current_progress,
                goal.is_active,
                goal.id,
            ),
        )

    def delete_goal(self, goal_id: int) -> bool:
        """Soft-delete a goal by deactivating it."""
        query = "UPDATE goals SET is_active = FALSE WHERE id = %s"
        return self.db.execute_query(query, (goal_id,))

    def reset_daily_progress(self) -> bool:
        """Reset progress for all daily goals (run at midnight)."""
        query = "UPDATE goals SET current_progress = 0 WHERE period = 'daily' AND is_active = TRUE"
        return self.db.execute_query(query)

    def reset_weekly_progress(self) -> bool:
        """Reset progress for all weekly goals (run on Monday)."""
        query = "UPDATE goals SET current_progress = 0 WHERE period = 'weekly' AND is_active = TRUE"
        return self.db.execute_query(query)
