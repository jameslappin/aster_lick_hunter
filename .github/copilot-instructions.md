# Copilot Instructions for Aster Liquidation Hunter Bot

This guide enables AI coding agents to work productively in this codebase. It summarizes architecture, workflows, conventions, and integration points unique to this project.

## Project Overview
- **Purpose:** Automated trading bot for Aster DEX, executing counter-trades on liquidation events. Includes a Flask-based web dashboard for monitoring and configuration.
- **Main entry points:**
  - `main.py` — Bot only
  - `launcher.py` — Bot + dashboard orchestrator
  - `src/api/api_server.py` — Dashboard API only

## Architecture & Data Flow
- **Core logic:**
  - `src/core/streamer.py` — WebSocket liquidation stream
  - `src/core/trader.py` — Trading logic, order management
  - `src/core/order_cleanup.py` — Stale order cleanup
  - `src/core/user_stream.py` — User data WebSocket
- **API & dashboard:**
  - `src/api/api_server.py` — Flask REST API, SSE events
  - `src/api/routes/` — REST endpoints for dashboard
  - `src/api/pnl_tracker.py` — P&L calculations
- **Database:**
  - `src/database/db.py` — SQLite operations
  - `src/database/auto_migrate.py` — Schema migration
- **Utilities:**
  - `src/utils/colored_logger.py` — Colored logging
  - `src/utils/auth.py` — HMAC API authentication
  - `src/utils/config.py` — Configuration management

## Configuration & Secrets
- **Trading parameters:**
  - `settings.json` — Main config (see README for schema)
  - `src/utils/config.py` — Loads and validates config
- **Secrets:**
  - `.env` (not in repo) — API credentials

## Developer Workflows
- **Install dependencies:**
  - `pip install -r requirements.txt`
- **Run bot and dashboard:**
  - `python launcher.py`
- **Run tests:**
  - `python -m pytest tests/`
  - Coverage: `python -m pytest --cov=src tests/`
- **Database migration/init:**
  - `python scripts/init_database.py`
  - `python scripts/migrate_db.py`
- **Simulation mode:**
  - Set `simulate_only: true` in `settings.json`

## Patterns & Conventions
- **Tranche system:**
  - Positions split/merged by PnL thresholds (see `src/core/trader.py`)
- **Order lifecycle:**
  - Stale orders cleaned by `order_cleanup.py`
- **WebSocket streams:**
  - Liquidation: `wss://fstream.asterdex.com/stream?streams=!forceOrder@arr`
- **REST API:**
  - Endpoints in `src/api/routes/` (see README for table)
- **Logging:**
  - Use `colored_logger.py` for all console output
- **Error handling:**
  - Comprehensive try/except, logs errors, and clean shutdown

## Integration Points
- **Aster DEX API:**
  - All trading and data via Aster DEX endpoints
- **Dashboard:**
  - Accessible at `http://localhost:5000` when running dashboard
- **Database:**
  - SQLite file managed by `src/database/db.py`

## Examples
- **Add a new trading symbol:**
  - Update `settings.json` under `symbols` key
- **Add a new REST endpoint:**
  - Create route in `src/api/routes/`, register in `api_server.py`
- **Extend tranche logic:**
  - Modify `src/core/trader.py` and related utils

## References
- See `README.md` and `CLAUDE.md` for further details and examples.

---
*Update this file as project conventions evolve. For unclear or missing sections, ask maintainers for clarification.*
