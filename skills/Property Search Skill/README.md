# 🏠 Property Search Skill

> MLS property search automation for real estate professionals

A powerful OpenClaw skill that integrates with the Property Search Flask app to fetch MLS listings via HomeHarvest (Redfin/Zillow/Realtor.com data). Create client cards with custom filters, run automated searches, and get notified when new properties match.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Client Management** | Create personalized client cards with saved search filters |
| 🔍 **Automated Searches** | Run scheduled searches for multiple clients automatically |
| 📧 **Email Notifications** | Notify clients instantly when new listings match their criteria |
| 📍 **Location-Based Filtering** | Filter by radius from any address, city, or ZIP code |
| 🏡 **Property Types** | Search houses, condos, townhouses, multi-family, land, mobile homes |
| 💰 **Price & Size Ranges** | Set min/max price, beds, baths, square footage |
| 🕒 **Flexible Scheduling** | Choose: immediate, daily, weekly, or never |

---

## 🚀 Quick Start

### Prerequisites

- Property Search Flask app running at `localhost:5050`
- HomeHarvest for MLS data scraping
- APScheduler for background tasks

### Installation

```bash
# Clone or navigate to the skill directory
cd ~/.openclaw/workspace/skills/Property Search Skill

# Ensure the Flask app is running
curl http://localhost:5050/health || echo "Start the app: ~/property-search/restart.sh"
```

---

## 📋 Usage

### Create a Client Card

```bash
python3 scripts/client_manager.py create \
  --first-name "John" \
  --last-name "Doe" \
  --email "john@example.com" \
  --location "Austin, TX" \
  --distance 10 \
  --min-price 300000 \
  --max-price 600000 \
  --min-beds 3 \
  --min-baths 2 \
  --property-types house condo \
  --status "for sale" \
  --email-frequency "once_daily"
```

### List All Clients

```bash
python3 scripts/client_manager.py list
```

**Output:**
```
ID                                   Name                      Email                          Location                  Frequency
============================================================================================================
8c5c0b89-6cd5-433b-a1fc-a740248568fb John Doe                  john@example.com               Austin, TX                once_daily
```

### Run Search for a Client

```bash
python3 scripts/client_manager.py search --client-id 8c5c0b89-6cd5-433b-a1fc-a740248568fb
```

### Email Client Their Listings

```bash
python3 scripts/client_manager.py email --client-id 8c5c0b89-6cd5-433b-a1fc-a740248568fb
```

### Quick Search (No Client Required)

```bash
python3 scripts/client_manager.py quick-search \
  --location "78660" \
  --distance 5 \
  --min-price 250000 \
  --max-price 500000 \
  --min-beds 3
```

---

## ⚙️ Filter Options

| Filter | Type | Description |
|--------|------|-------------|
| `location` | string | Address, city, ZIP, or neighborhood |
| `distance` | float | Radius in miles from location (0 = no limit) |
| `min_price` | int | Minimum listing price |
| `max_price` | int | Maximum listing price |
| `min_beds` | int | Minimum bedrooms |
| `min_baths` | int | Minimum bathrooms |
| `min_sqft` | int | Minimum square footage |
| `max_sqft` | int | Maximum square footage |
| `max_age` | int | Maximum home age in years |
| `min_age` | int | Minimum home age in years |
| `property_types` | list | house, condo, townhouse, multi-family, land, mobile |
| `status` | string | for sale, pending, sold |

---

## 📧 Email Frequency Options

| Frequency | Description |
|-----------|-------------|
| `every_new_listing` | Email immediately when new listings match (default) |
| `once_daily` | Send daily digest (max once per 24 hours) |
| `once_weekly` | Send weekly digest (max once per 7 days) |
| `never` | Don't send emails |

---

## 🔄 Scheduled Searches

The Flask app automatically runs hourly scheduled searches:

- **Every new listing** → Searched every hour, emailed if new listings found
- **Once daily** → Searched only if 24+ hours since last email
- **Once weekly** → Searched only if 7+ days since last email
- **Never** → Never auto-searched

---

## 📊 Output Format

Listings are returned as JSON:

```json
{
  "total": 15,
  "new": 3,
  "listings": [
    {
      "id": "mls_12345",
      "address": "123 Main St",
      "city": "Austin",
      "state": "TX",
      "zip": "78701",
      "price": 450000,
      "beds": 3,
      "baths": 2,
      "sqft": 2100,
      "property_type": "house",
      "year_built": 2015,
      "days_on_market": 5,
      "url": "https://...",
      "photo": "https://...",
      "latitude": 30.2672,
      "longitude": -97.7431,
      "is_new": true
    }
  ]
}
```

---

## 🌐 Web Interface

The Flask app includes a web UI at `http://localhost:5050`:

| Endpoint | Description |
|------------|-------------|
| `/clients` | Manage client cards |
| `/search-page` | Run one-off searches |
| `/map` | View listings on interactive map |
| `/settings` | Configure email notifications |

---

## 🏗️ API Endpoints

The Flask app exposes these REST endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/clients` | List all clients |
| POST | `/clients/new` | Create new client |
| POST | `/clients/{id}/search` | Run search for client |
| POST | `/clients/{id}/email` | Email listings to client |
| GET | `/api/listings` | Get all listings (JSON) |
| POST | `/search` | Run quick search |

---

## 📁 Project Structure

```
Property Search Skill/
├── scripts/
│   └── client_manager.py    # CLI client management tool
├── SKILL.md                 # Detailed skill documentation
├── README.md               # This file
└── requirements.txt        # Python dependencies
```

---

## 🛠️ Dependencies

- [HomeHarvest](https://github.com/) - MLS data scraping from Redfin/Zillow/Realtor.com
- [APScheduler](https://apscheduler.readthedocs.io/) - Background job scheduling
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [requests](https://requests.readthedocs.io/) - HTTP library

---

## 🐛 Troubleshooting

### "Could not connect to localhost:5050"

The Flask app isn't running. Start it with:
```bash
~/property-search/restart.sh
```

### "No clients found"

Create a client first:
```bash
python3 scripts/client_manager.py create --first-name "Test" --last-name "User" --email "test@test.com" --location "Austin, TX"
```

---

## 📝 License

MIT - Feel free to use and modify for your real estate needs.

---

## 🙏 Credits

Built with ❤️ for OpenClaw by real estate professionals, for real estate professionals.

---

<p align="center">
  <em>Happy house hunting! 🏡</em>
</p>
