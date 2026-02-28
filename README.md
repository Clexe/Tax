# NaijaTax Bot

A Telegram bot for Nigerian Personal Income Tax calculation under the **Nigeria Tax Act (NTA) 2025**, effective January 1, 2026.

## Features

- **Salaried employees**: Full PAYE calculation with all NTA 2025 reliefs
- **Self-employed / freelancers**: Net income tax after business expenses
- **PAYE checker**: Compare your tax with what your employer deducts
- **Bilingual**: English and Nigerian Pidgin
- **Tax guidance**: In-app help topics (PAYE, chargeable income, Rent Relief, etc.)
- **Admin dashboard**: Usage stats via `/admin` command

## NTA 2025 Tax Bands

| Band | Chargeable Income | Rate |
|------|-------------------|------|
| 1 | First ₦800,000 | 0% |
| 2 | Next ₦2,200,000 | 15% |
| 3 | Next ₦6,000,000 | 18% |
| 4 | Next ₦4,000,000 | 21% |
| 5 | Next ₦12,000,000 | 23% |
| 6 | Next ₦25,000,000 | 23% |
| 7 | Above ₦50,000,000 | 25% |

**No minimum tax** under NTA 2025.

## Allowable Deductions

| Deduction | Formula | Cap |
|-----------|---------|-----|
| Rent Relief | 20% of annual rent | ₦500,000 |
| Pension | 8% of (basic + housing + transport) | None |
| NHF | 2.5% of annual basic | None |
| NHIS | Actual contribution | None |
| Life Assurance | Actual premium | ₦100,000 |

## Tech Stack

- **Python 3.10+**
- **python-telegram-bot 20.7** (async PTB with ConversationHandlers)
- **aiohttp 3.9** (webhook HTTP server)
- **SQLAlchemy 2.0** + **Alembic** (PostgreSQL in prod, SQLite locally)
- **Railway** (deployment platform)

## Project Structure

```
bot/
├── calculators/
│   ├── nta.py          # NTA 2025 tax band logic (pure functions)
│   ├── reliefs.py      # Deduction calculations (pure functions)
│   └── formatter.py    # HTML result message builder
├── utils/
│   ├── validators.py   # parse_amount() — user input parsing
│   ├── messages.py     # Bilingual message strings
│   └── keyboards.py    # InlineKeyboardMarkup builders
├── database/
│   ├── models.py       # SQLAlchemy 2.0 ORM models
│   └── db.py           # Session factory + helper functions
├── handlers/
│   ├── start.py        # /start, language selection, cancel
│   ├── salaried.py     # 12-state salaried flow
│   ├── selfemployed.py # 7-state self-employed flow
│   ├── checker.py      # 13-state PAYE checker flow
│   ├── help.py         # Stateless help callbacks
│   ├── actions.py      # Post-result action buttons
│   └── admin.py        # /admin stats command
└── main.py             # Bot entry point (webhook + polling)
tests/
├── test_nta.py         # Tax band calculation tests
├── test_reliefs.py     # Relief/deduction tests
└── test_validators.py  # Input parser tests
alembic/                # Database migrations
```

## Local Development

### Prerequisites

- Python 3.10+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

### Setup

```bash
# Clone the repository
git clone <repo-url>
cd Tax

# Install dependencies
pip install -r requirements.txt

# Copy and fill in environment variables
cp .env.example .env
# Edit .env and set BOT_TOKEN (DATABASE_URL is optional for local dev)

# Run in polling mode (no webhook needed locally)
python -m bot.main
```

SQLite (`naijatax_local.db`) is used automatically when `DATABASE_URL` is not set.

### Running Tests

```bash
pytest tests/ -v
```

Tests are pure unit tests — no database or network connection required.

## Deployment on Railway

### Environment Variables

Set these in your Railway service:

| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram bot token from BotFather |
| `DATABASE_URL` | Auto-injected by Railway PostgreSQL plugin |
| `WEBHOOK_URL` | Your Railway app URL (e.g. `https://your-app.up.railway.app`) |
| `PORT` | Auto-injected by Railway (default: 8443) |
| `ADMIN_TELEGRAM_ID` | Your Telegram numeric user ID for /admin |
| `LOG_LEVEL` | `INFO` or `DEBUG` (default: `INFO`) |

### Deploy

1. Push to GitHub and connect your repo to Railway
2. Railway detects `railway.toml` and builds with Nixpacks
3. The bot automatically runs Alembic migrations on startup
4. Set `WEBHOOK_URL` to your Railway app URL
5. Bot starts in webhook mode automatically when `WEBHOOK_URL` is set

### Health Check

`GET /` returns `200 OK` with `"NaijaTax Bot is running"`.

## Database Schema

**`users`**
- `telegram_id` (BigInt, PK)
- `username` (String, nullable)
- `language_preference` (String, default `"en"`)
- `first_seen` (DateTime)
- `last_active` (DateTime)
- `total_calculations` (Integer)

**`calculation_logs`**
- `id` (Integer, PK, autoincrement)
- `telegram_id` (BigInt, FK → users)
- `calculation_type` (`salaried` | `selfemployed` | `checker`)
- `gross_annual` (Float)
- `chargeable_income` (Float)
- `annual_tax` (Float)
- `effective_rate` (Float)
- `created_at` (DateTime)

## Contact / Tax Authority

Tax is administered by the **Nigeria Revenue Service (NRS)** — formerly FIRS, renamed under NTA 2025.

Website: [www.nrs.gov.ng](https://www.nrs.gov.ng)
