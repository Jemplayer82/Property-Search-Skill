# OpenClaw Skills

Custom agent skills for [OpenClaw](https://openclaw.ai) - my personal AI assistant.

## What's OpenClaw?

[OpenClaw](https://github.com/openclaw/openclaw) is an open-source agent runtime that lets you run AI assistants with custom skills. This repo contains my private skill collection.

## Skills Included

### Property Research
- **Property Research Paid** - Full property research with BatchData API, TCAD scraping, deed lookups, and PDF reports via Google Drive
- **Property Research Free** - Demo version using free data sources
- **Property Search Skill** - MLS listing search via HomeHarvest (Redfin/Zillow/Realtor.com). Create client cards with filters, run automated searches, email notifications for new listings

### Daily Utilities
- **School Lunch Menu** - Fetches cafeteria menus from SchoolDish for PfISD schools. Automated daily at 5am with WhatsApp/email delivery

### Other
- **scrapling-official** - Web scraping with anti-bot bypass using Scrapling
- **screen-monitor** - Screen sharing and analysis

## Structure

```
skills/
├── SKILL-NAME/
│   ├── SKILL.md          # Documentation and usage
│   ├── scripts/          # Python/bash scripts
│   ├── references/       # Reference docs
│   └── ...
```

## Installing a Skill

In OpenClaw:
```
/openclaw skills install https://github.com/YOUR-USER/openclaw-skills/tree/main/skills/SKILL-NAME
```

## Creating New Skills

See the [AgentSkills spec](https://docs.openclaw.ai/skills/) or use the `skill-creator` skill:
```
/openclaw skills create my-new-skill
```

## License

Private - These are personal tools for my OpenClaw instance.
