# Changelog

All notable changes to ProductivityAnalyzer are documented here.

Format based on [Keep a Changelog](https://keepachangelog.com/) and [Conventional Commits](https://www.conventionalcommits.org/).

---

## [2.0.0] - 2026-03-26

### Complete Rewrite from v1.0

#### Architecture
- **Clean layered architecture**: config / database / tracking / reporting / services / ui / utils
- **Repository pattern**: Dedicated repository classes for each database table
- **Dependency injection**: Database pool passed to all components
- **Configuration management**: Environment-based config via `.env` + `python-dotenv`
- **Data models**: Typed dataclasses replace raw tuples throughout the codebase
- **Migration system**: Versioned schema migrations with rollback tracking

#### Core Features
- **Activity Tracking**: Background QThread tracks active window with intelligent categorization
- **App Categorizer**: Rules-based engine classifies apps as productive/unproductive/neutral/idle
- **Focus Mode**: Block distracting apps (minimize) and websites (hosts file) during sessions
- **Goal Setting**: Create daily/weekly/monthly goals with progress bars and completion tracking
- **Productivity Scoring**: Weighted algorithm calculates daily score (0-100) with letter grades

#### Analytics & Reporting
- **Dashboard**: Real-time stat cards, pie chart, trend chart, and suggestion cards
- **Weekly Trend**: 7-day productivity score line chart with productive/unproductive bars
- **Monthly Trend**: 30-day view of productivity patterns
- **Quarterly Trend**: 90-day weekly aggregated view for long-term analysis
- **Activity Bar Chart**: Daily activity breakdown by category
- **Meeting Overload Detection**: Detects Zoom/Teams/Meet usage and warns about excessive meetings
- **CSV Export**: Export activity data for any date range
- **PDF Export**: Professional daily report with summary table and score

#### AI & Integrations
- **Suggestion Engine**: Rule-based smart recommendations with burnout alerts and trend analysis
- **LLM Summaries** (optional): OpenAI-powered natural language daily summaries with graceful fallback
- **Natural Language Queries** (basic): Keyword-based query handler with LLM upgrade path
- **GitHub Integration** (optional): Commit analytics via GitHub REST API (no OAuth required)
- **Sentry Integration** (optional): Error tracking for production monitoring

#### User Interface
- **Sidebar Navigation**: 6-page layout (Dashboard, Activity Log, Focus Mode, Reports, Goals, Settings)
- **Professional Light Theme**: Clean, minimalist design with subtle gradients
- **Professional Dark Theme**: Deep immersive theme, easy on the eyes
- **One-Click Theme Toggle**: Switch themes from Settings page
- **System Tray**: Notifications, break reminders, and quick access menu
- **Responsive Cards**: Stat cards, goal cards, suggestion cards with priority-based styling

#### Database
- **PostgreSQL Only**: Removed all SQLite usage, standardized on PostgreSQL
- **Connection Pooling**: `psycopg2.SimpleConnectionPool` with context manager
- **Schema Migration 001**: Initial schema (6 tables, 6 indexes, seed data)
- **Schema Migration 002**: Soft delete support (`deleted_at` columns)
- **Proper Indexing**: Indexes on timestamp, category, date, active status

#### Testing & Quality
- **57 Unit + Integration Tests**: Pytest with coverage reporting
- **Test Coverage**: 42% (non-UI business logic)
- **Integration Tests**: Full workflow tests (categorizer -> reporting -> suggestions)
- **E2E Widget Tests**: pytest-qt based UI component tests (skipped in headless CI)
- **Linting**: Ruff with project-specific rule configuration
- **Formatting**: Black (line-length: 110)
- **Type Checking**: MyPy with strict mode on business logic
- **Security Audit**: pip-audit in CI pipeline

#### DevOps
- **GitHub Actions CI**: Lint, type check, test, security audit, Docker build
- **Multi-platform CI**: Tests run on Ubuntu + Windows, Python 3.11/3.12/3.13
- **Docker**: Multi-stage Dockerfile for minimal image size
- **Docker Compose**: Development environment with local PostgreSQL
- **PyInstaller**: Build configuration for standalone `.exe` distribution
- **Structured Logging**: Rotating file handler with console output

#### Documentation
- **README.md**: Comprehensive guide with badges, architecture diagram, setup instructions
- **CONTRIBUTING.md**: Development workflow, code style, testing guidelines
- **CHANGELOG.md**: Full version history
- **Architecture Decision Records**: ADR-001 (PyQt5), ADR-002 (PostgreSQL), ADR-003 (Repository Pattern)

#### Security
- **No hardcoded credentials**: All secrets in `.env` (git-ignored)
- **Input validation**: All user inputs validated before processing
- **Connection management**: Context managers prevent connection leaks
- **Dependency auditing**: pip-audit in CI pipeline
- **Safe file handling**: Proper encoding, permission checks, error handling

#### Fixed (from v1.0)
- Double `QApplication` instantiation causing crash
- PostgreSQL and SQLite mixed usage across modules
- File handling bugs in website blocker (`with` block scope)
- Thread safety violations (`QApplication.processEvents()` from background thread)
- Connection leaks in database operations
- Class name collisions (`ProductivityAnalyzerApp` in two files)
- Inconsistent table names (`activity_log` vs `activity_logs`)
- Hardcoded file paths (Windows-only `HOSTS_PATH`)
- Broken async/await with Qt event loop
- `AUTOINCREMENT` SQLite syntax in PostgreSQL class

#### Removed
- All SQLite dependencies and direct `sqlite3` usage
- Hardcoded database credentials from source code
- Unused dependencies: FastAPI, uvicorn, docker, lightning_sdk, starlette, etc.
- Empty/dead files: `oo.py`
- Broken async patterns: `asyncio.new_event_loop()` in Qt context
- `print()` statements: Replaced with structured logging

---

## [1.0.0] - 2024-09-01

### Initial Release
- Basic activity tracking using `pygetwindow`
- Simple PyQt5 UI with single window
- Mixed PostgreSQL and SQLite database access
- Basic focus mode (website blocking via hosts file)
- Matplotlib charts (bar chart only)
- Manual report export to CSV