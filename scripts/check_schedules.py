"""Compare schedule images; never modify the calendar or accepted baselines."""
import argparse
import hashlib
import io
import json
import shutil
import time
import urllib.request
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def fetch(url):
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={
                'User-Agent': 'BJJ-Schedule-Monitor/1.0', 'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(request, timeout=30) as response:
                data = response.read(15 * 1024 * 1024 + 1)
            if len(data) > 15 * 1024 * 1024:
                raise ValueError('Image exceeds 15 MB limit')
            return data
        except Exception:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)


def decode(data):
    with Image.open(io.BytesIO(data)) as image:
        image.load()
        return ImageOps.exif_transpose(image).convert('RGB')


def compare(before, after):
    # Same-size decoded pixels ignore PNG metadata and lossless re-encoding.
    # Resize only to align images; even tiny visible edits trigger review.
    if before.size != after.size:
        after = after.resize(before.size, Image.Resampling.LANCZOS)
    diff = ImageChops.difference(before, after)
    channels = diff.split()
    maximum = ImageChops.lighter(ImageChops.lighter(channels[0], channels[1]), channels[2])
    mask = maximum.point(lambda value: 255 if value > 12 else 0)
    pixels = mask.histogram()[255]
    return pixels > 0, pixels, diff


def check(sources, baselines, output, fetcher=fetch):
    output.mkdir(parents=True, exist_ok=True)
    results = []
    for source in sources:
        result = {'id': source['id'], 'name': source['name'], 'url': source['url']}
        try:
            baseline = baselines / (source['id'] + '.png')
            before = decode(baseline.read_bytes())
            data = fetcher(source['url'])
            after = decode(data)
            folder = output / source['id']
            folder.mkdir(exist_ok=True)
            shutil.copyfile(baseline, folder / 'before.png')
            after.save(folder / 'after.png')
            changed, pixels, diff = compare(before, after)
            result.update(status='changed' if changed else 'unchanged', changed_pixels=pixels,
                          sha256=hashlib.sha256(data).hexdigest(), size=list(after.size))
            if changed:
                diff.save(folder / 'diff.png')
        except Exception as error:
            result.update(status='error', error=str(error))
        results.append(result)
    report = {'results': results, 'needs_review': any(r['status'] != 'unchanged' for r in results)}
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'monitor-output')
    args = parser.parse_args()
    sources = json.loads((ROOT / 'monitor/sources.json').read_text())
    report = check(sources, ROOT / 'monitor/baselines', args.output)
    for result in report['results']:
        print(f"{result['name']}: {result['status']}")
    # The workflow uploads evidence and creates/updates an issue before failing.
    return 0


if __name__ == '__main__':
    main()
