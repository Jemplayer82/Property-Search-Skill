# MEMORY.md

This file records long-term insights and decisions. Update as you go.

## Preferences
- **Web scraping:** Always use scrapling with `stealthy-fetch` (stealth mode) instead of the regular browser for any web scraping tasks. Cap'n prefers this approach.
- **Debug mode:** When debugging or learning, slow down and work through issues step by step rather than rushing ahead.
- **Config changes:** Always show proposed changes and wait for explicit OK before applying. No exceptions.
- **Models:** Use `ollama/qwen3-coder-next:cloud` as an available model option when requested.
- **Model configuration:** Kimi-k2.5:cloud is default; qwen3-coder-next:cloud is available for switching. OpenRouter has been removed from model catalog.

## Property Research Workflow
- **When asked about a property:** First search Google Drive for an existing folder with that address
- If folder exists: read all files (PDFs, MD files, etc.) to gather existing data before doing any web searches
- Pull property data from Travis CAD (travis.prodigycad.com) using browser automation
- Create a Google Drive folder named after the address (if it doesn't exist)
- Upload a PDF of the TCAD page to the folder
- Pull comps from surrounding area (Park at Blackhawk / Blackhawk neighborhood)
- Upload comps analysis MD file to the folder
- Deed search via tccsearch.org (Travis County Clerk)

## Projects
- Working on property research for Pflugerville TX properties (Park at Blackhawk area)
- First property researched: 3520 Winding Shore Lane, Pflugerville TX 78660
  - Owner: Ferguson Landon & Jennifer
  - TCAD PropID: 550733
  - 2025 Appraisal: $461,373
  - Deed instrument: 2012132194TR (Warranty Deed, 8/2/2012)
  - Drive folder: https://drive.google.com/drive/folders/1dNUxzdiEWEZuU5x1N88FnrLMmj7tkb62
- Attempted research on 3520 Winding Shore Lane, Pflugerville TX 78660 (2026-03-21)
  - Confirmed exists on Google Maps
  - TCAD search failed - JavaScript-heavy site not rendering with automation tools
  - Created Drive folder but awaiting actual property data: https://drive.google.com/drive/folders/1of3ie2BQNU-xi4Jjo0R41d_sasvX-hfW

## Session Startup (2026-03-21)
- Setup completed: qwen3-coder-next:cloud model added to ollama provider
- OpenRouter provider removed from model catalog to clean up dropdown
- Memory flush enabled before compaction for long sessions
