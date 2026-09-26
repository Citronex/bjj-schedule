import importlib.util
import io
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw, PngImagePlugin

spec = importlib.util.spec_from_file_location('monitor', Path(__file__).resolve().parents[1] / 'scripts/check_schedules.py')
monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


def png(image, info=None):
    buffer = io.BytesIO()
    image.save(buffer, format='PNG', pnginfo=info)
    return buffer.getvalue()


class ScheduleMonitorTests(unittest.TestCase):
    def test_metadata_does_not_trigger_change(self):
        image = Image.new('RGB', (100, 100), 'white')
        info = PngImagePlugin.PngInfo()
        info.add_text('comment', 'New export')
        self.assertFalse(monitor.compare(monitor.decode(png(image)), monitor.decode(png(image, info)))[0])

    def test_small_class_time_edit_is_detected(self):
        before = Image.new('RGB', (1536, 1024), 'white')
        after = before.copy()
        ImageDraw.Draw(after).text((100, 100), '6:30', fill='black')
        self.assertTrue(monitor.compare(before, after)[0])

    def test_minor_channel_noise_is_ignored(self):
        self.assertFalse(monitor.compare(Image.new('RGB', (100, 100), (250, 250, 250)), Image.new('RGB', (100, 100), (249, 249, 249)))[0])

    def test_resize_same_flat_content(self):
        self.assertFalse(monitor.compare(Image.new('RGB', (100, 100), 'white'), Image.new('RGB', (200, 200), 'white'))[0])

    def test_errors_do_not_skip_other_sources_or_replace_baselines(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = png(Image.new('RGB', (100, 100), 'white'))
            for name in ['failed', 'unchanged', 'changed']:
                (root / (name + '.png')).write_bytes(data)
            sources = [{'id': name, 'name': name, 'url': name} for name in ['failed', 'unchanged', 'changed']]
            def fetch(url):
                if url == 'failed':
                    return b'<html>error page</html>'
                return data if url == 'unchanged' else png(Image.new('RGB', (100, 100), 'black'))
            report = monitor.check(sources, root, root / 'out', fetch)
            self.assertEqual([r['status'] for r in report['results']], ['error', 'unchanged', 'changed'])
            self.assertTrue(report['needs_review'])
            self.assertTrue((root / 'out/changed/diff.png').exists())
            self.assertEqual((root / 'changed.png').read_bytes(), data)


if __name__ == '__main__':
    unittest.main()
