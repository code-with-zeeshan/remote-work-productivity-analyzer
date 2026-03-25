<div align="center">

# ProductivityAnalyzer v2.0

**A powerful desktop application that tracks and analyzes your work activity to boost productivity.**

[![CI Pipeline](https://github.com/code-with-zeeshan/remote-work-productivity-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/code-with-zeeshan/remote-work-productivity-analyzer/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/badge/linting-ruff-261230.svg)](https://github.com/astral-sh/ruff)
[![Tests: 57 passed](https://img.shields.io/badge/tests-57%20passed-brightgreen.svg)](#testing)
[![Coverage: 42%](https://img.shields.io/badge/coverage-42%25-yellow.svg)](#testing)

</div>

---

## Features

| Feature | Description |
|---|---|
| **Smart Dashboard** | Real-time productivity score, trends, and daily summaries |
| **Focus Mode** | Block distracting apps and websites during work sessions |
| **Activity Tracking** | Automatic window tracking with intelligent categorization |
| **Goal Setting** | Set daily/weekly/monthly productivity goals with progress tracking |
| **Visual Reports** | Pie charts, trend lines (weekly/monthly/quarterly), and activity bar charts |
| **AI Suggestions** | Smart recommendations, burnout alerts, meeting overload detection |
| **LLM Summaries** | Optional AI-powered daily summaries via OpenAI (graceful fallback) |
| **GitHub Integration** | Optional commit analytics to correlate coding output with productivity |
| **Export Reports** | Export to CSV and PDF formats |
| **Dark Mode** | Professional light and dark themes with one-click toggle |
| **Notifications** | System tray notifications with break reminders and goal alerts |
| **Sentry Integration** | Optional error tracking for production monitoring |

---

## Architecture

```
ProductivityAnalyzer/
├── config/              # Configuration, constants, .env management
├── database/            # Connection pool, models, repositories, migrations
│   ├── repositories/    # CRUD operations (activity, goals, focus settings)
│   └── migrations/      # Schema versioning (001_initial, 002_soft_deletes)
├── tracking/            # Activity tracker, focus mode, website blocker, categorizer
├── reporting/           # Report generation, charts (pie, bar, trend), exporters (CSV, PDF)
├── services/            # Scoring, notifications, suggestion engine, LLM, GitHub integration
│   └── integrations/    # Third-party integrations (GitHub)
├── ui/                  # PyQt5 main window, 6 page widgets, QSS themes
│   ├── widgets/         # Dashboard, Activity Log, Focus Mode, Reports, Goals, Settings
│   └── styles/          # Light theme + Dark theme (style.qss, dark_theme.qss)
├── utils/               # Logger, cross-platform helpers, validators
├── tests/               # 57 tests (unit + integration)
│   ├── test_database/   # Repository tests
│   ├── test_tracking/   # Categorizer, website blocker tests
│   ├── test_reporting/  # Report generator tests
│   ├── test_integration/# Full workflow integration tests
│   └── test_ui/         # Validator tests + E2E widget tests
├── docs/adr/            # Architecture Decision Records
├── .github/workflows/   # CI/CD pipeline (lint, test, security, docker)
└── main.py              # Application entry point
```

---

## Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL database (local or remote — e.g., Aiven, Supabase, Neon)

### Installation

```bash
# Clone the repository
git clone https://github.com/code-with-zeeshan/remote-work-productivity-analyzer.git
cd remote-work-productivity-analyzer/ProductivityAnalyzer

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate       # Windows
# source venv/bin/activate    # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Create directories
mkdir assets exports logs      # Linux/Mac
# On Windows PowerShell:
# New-Item -ItemType Directory -Force -Path assets, exports, logs

# Run the application
python main.py
```

### Optional Integrations

| Integration | Setup |
|---|---|
| **GitHub Analytics** | Add `GITHUB_USERNAME` and `GITHUB_TOKEN` to `.env` |
| **AI Summaries** | Add `OPENAI_API_KEY` to `.env` and `pip install openai` |
| **Error Tracking** | Add `SENTRY_DSN` to `.env` (get from sentry.io) |

---

## Testing

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests with coverage
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/test_database/ -v       # Database repo tests
python -m pytest tests/test_tracking/ -v        # Tracking & categorizer tests
python -m pytest tests/test_reporting/ -v       # Report generation tests
python -m pytest tests/test_integration/ -v     # Integration workflow tests
python -m pytest tests/test_ui/ -v              # Validator & widget tests

# Code quality checks
ruff check .              # Linting
black --check .           # Format check
mypy config database tracking reporting services utils --ignore-missing-imports  # Type check

# Security audit
pip-audit --strict
```

### Test Summary

```
57 passed, 3 skipped (GUI tests need display)
Coverage: 42% (non-UI code)
```

---

## Productivity Score

Your score is calculated based on time spent in categorized activities:

| Grade | Score | Meaning |
|---|---|---|
| A+ | 90-100 | Exceptional productivity |
| A | 80-89 | Great focus |
| B | 70-79 | Good, room to improve |
| C | 60-69 | Average |
| D | 50-59 | Below average |
| F | 0-49 | Needs improvement |

### How Categories Work

| Category | Examples | Effect on Score |
|---|---|---|
| **Productive** | VS Code, PyCharm, GitHub, Terminal | Boosts score |
| **Unproductive** | YouTube, Facebook, Reddit, Netflix | Lowers score |
| **Neutral** | Chrome, Slack, Outlook, Zoom | Slight positive |
| **Idle** | No active window, screen locked | No effect |

You can customize category rules from **Settings > App Categories**.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.13 |
| **UI Framework** | PyQt5 5.15 |
| **Database** | PostgreSQL + psycopg2 (connection pooling) |
| **Charts** | Matplotlib (pie, bar, trend line) |
| **PDF Export** | ReportLab |
| **AI (Optional)** | OpenAI GPT-3.5 Turbo |
| **Error Tracking** | Sentry SDK (optional) |
| **Testing** | Pytest + pytest-cov + pytest-qt |
| **Linting** | Ruff |
| **Formatting** | Black |
| **Type Checking** | MyPy |
| **CI/CD** | GitHub Actions |
| **Containerization** | Docker + Docker Compose |

---

## Building Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build standalone .exe
pyinstaller build_exe.spec

# Output will be in dist/ProductivityAnalyzer.exe
```

---

## Project Roadmap

- [x] **v1.0** — Basic activity tracking with PyQt5
- [x] **v2.0** — Complete rewrite with clean architecture
  - [x] Repository pattern with PostgreSQL
  - [x] Intelligent activity categorization
  - [x] Focus mode with app/website blocking
  - [x] Goal setting and tracking
  - [x] Visual reports (pie, bar, trend)
  - [x] CSV and PDF export
  - [x] AI suggestion engine with burnout detection
  - [x] Meeting overload detection
  - [x] Monthly and quarterly trend analysis
  - [x] Dark mode theme
  - [x] System tray notifications
  - [x] GitHub commit analytics integration
  - [x] LLM-powered summaries (optional)
  - [x] Soft delete support
  - [x] CI/CD with GitHub Actions
  - [x] Docker support
  - [x] 57 automated tests
- [ ] **v3.0** (Future)
  - [ ] Google Calendar integration
  - [ ] Toggl/Clockify integration
  - [ ] Team features with RBAC
  - [ ] PyQt6 migration

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.

## Architecture Decisions

See [docs/adr/](ProductivityAnalyzer/docs/adr/) for Architecture Decision Records.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Contact

**Mohammad Zeeshan** — [LinkedIn](https://www.linkedin.com/in/mohammad-zeeshan-37637a1a5)

---

<div align="center">
Made with dedication for productivity enthusiasts
</div>