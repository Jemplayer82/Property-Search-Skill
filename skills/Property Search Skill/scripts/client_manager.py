#!/usr/bin/env python3
"""
Client Manager for Property Search Flask App

Manages client cards and runs searches via the Flask API.
"""

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

import requests

BASE_URL = "http://localhost:5050"
CLIENTS_FILE = Path.home() / "property-search" / "clients.json"


def load_clients():
    """Load clients directly from the JSON file."""
    if CLIENTS_FILE.exists():
        with open(CLIENTS_FILE) as f:
            return json.load(f)
    return []


def save_clients(clients):
    """Save clients directly to the JSON file."""
    with open(CLIENTS_FILE, "w") as f:
        json.dump(clients, f, indent=2)


def list_clients():
    """List all clients."""
    clients = load_clients()
    if not clients:
        print("No clients found.")
        return

    print(f"\n{'ID':<36} {'Name':<25} {'Email':<30} {'Location':<25} {'Frequency':<15}")
    print("=" * 140)
    for c in clients:
        name = f"{c['first_name']} {c['last_name']}"
        loc = c['filters'].get('location', '')[:24]
        freq = c.get('email_frequency', 'every_new_listing')
        print(f"{c['id']:<36} {name:<25} {c['email']:<30} {loc:<25} {freq:<15}")
    print(f"\nTotal: {len(clients)} client(s)")


