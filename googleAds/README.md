# Fowler Homes Google Ads Editor

A web-based editor for managing Fowler Homes' Google Ads campaigns. Provides real-time SERP previews, character count validation, and one-click export to JSON or CSV.

## What It Does

This is a single-page application backed by a Python server that lets you view, edit, and export Google Ads campaigns (specifically Responsive Search Ads) without logging into Google Ads Editor.

### Campaign Management

- **25 campaigns** organised by region (Auckland, Christchurch, Hamilton, Tauranga, etc.) and type (Brand vs Services)
- Sidebar lists all campaigns with budget, ad count, and location at a glance
- Filter campaigns by **All**, **Brand**, or **Services**
- Each campaign shows budget, status, locations, comments, and region-specific USPs (Unique Selling Points)

### Ad Editing

- Edit **headlines** (up to 10 per RSA, 30 char limit) and **descriptions** (up to 4 per RSA, 90 char limit) inline
- Edit final URLs per ad
- Collapsible ad cards with expand/collapse all

### SERP Preview

- Live Google Search result preview updates as you type
- Shows domain, headlines joined with separators, and combined descriptions exactly as they'd appear in search results
- Character count pills below each preview: grey (under limit), green (approaching limit), red (over limit)
- Red border and warning banner when any field exceeds Google Ads limits

### Export

- **Export JSON** — downloads the full data structure as `ads_data.json`
- **Export CSV** — downloads a tab-separated `ads_review.csv` with columns for Campaign, Ad Group, RSA #, Headlines 1-10, Descriptions 1-4, and Final URL

### Save & Backup

- **Save** button writes changes to the server
- Server creates a timestamped backup on every save and retains the last 10
- Unsaved changes warning on page close

## Architecture

```
ads_editor.html   — Single-file frontend (HTML, CSS, JS, no build step)
ads_data.json     — Campaign data (read on load, written on save)
server.py         — Python HTTP server (stdlib only, no dependencies)
Procfile          — Railway/Render/Fly.io deployment config
```

### Server Endpoints

| Method | Path             | Auth | Description                          |
|--------|------------------|------|--------------------------------------|
| GET    | `/`              | Yes  | Redirects to `/ads_editor.html`      |
| GET    | `/ads_editor.html` | Yes | Serves the editor                    |
| GET    | `/ads_data.json` | Yes  | Returns current campaign data        |
| GET    | `/login`         | No   | Login page                           |
| POST   | `/login`         | No   | Authenticate with password           |
| POST   | `/logout`        | No   | Clear session and redirect to login  |
| POST   | `/save`          | Yes  | Save campaign data (with backup)     |

### Authentication

- Enabled by setting the `APP_PASSWORD` environment variable
- HMAC-SHA256 signed session cookies (24-hour expiry)
- `HttpOnly` and `SameSite=Lax` cookie flags
- `Secure` flag added automatically on non-localhost hosts

## Running Locally

```bash
python3 server.py
```

Open http://localhost:8080. No dependencies beyond Python 3 stdlib.

To enable password protection locally:

```bash
APP_PASSWORD=yourpassword python3 server.py
```

## Environment Variables

| Variable       | Default          | Description                                      |
|----------------|------------------|--------------------------------------------------|
| `PORT`         | `8080`           | Server listening port                            |
| `APP_PASSWORD` | *(empty)*        | Set to enable login protection                   |
| `APP_SECRET`   | *(auto-generated)* | HMAC signing key for session tokens            |
| `DATA_DIR`     | *(script dir)*   | Persistent storage path (for cloud volumes)      |

## Deployment

Deployed on Railway. The `Procfile` runs `python server.py`. Set `APP_PASSWORD` and optionally `DATA_DIR` (for a persistent volume) in Railway's environment variables.

On first deploy, the server copies `ads_data.json` to `DATA_DIR` if the file doesn't already exist there.
