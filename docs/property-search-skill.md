# `$ property-search-skill` details

Longer reference moved out of the main README.

## `[ repository structure ]`

```
skills/
├── Property Search Skill/
│   ├── SKILL.md                   # Usage and API documentation
│   └── scripts/
│       └── client_manager.py      # CLI for managing clients and running searches
├── scrapling/
│   ├── SKILL.md
│   ├── examples/                  # Fetch and spider examples
│   └── references/                # Detailed usage guides
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


## `[ property search skill — quick reference ]`

This skill connects to the Property Search Flask app at `http://localhost:5050`.

### create a client

```bash
$ python3 skills/Property\ Search\ Skill/scripts/client_manager.py create \
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

### run a search

```bash
# Search for a specific client
$ python3 skills/Property\ Search\ Skill/scripts/client_manager.py search --client-id <CLIENT_ID>

# Quick one-off search without saving a client
$ python3 skills/Property\ Search\ Skill/scripts/client_manager.py quick-search \
  --location "78660" \
  --distance 5 \
  --min-price 250000 \
  --max-price 500000 \
  --min-beds 3
```

### email a client their listings

```bash
$ python3 skills/Property\ Search\ Skill/scripts/client_manager.py email --client-id <CLIENT_ID>
```

### email frequency options

| Option | Behavior |
|--------|----------|
| `every_new_listing` | Email immediately when a new match is found |
| `once_daily` | Send a digest at most once per 24 hours |
| `once_weekly` | Send a digest at most once per 7 days |
| `never` | No automatic emails |
