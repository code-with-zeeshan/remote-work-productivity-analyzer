# ui/widgets/goals_widget.py
"""
Goals page — set, track, and manage productivity goals.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from config.constants import GoalPeriod
from database.connection import DatabasePool
from database.models import ProductivityGoal
from database.repositories.goals_repo import GoalsRepository
from utils.logger import setup_logger
from utils.validators import validate_goal_input

logger = setup_logger("ui.goals")


class GoalCard(QFrame):
    """Individual goal card with progress bar."""

    def __init__(self, goal: ProductivityGoal, on_delete=None, parent=None):
        super().__init__(parent)
        self.goal = goal
        self.setObjectName("card")
        self.setFixedHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        # Header row
        header = QHBoxLayout()
        title = QLabel(f"🏆 {goal.title}")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        header.addWidget(title)

        period_label = QLabel(f"[{goal.period.value.capitalize()}]")
        period_label.setStyleSheet("color: #636e72; font-size: 12px;")
        header.addWidget(period_label)

        header.addStretch()

        progress_text = QLabel(f"{goal.current_progress:.1f} / {goal.target_hours:.1f} hours")
        progress_text.setStyleSheet("font-size: 13px; font-weight: bold; color: #0984e3;")
        header.addWidget(progress_text)

        if on_delete:
            delete_btn = QPushButton("✕")
            delete_btn.setObjectName("dangerButton")
            delete_btn.setFixedSize(30, 30)
            delete_btn.clicked.connect(lambda: on_delete(goal.id))
            header.addWidget(delete_btn)

        layout.addLayout(header)

        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(min(100, int(goal.progress_percentage)))
        progress_bar.setFormat(f"{goal.progress_percentage:.1f}%")

        # Color based on progress
        if goal.progress_percentage >= 100:
            progress_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #00b894; border-radius: 8px; }"
            )
        elif goal.progress_percentage >= 50:
            progress_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #0984e3; border-radius: 8px; }"
            )
        else:
            progress_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #fdcb6e; border-radius: 8px; }"
            )

        layout.addWidget(progress_bar)

        # Status
        if goal.progress_percentage >= 100:
            status = QLabel("✅ Goal Achieved!")
            status.setStyleSheet("color: #00b894; font-weight: bold;")
        else:
            remaining = max(0, goal.target_hours - goal.current_progress)
            status = QLabel(f"📌 {remaining:.1f} hours remaining")
            status.setStyleSheet("color: #636e72; font-size: 11px;")
        layout.addWidget(status)


class GoalsWidget(QWidget):
    """Goals management page."""

    def __init__(self, db_pool: DatabasePool, parent=None):
        super().__init__(parent)
        self.goals_repo = GoalsRepository(db_pool)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        # Header
        title = QLabel("🏆 Goals")
        title.setObjectName("pageTitle")
        layout.addWidget(title)

        subtitle = QLabel("Set productivity goals and track your progress")
        subtitle.setObjectName("pageSubtitle")
        layout.addWidget(subtitle)

        # ── Add Goal Form ──
        form_group = QGroupBox("Add New Goal")
        form_layout = QFormLayout(form_group)

        self.goal_title_input = QLineEdit()
        self.goal_title_input.setPlaceholderText("e.g., Code for 4 hours daily")
        form_layout.addRow("Title:", self.goal_title_input)

        self.target_hours_input = QDoubleSpinBox()
        self.target_hours_input.setRange(0.5, 24.0)
        self.target_hours_input.setValue(4.0)
        self.target_hours_input.setSuffix(" hours")
        self.target_hours_input.setSingleStep(0.5)
        form_layout.addRow("Target:", self.target_hours_input)

        self.period_input = QComboBox()
        self.period_input.addItems(["Daily", "Weekly", "Monthly"])
        form_layout.addRow("Period:", self.period_input)

        add_button = QPushButton("➕ Add Goal")
        add_button.setObjectName("successButton")
        add_button.clicked.connect(self._add_goal)
        form_layout.addRow("", add_button)

        layout.addWidget(form_group)

        # ── Active Goals List ──
        goals_header = QHBoxLayout()
        goals_label = QLabel("Active Goals")
        goals_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        goals_header.addWidget(goals_label)
        goals_header.addStretch()

        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("secondaryButton")
        refresh_btn.clicked.connect(self.refresh_data)
        goals_header.addWidget(refresh_btn)
        layout.addLayout(goals_header)

        # Scrollable goals list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.goals_container_widget = QWidget()
        self.goals_list_layout = QVBoxLayout(self.goals_container_widget)
        self.goals_list_layout.setSpacing(10)
        self.goals_list_layout.addStretch()

        scroll.setWidget(self.goals_container_widget)
        layout.addWidget(scroll, 1)

    def refresh_data(self):
        """Reload goals from database."""
        # Clear existing cards
        while self.goals_list_layout.count() > 1:  # Keep the stretch
            item = self.goals_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        goals = self.goals_repo.get_active_goals()

        if not goals:
            no_goals = QLabel("No active goals. Add one above to get started! 🎯")
            no_goals.setStyleSheet("color: #636e72; font-size: 14px; padding: 20px;")
            no_goals.setAlignment(Qt.AlignCenter)
            self.goals_list_layout.insertWidget(0, no_goals)
        else:
            for goal in goals:
                card = GoalCard(goal, on_delete=self._delete_goal)
                self.goals_list_layout.insertWidget(self.goals_list_layout.count() - 1, card)

        logger.debug(f"Goals refreshed: {len(goals)} active goals")

    def _add_goal(self):
        """Validate and add a new goal."""
        title = self.goal_title_input.text().strip()
        target = str(self.target_hours_input.value())

        valid, error = validate_goal_input(title, target)
        if not valid:
            QMessageBox.warning(self, "Invalid Input", error)
            return

        period_map = {"Daily": GoalPeriod.DAILY, "Weekly": GoalPeriod.WEEKLY, "Monthly": GoalPeriod.MONTHLY}
        period = period_map.get(self.period_input.currentText(), GoalPeriod.DAILY)

        goal = ProductivityGoal(
            title=title,
            target_hours=float(target),
            period=period,
        )

        result = self.goals_repo.create_goal(goal)
        if result:
            self.goal_title_input.clear()
            self.target_hours_input.setValue(4.0)
            self.refresh_data()
            QMessageBox.information(self, "Success", f"Goal '{title}' created! 🎯")
        else:
            QMessageBox.warning(self, "Error", "Failed to create goal.")

    def _delete_goal(self, goal_id: int):
        """Delete a goal after confirmation."""
        reply = QMessageBox.question(
            self,
            "Delete Goal",
            "Are you sure you want to delete this goal?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            self.goals_repo.delete_goal(goal_id)
            self.refresh_data()
