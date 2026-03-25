# Contributing to ProductivityAnalyzer

Thank you for your interest in contributing! Here's how to get started.

---

## Development Setup

1. **Fork** the repository on GitHub
2. **Clone** your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/remote-work-productivity-analyzer.git
   cd remote-work-productivity-analyzer/ProductivityAnalyzer
   ```
3. **Create virtual environment** and install dev dependencies:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate          # Windows
   # source venv/bin/activate       # Linux/Mac

   pip install -r requirements-dev.txt
   ```
4. **Create `.env`** from template:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

---

## Development Workflow

1. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the code style below

3. **Run all quality checks** before committing:
   ```bash
   # Auto-fix lint issues
   ruff check . --fix

   # Format code
   black .

   # Type check
   mypy config database tracking reporting services utils --ignore-missing-imports

   # Run tests
   python -m pytest tests/ -v
   ```

4. **Commit** using conventional commit messages:
   ```
   feat: add weekly email report
   fix: resolve database connection leak on focus mode end
   docs: update README with Docker instructions
   test: add categorizer edge case tests
   refactor: simplify report generator scoring logic
   style: apply Black formatting to tracking module
   chore: update dependencies in requirements.txt
   ```

5. **Push** and create a **Pull Request** against `main`

---

## Code Style

| Tool | Purpose | Config |
|---|---|---|
| **Black** | Code formatting | `pyproject.toml` — line-length: 110 |
| **Ruff** | Linting | `pyproject.toml` — custom rule selection |
| **MyPy** | Type checking | `pyproject.toml` — `check_untyped_defs = true` |

### Key Style Rules

- **Line length**: 110 characters (Black handles this)
- **Imports**: Sorted by Ruff's isort integration (stdlib > third-party > local)
- **Type hints**: Required on all public function signatures
- **Docstrings**: Required for all classes and public methods
- **No `print()`**: Use `logger.info()` / `logger.error()` from `utils.logger`
- **No hardcoded values**: Use `config/settings.py` or `config/constants.py`
- **File encoding**: Always `encoding="utf-8"` when opening files

### Ruff Rules Note

Some rules are intentionally disabled in `pyproject.toml`:
- `DTZ*` — Timezone-aware datetime is unnecessary for a local desktop app
- `RUF001` — We use emojis intentionally in UI labels
- `N802` — Qt override methods like `closeEvent` cannot be renamed

---

## Testing Guidelines

### Structure

```
tests/
├── conftest.py                  # Shared fixtures (mock_db_pool, sample data)
├── test_database/               # Repository CRUD tests
├── test_tracking/               # Categorizer, website blocker tests
├── test_reporting/              # Report generator tests
├── test_integration/            # Full workflow tests (multi-component)
└── test_ui/                     # Validator tests + E2E widget tests
```

### Rules

- Write tests for **all new features**
- Use fixtures from `conftest.py` for shared test data
- **Mock external dependencies** (database, file system, network)
- **Integration tests** go in `tests/test_integration/`
- **UI widget tests** use `pytest-qt` and are skipped in headless CI
- Target **coverage >= 35%** (increasing over time as more tests are added)
- Run `python -m pytest tests/ -v` before every commit

### Running Specific Tests

```bash
python -m pytest tests/test_database/ -v           # Database tests only
python -m pytest tests/test_tracking/ -v            # Tracking tests only
python -m pytest tests/ -k "test_categorize" -v     # Tests matching keyword
python -m pytest tests/ --cov=. --cov-report=html   # Generate HTML coverage
```

---

## Architecture

The project follows a **layered architecture** with clear separation of concerns:

```
UI Layer          →  ui/ (PyQt5 widgets, styles)
Service Layer     →  services/ (scoring, notifications, suggestions, integrations)
Business Layer    →  tracking/ (activity tracker, focus mode, categorizer)
                     reporting/ (report generator, charts, exporters)
Data Layer        →  database/ (connection pool, repositories, models, migrations)
Infrastructure    →  config/ (settings, constants)
                     utils/ (logger, platform utils, validators)
```

### Key Patterns

- **Repository Pattern**: All database access through repository classes
- **Dependency Injection**: `DatabasePool` injected into all components
- **Signal/Slot**: Qt signals for cross-thread communication
- **Context Managers**: Database connections always managed via `with` blocks
- **Factory Methods**: `from_db_row()` on model classes for database deserialization

---

## Reporting Bugs

Open a GitHub Issue with:
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS
- Relevant log output from `logs/productivity_analyzer.log`
- Screenshots (if UI-related)

---

## Feature Requests

Open a GitHub Issue with the `enhancement` label including:
- Description of the feature
- Why it would be useful
- Any mockups or examples (optional)