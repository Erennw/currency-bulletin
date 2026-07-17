# Currency Bulletin 💱

A Python CLI tool that fetches daily USD/TRY and EUR/TRY exchange
rates from the [Frankfurter API](https://frankfurter.dev) and prints
a human-readable bulletin with day-over-day change indicators.

## Features
- Live exchange rates from the Frankfurter API (ECB data, no API key required)
- Day-over-day change tracking with ↑/↓ percentage indicators
- Persistent rate history stored in JSON
- Duplicate-entry protection (same-day runs are detected)
- Fault-tolerant networking: 3 retries with increasing backoff
- Configuration via `.env` with fail-fast validation

## Setup
1. Clone the repository
2. Create a virtual environment and install dependencies:
