# Schedule image monitor

Runs on the first of each month at 13:17 UTC (9:17 AM Eastern during daylight saving, 8:17 AM otherwise), or manually via **Actions → Check schedule images → Run workflow**. No external API key is required. The static app still has no runtime or build dependencies.

The initial baselines were captured September 26, 2026. They are reference images for future changes, not a new audit of the calendar's existing class data. Snake Hill uses the full-resolution version of the supplied thumbnail, verified on https://snakehillmma.com/schedule/.

Sources are configured in `sources.json`. Snake Hill discovers its schedule image from its page each run. Evolution uses fixed image URLs: replacement images at new URLs require updating those sources. The Evolution website blocked automated page access during setup; its supplied CDN images were accessible.

Direct image comparison avoids browser layout/font differences and needs no Playwright/browser install. Images are decoded to RGB; metadata changes do not count. Resized images are aligned to the baseline. Any pixel with a channel difference over 12 triggers review, deliberately favoring sensitivity to tiny time/day edits. Compression, redesigns, logos, or kids schedule edits can still trigger an alert. Only human review determines whether adult classes changed. Locations are fixed, not extracted or compared.

Every run saves a JSON report and before/after images. Changed images also include a difference image. Artifacts are retained for 90 days. Image changes and download/decoding failures create or update one open GitHub issue, link the evidence, and fail the run. An unchanged run creates no issue. Existing review issues are not automatically closed, and baselines are never automatically overwritten. GitHub notification delivery follows your repository watch/Actions preferences.

## Review and accept a change

1. Open the issue's workflow run and download the `schedule-comparison` artifact.
2. Read `before.png` and `after.png` for the affected academy. Compare adult class days, times, names, Gi/No-Gi details, additions and removals only. Keep locations fixed and exclude kids classes. Preserve the known Beacon rotation anchor unless an explicit class update changes that rotation.
3. Propose any necessary changes to `index.html` for review. Do not update the calendar on pixel differences alone.
4. After review, copy the reviewed `after.png` from the artifact to `monitor/baselines/<source-id>.png`. Use the reviewed file, not a fresh download that may have changed again. Commit the accepted baseline with the calendar edit, or by itself if only cosmetic details changed.
5. Run the workflow manually, then close the issue after the check succeeds. For fetch errors, fix the source instead of accepting an empty/error baseline.

Local check:

```sh
python3 -m venv .venv
.venv/bin/pip install -r monitor/requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/check_schedules.py
```

GitHub can delay scheduled jobs and disables scheduled workflows in public repositories after 60 days without repository activity. Re-enable the workflow in Actions if that occurs; a monthly run by itself does not guarantee indefinite scheduling. See https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule.

## October 5, 2026 correction

Snake Hill's accepted baseline and calendar now use the newer image supplied by the user on October 5. The website was still serving the July image (SHA-256 `12494fc1d728a7bc29feb2d6062adb42582ebe94abe6f8a1b9c518da7272cc6e`), explaining the successful October 5 check. The new accepted image has SHA-256 `f7198d5394ab738c7930294903b2d0aaf1d59b2a6b8b6851595ae5c6ad89f1cd`.

Snake Hill now resolves the image from its schedule page on every run, using a configurable image-path pattern. Missing, ambiguous, or inaccessible page images are errors, with no silent fallback to the old URL. A replacement with an unrecognizable filename requires adjusting that pattern. Evolution still uses fixed CDN URLs.

Until Snake Hill updates its website, the monitor will flag that site's disagreement with the accepted user-supplied schedule. Do not revert the calendar or baseline to the stale website image. A successful check only means the monitored sources match the accepted images; changes shared privately or elsewhere cannot be discovered by checking these sources.
