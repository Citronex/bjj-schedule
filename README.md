# BJJ Schedule

A single-file, static schedule app for Evolution Grappling Academy (Beacon and Fishkill) and Snake Hill MMA (Marlboro).

## Contents
- `index.html` — complete GitHub Pages-ready app; logos are embedded, so there are no external assets or build dependencies.
- `monitor/` — monthly schedule-image baselines, sources, and review instructions.

## Current features
- Day and Week views with previous/next navigation and a Today button.
- Mobile defaults to Day view with large touch targets and safe-area spacing for iOS Safari.
- Switching views preserves the selected date and filters.
- Filters for academy location and Gi / No-Gi classes.
- Correct alternating Beacon fundamentals rotation, anchored to the Saturday, September 12, 2026 Gi class, using calendar dates to remain stable across daylight-saving changes.
- Academy logos on class cards and beside the page title.

The schedule currently lists adult classes and open mats. Kids classes are excluded.

## Schedule monitoring

The **Check schedule images** GitHub Action runs monthly and can also be run manually. Changed images or fetch errors open a review issue with comparison evidence. Calendar changes require review; only class information is in scope. See [monitor instructions](monitor/README.md) for details, URL replacement limitations, and accepting a new baseline.
