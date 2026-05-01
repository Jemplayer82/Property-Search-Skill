# OpenClaw Skills

A collection of custom agent skills for [OpenClaw](https://github.com/openclaw/openclaw) — an open-source AI agent runtime. These skills extend Claude with real-world integrations for property research, web scraping, daily utilities, and more.

## Skills Included

### Property Research

**Property Search Skill** — MLS listing search powered by HomeHarvest (Redfin / Zillow / Realtor.com). Create client cards with saved filters, run automated searches, and send email notifications for new listings. Integrates with the [Property Search](https://github.com/jemplayer82/Property-Search) Flask app running locally.

**Property Research** — Full property research workflow using BatchData API, TCAD scraping, deed lookups, and PDF report generation via Google Drive.

### Web & Screen

**Scrapling** — Web scraping with anti-bot bypass using the [Scrapling](https://github.com/D4Vinci/Scrapling) library. Includes static, dynamic, and stealthy fetch modes with spider support.

**Screen Monitor** — Screen capture and analysis tool. Shares and analyzes your screen through a web endpoint.

### Daily Utilities

**School Lunch Menu** — Fetches daily cafeteria menus from SchoolDish for Pflugerville ISD schools. Runs automatically at 5am with delivery via WhatsApp or email.

**Git Essentials** — Common git workflows and shortcuts.

**Online Shopping** — Browsing assistant for online stores with saved preferences and site lists.

## Repository Structure

```
skills/
├── Property Search Skill/
│   ├── SKILL.md          # Usage and API documentation
│   └── scripts/
│       └── client_manager.py   # CLI for managing clients and running searches
├── scrapling/
│   ├── SKILL.md
│   ├── examples/         # Fetch and spider examples
│   └── references/       # Detailed usage guides
├── screen-monitor/
│   ├── SKILL.md
│   └── web/
│       └── screen-share.html
├── school-lunch-menu/
│   ├── SKILL.md
│   └── scripts/
├── git-essentials/
│   └── SKILL.md
└── online-shopping/
    ├── SKILL.md
    └── scripts/
```

## Property Search Skill — Quick Reference

This skill connects to the Property Search Flask app at `http://localhost:5050`.

### Create a Client

```bash
python3 skills/Property\ Search\ Skill/scripts/client_manager.py create \
  --first-name "Jane" \
  --last-name "Smith" \
  --email "jane@example.com" \
  --location "Austin, TX" \
  --distance 10 \
  --min-price 300000 \
  --max-price 600000 \
  --min-beds 3 \
  --min-baths 2 \
  --property-types house \
  --status "for sale" \
  --email-frequency once_daily
```

### Run a Search

```bash
# Search for a specific client
python3 skills/Property\ Search\ Skill/scripts/client_manager.py search --client-id <CLIENT_ID>

# Quick one-off search without saving a client
python3 skills/Property\ Search\ Skill/scripts/client_manager.py quick-search \
  --location "78660" \
  --distance 5 \
  --min-price 250000 \
  --max-price 500000 \
  --min-beds 3
```

### Email a Client Their Listings

```bash
python3 skills/Property\ Search\ Skill/scripts/client_manager.py email --client-id <CLIENT_ID>
```

### Email Frequency Options

| Option | Behavior |
|--------|----------|
| `every_new_listing` | Email immediately when a new match is found |
| `once_daily` | Send a digest at most once per 24 hours |
| `once_weekly` | Send a digest at most once per 7 days |
| `never` | No automatic emails |

## Installing a Skill in OpenClaw

```
/openclaw skills install https://github.com/jemplayer82/Property-Search-Skill/tree/main/skills/SKILL-NAME
```

## Requirements

- [OpenClaw](https://github.com/openclaw/openclaw) installed and configured
- For Property Search Skill: the [Property Search](https://github.com/jemplayer82/Property-Search) app running at `localhost:5050`
- For School Lunch Menu: SMTP or WhatsApp credentials configured in OpenClaw
