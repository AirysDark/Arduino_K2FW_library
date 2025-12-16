# Sonic-Stream – Moonraker UI (Static)

This is a **static UI** that connects to **Moonraker** and uses it to control your printer.

## Best way to run (avoids CORS issues)
Host this UI inside Moonraker's web root:

1) Copy folder to:
   `~/printer_data/www/sonic-stream/`

2) Open in browser:
   `http://<printer-ip>/sonic-stream/`

When hosted this way, you can leave **API Base URL empty** (same host).

## If you run it from another PC/host
Set **API Base URL** in Settings, e.g.
- `http://<printer-ip>`
- `http://<printer-ip>:7125`

Note: your browser may block requests if Moonraker isn't configured for CORS. Hosting inside `printer_data/www/` is recommended.

## Endpoints used
- GET  `/server/info`
- POST `/printer/objects/query`
- POST `/printer/gcode/script`
- POST `/printer/print/pause`
- POST `/printer/print/cancel`
- GET  `/server/files/list?root=gcodes`
- POST `/printer/print/start`