def create_client(args):
    """Create a new client card."""
    client = {
        "id": str(uuid.uuid4()),
        "first_name": args.first_name,
        "last_name": args.last_name,
        "email": args.email,
        "email_frequency": args.email_frequency,
        "last_emailed": None,
        "filters": {
            "location": args.location,
            "distance": args.distance,
            "min_price": args.min_price or 0,
            "max_price": args.max_price or 0,
            "min_beds": args.min_beds or 0,
            "min_baths": args.min_baths or 0,
            "property_types": args.property_types or [],
            "status": args.status,
            "min_sqft": args.min_sqft,
            "max_sqft": args.max_sqft,
            "max_age": args.max_age,
            "min_age": args.min_age,
        },
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    clients = load_clients()
    clients.append(client)
    save_clients(clients)

    print(f"✅ Created client: {client['first_name']} {client['last_name']}")
    print(f"   ID: {client['id']}")
    print(f"   Email: {client['email']}")
    print(f"   Location: {client['filters']['location']}")
    print(f"   Email frequency: {client['email_frequency']}")
    return client


def search_client(args):
    """Run a search for a specific client."""
    try:
        resp = requests.post(f"{BASE_URL}/clients/{args.client_id}/search", timeout=120)
        resp.raise_for_status()
        data = resp.json()

        print(f"\n🔍 Search Results for {data.get('client', {}).get('first_name', 'Client')}:")
        print(f"   Total listings: {data['total']}")
        print(f"   New listings: {data['new']}")

        if data['listings']:
            print(f"\n{'Address':<40} {'Price':<12} {'Beds':<5} {'Baths':<5} {'SqFt':<8} {'Status':<8}")
            print("=" * 90)
            for l in data['listings']:
                status = "NEW" if l.get('is_new') else "seen"
                price = f"${l.get('price', 0):,}" if l.get('price') else "N/A"
                addr = f"{l.get('address', '')}, {l.get('city', '')}"[:38]
                print(f"{addr:<40} {price:<12} {str(l.get('beds', '-')):<5} {str(l.get('baths', '-')):<5} {str(l.get('sqft', '-')):<8} {status:<8}")

        return data
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {BASE_URL}")
        print("   Make sure the Flask app is running: ~/property-search/restart.sh")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def email_client(args):
    """Email listings to a client."""
    try:
        resp = requests.post(f"{BASE_URL}/clients/{args.client_id}/email", timeout=30)
        resp.raise_for_status()
        print(f"✅ Email sent to client!")
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {BASE_URL}")
        print("   Make sure the Flask app is running: ~/property-search/restart.sh")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def quick_search(args):
    """Run a quick search without creating a client."""
    config = {
        "location": args.location,
        "filters": {
            "min_price": args.min_price or 0,
            "max_price": args.max_price or 0,
            "min_beds": args.min_beds or 0,
            "min_baths": args.min_baths or 0,
            "property_types": args.property_types or [],
            "status": [args.status],
            "min_sqft": args.min_sqft,
            "max_sqft": args.max_sqft,
            "max_age": args.max_age,
            "min_age": args.min_age,
            "distance": args.distance or 0,
        }
    }

    try:
        print(f"🔍 Searching: {args.location}...")
        resp = requests.post(f"{BASE_URL}/search", json=config, timeout=120)
        resp.raise_for_status()
        data = resp.json()

        print(f"\n✅ Found {data['total']} listings ({data['new']} new)")

        if data['listings']:
            print(f"\n{'Address':<40} {'Price':<12} {'Beds':<5} {'Baths':<5} {'SqFt':<8} {'Status':<8}")
            print("=" * 90)
            for l in data['listings'][:20]:  # Show first 20
                status = "NEW" if l.get('is_new') else "seen"
                price = f"${l.get('price', 0):,}" if l.get('price') else "N/A"
                addr = f"{l.get('address', '')}, {l.get('city', '')}"[:38]
                print(f"{addr:<40} {price:<12} {str(l.get('beds', '-')):<5} {str(l.get('baths', '-')):<5} {str(l.get('sqft', '-')):<8} {status:<8}")

            if len(data['listings']) > 20:
                print(f"\n... and {len(data['listings']) - 20} more listings")

        return data
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to {BASE_URL}")
        print("   Make sure the Flask app is running: ~/property-search/restart.sh")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def delete_client(args):
    """Delete a client by ID."""
    clients = load_clients()
    original_count = len(clients)
    clients = [c for c in clients if c['id'] != args.client_id]

    if len(clients) == original_count:
        print(f"❌ Client {args.client_id} not found.")
        sys.exit(1)

    save_clients(clients)
    print(f"✅ Client {args.client_id} deleted.")


def main():
    parser = argparse.ArgumentParser(
        description="Property Search Client Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all clients
  %(prog)s list

  # Create a new client
  %(prog)s create --first-name "John" --last-name "Doe" --email "john@example.com" \\
      --location "Austin, TX" --distance 10 --min-price 300000 --max-price 600000

  # Search for a client
  %(prog)s search --client-id <UUID>

  # Email client their listings
  %(prog)s email --client-id <UUID>

  # Quick search without creating client
  %(prog)s quick-search --location "78660" --distance 5 --min-price 250000

  # Delete a client
  %(prog)s delete --client-id <UUID>
        """
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # List command
    subparsers.add_parser("list", help="List all clients")

    # Create command
    create_parser = subparsers.add_parser("create", help="Create a new client")
    create_parser.add_argument("--first-name", required=True, help="Client first name")
    create_parser.add_argument("--last-name", required=True, help="Client last name")
    create_parser.add_argument("--email", required=True, help="Client email")
    create_parser.add_argument("--location", required=True, help="Search location (address, city, ZIP)")
    create_parser.add_argument("--distance", type=float, default=0, help="Radius in miles (0 = no limit)")
    create_parser.add_argument("--min-price", type=int, help="Minimum price")
    create_parser.add_argument("--max-price", type=int, help="Maximum price")
    create_parser.add_argument("--min-beds", type=int, help="Minimum bedrooms")
    create_parser.add_argument("--min-baths", type=int, help="Minimum bathrooms")
    create_parser.add_argument("--min-sqft", type=int, help="Minimum square footage")
    create_parser.add_argument("--max-sqft", type=int, help="Maximum square footage")
    create_parser.add_argument("--max-age", type=int, help="Maximum home age (years)")
    create_parser.add_argument("--min-age", type=int, help="Minimum home age (years)")
    create_parser.add_argument("--property-types", nargs="+", choices=["house", "condo", "townhouse", "multi-family", "land", "mobile"],
                               help="Property types to include")
    create_parser.add_argument("--status", default="for sale", choices=["for sale", "pending", "sold"],
                               help="Listing status")
    create_parser.add_argument("--email-frequency", default="every_new_listing",
                               choices=["every_new_listing", "once_daily", "once_weekly", "never"],
                               help="How often to email client")

    # Search command
    search_parser = subparsers.add_parser("search", help="Run search for a client")
    search_parser.add_argument("--client-id", required=True, help="Client UUID")

    # Email command
    email_parser = subparsers.add_parser("email", help="Email listings to client")
    email_parser.add_argument("--client-id", required=True, help="Client UUID")

    # Quick search command
    quick_parser = subparsers.add_parser("quick-search", help="Quick search without creating client")
    quick_parser.add_argument("--location", required=True, help="Search location")
    quick_parser.add_argument("--distance", type=float, default=0, help="Radius in miles")
    quick_parser.add_argument("--min-price", type=int, help="Minimum price")
    quick_parser.add_argument("--max-price", type=int, help="Maximum price")
    quick_parser.add_argument("--min-beds", type=int, help="Minimum bedrooms")
    quick_parser.add_argument("--min-baths", type=int, help="Minimum bathrooms")
    quick_parser.add_argument("--min-sqft", type=int, help="Minimum square footage")
    quick_parser.add_argument("--max-sqft", type=int, help="Maximum square footage")
    quick_parser.add_argument("--max-age", type=int, help="Maximum home age")
    quick_parser.add_argument("--min-age", type=int, help="Minimum home age")
    quick_parser.add_argument("--property-types", nargs="+", choices=["house", "condo", "townhouse", "multi-family", "land", "mobile"])
    quick_parser.add_argument("--status", default="for sale", choices=["for sale", "pending", "sold"])

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a client")
    delete_parser.add_argument("--client-id", required=True, help="Client UUID")

    args = parser.parse_args()

    if args.command == "list":
        list_clients()
    elif args.command == "create":
        create_client(args)
    elif args.command == "search":
        search_client(args)
    elif args.command == "email":
        email_client(args)
    elif args.command == "quick-search":
        quick_search(args)
    elif args.command == "delete":
        delete_client(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
