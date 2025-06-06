# zoom-viewer
Zoom viewer project featuring custom OpenSeaDragon configuration

## Installation

1. Clone this repository.
2. Serve the directory with a simple HTTP server so the HTML files can load tiles from a remote host:
   ```bash
   python -m http.server
   ```
   Then open `http://localhost:8000/index.html` or `http://localhost:8000/default_tile.html` in a browser.
   Alternatively you can open the HTML files directly from disk if your browser allows local file access.

## Usage

1. Edit the `TILE_PREFIX` constant inside `index.html` (and `default_tile.html` if used) to point to the base URL where your tiles are hosted.
2. Open the desired HTML file in your browser. Use the on-screen buttons or scroll wheel to zoom between layers.

### Tile Hosting Requirements

Tiles must be publicly accessible at URLs following the pattern:
`<TILE_PREFIX>/layer_<layer>/<y>_<x>.(png|webp)`.
The viewer requires CORS to be enabled if served from a different domain.

`default_tile.html` also defines `fallbackTile` which is displayed whenever a tile is missing, avoiding console errors.

### Uploading Tiles

The `upload_tiles.py` script uploads tiles to a Cloudflare R2 bucket. Configure your bucket information in `wrangler.toml` and ensure the `wrangler` CLI is installed. The script expects Cloudflare authentication via the `CLOUDFLARE_API_TOKEN` environment variable.

