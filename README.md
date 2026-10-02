<p align="center"><img src="assets/fathom-header-banner.svg" alt="Fathom Works — property-search-skill" width="100%"></p>

# `$ property-search-skill`

**A set of add-on abilities that let an AI assistant search for homes, scrape web pages, and handle small daily chores.** Each ability is called a skill: a folder of instructions the assistant reads and follows.

**In plain terms:** if you use the [OpenClaw](https://github.com/openclaw/openclaw) AI agent (an open-source program that runs an AI assistant on your own computer), these skills teach it new jobs. The main one finds home listings that match a client's wishes and emails them the results.

*A [Fathom Works](https://github.com/Jemplayer82) project.*

## `[ quick start ]`

Tell OpenClaw to install the skill you want. Replace `SKILL-NAME` with a folder name from `skills/`.

```
/openclaw skills install https://github.com/jemplayer82/Property-Search-Skill/tree/main/skills/SKILL-NAME
```

## `[ skills included ]`

| Skill | What it does |
|---|---|
| Property Search Skill | Searches home listings (Redfin, Zillow, Realtor.com) using HomeHarvest, a free listing-search library. Saves each client's wishes and emails new matches. Works with the [Property Search](https://github.com/jemplayer82/Property-Search) app. |
| Property Research | Looks up one property in depth: owner and tax records, deeds, and a PDF report saved to Google Drive. |
| Scrapling | Reads web pages, even ones that try to block automated visitors, using the [Scrapling](https://github.com/D4Vinci/Scrapling) library. |
| Screen Monitor | Shares your screen through a web page so the assistant can look at it. |
| School Lunch Menu | Fetches the daily cafeteria menu for Pflugerville ISD schools at 5am and sends it by WhatsApp or email. |
| Git Essentials | Common git (version tracking) steps and shortcuts. |
| Online Shopping | Helps browse online stores using your saved preferences and site lists. |

## `[ usage ]`

The property skill talks to the Property Search app at `http://localhost:5050`. Start that app first. Then run the helper script. This example saves a new client:

```bash
$ python3 skills/Property\ Search\ Skill/scripts/client_manager.py create --first-name "Jane" --last-name "Smith" --email "jane@example.com" --location "Austin, TX"
```

Other commands are `search`, `quick-search` (a one-off search without saving a client) and `email`. Every option and example is in [docs/property-search-skill.md](docs/property-search-skill.md).

Email frequency for each client:

| Option | What happens |
|--------|----------|
| `every_new_listing` | Email right away when a new match appears |
| `once_daily` | One summary at most every 24 hours |
| `once_weekly` | One summary at most every 7 days |
| `never` | No automatic emails |

## `[ requirements ]`

- [OpenClaw](https://github.com/openclaw/openclaw) installed and set up.
- Property Search Skill: the [Property Search](https://github.com/jemplayer82/Property-Search) app running at `localhost:5050`.
- School Lunch Menu: SMTP (email sending) or WhatsApp login details set up in OpenClaw.

## `[ docs ]`

- [Property Search Skill reference](docs/property-search-skill.md): folder layout, all commands, full examples.
- Each skill has its own `SKILL.md` inside `skills/`.

## `[ license ]`

AGPL-3.0. See [LICENSE](LICENSE).

<img src="assets/fathom-footer-banner.svg" alt="Fathom Works — sound the depths before you set a course" width="100%">
