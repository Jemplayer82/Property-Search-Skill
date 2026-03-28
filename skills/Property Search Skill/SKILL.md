---
name: Property Search Skill
description: Integration with the Property Search Flask app for MLS listings via HomeHarvest. Create client cards with filters, run searches, and get notified of new listings. Supports location-based filtering with distance radius, price ranges, beds/baths, property types, and age filters.
---

# Property Search Skill

Integrates with the Property Search Flask app running at `localhost:5050` to search MLS listings via HomeHarvest (Redfin/Zillow/Realtor.com data).

## Features

- **Client Management**: Create, edit, delete client cards with custom filters
- **Automated Searches**: Run searches for clients with their saved filters
- **Email Notifications**: Send listing results to clients
- **Distance Filtering**: Filter listings by radius from a center point
- **Property Filters**: Price, beds, baths, sqft, property type, age, status

## API Endpoints

The Flask app exposes these endpoints:
- `GET /clients` - List all clients
- `POST /clients/new` - Create new client
- `POST /clients/<id>/search` - Run search for client
- `POST /clients/<id>/email` - Email listings to client
- `GET /api/listings` - Get all listings (JSON)

## Usage

### Create a New Client

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

### Run Search for a Client

```bash
python3 scripts/client_manager.py search --client-id <CLIENT_ID>
```

### Email Client Their Listings

```bash
python3 scripts/client_manager.py email --client-id <CLIENT_ID>
```

### Search Without Creating Client

```bash
python3 scripts/client_manager.py quick-search \
  --location "78660" \
  --distance 5 \
  --min-price 250000 \
  --max-price 500000 \
  --min-beds 3
```

## Client Filter Options

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
| `email_frequency` | string | every_new_listing, once_daily, once_weekly, never |

## Email Frequency Options

- `every_new_listing` - Email immediately when new listings match (default)
- `once_daily` - Send daily digest (max once per 24 hours)
- `once_weekly` - Send weekly digest (max once per 7 days)
- `never` - Don't send emails

## Example Client Card

```json
{
  "id": "8c5c0b89-6cd5-433b-a1fc-a740248568fb",
  "first_name": "Landon",
  "last_name": "Ferguson",
  "email": "landon@txferguson.net",
  "email_frequency": "once_weekly",
  "filters": {
    "location": "3524 winding shore ln",
    "distance": 0,
    "min_price": 250000,
    "max_price": 500000,
    "min_beds": 0,
    "min_baths": 0,
    "property_types": ["house"],
    "status": "for sale",
    "min_sqft": 3000,
    "max_age": 10
  }
}
```

## Scheduled Searches

The Flask app runs hourly scheduled searches automatically. Clients with:
- `every_new_listing`: Searched every hour, emailed if new listings found
- `once_daily`: Searched only if 24+ hours since last email
- `once_weekly`: Searched only if 7+ days since last email
- `never`: Never auto-searched

## Output Format

Listings are returned as:
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

## Web Interface

The app also has a web UI available at `http://localhost:5050`:
- `/clients` - Manage client cards
- `/search-page` - Run one-off searches
- `/map` - View listings on a map
- `/settings` - Configure email notifications

## Dependencies

- Flask app running at `localhost:5050`
- HomeHarvest for MLS data scraping
- APScheduler for background searches
- SMTP config for email notifications (configured via web UI)
