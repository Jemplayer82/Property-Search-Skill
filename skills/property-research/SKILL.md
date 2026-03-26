# Property Research Skill

Generate professional property research reports for any US address using BatchData API, Google Maps, and Google Drive.

## Features

- **BatchData Integration** - Property data, tax info, ownership, comparables
- **Google Maps** - Location mapping and street view imagery  
- **Google Drive** - Automatic cloud storage of reports
- **Professional PDF** - Clean, formatted 2-page reports
- **Batch Processing** - Generate reports for multiple properties

## Requirements

- Python 3.7+
- BatchData API key
- Google Maps API key
- Google Drive OAuth credentials

## Setup (one-time)

```bash
cd ~/.openclaw/workspace/skills/property-research
python3 setup.py
# Edit .env with your API keys
```

## Usage

### Single property:
```bash
cd ~/.openclaw/workspace/skills/property-research
source venv/bin/activate
python -m src.main "123 Main St, New York, NY" --upload
```

### Batch processing:
```bash
python -m src.main --batch addresses.txt --upload
```

## Output

Generates 2-page PDF reports:
- **Page 1:** Header with property address
- **Page 2:** Map buttons, map image, street view, comparable properties section, footer

Reports saved to `output/` folder and optionally uploaded to Google Drive.

## API Keys

Edit `.env` file:
```env
BATCHDATA_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here
GOOGLE_DRIVE_CLIENT_ID=your_client_id
GOOGLE_DRIVE_CLIENT_SECRET=your_secret
```

## Dependencies

- `requests`
- `google-api-python-client`
- `reportlab`
- `python-dotenv`
- `pyenchant` (optional, for spell checking)
- `pandas`

## License

MIT License - see LICENSE file
