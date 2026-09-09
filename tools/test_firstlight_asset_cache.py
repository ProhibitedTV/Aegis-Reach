"""Exercise cache freshness against real temporary files, never installed assets."""
from pathlib import Path
import os
import tempfile
import unittest
from firstlight_asset_cache import synchronize


class OriginalAssetCacheTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.art = self.root / 'original'
        self.art.mkdir()
        self.stamp = self.root / 'stamp.json'
        (self.art / 'Lab.fpe').write_text('model = Lab.x\ntextured = atlas.png\n')
        (self.art / 'Lab.x').write_bytes(b'original mesh')
        (self.art / 'atlas.png').write_bytes(b'original texture')
        self.cache = self.art / 'Lab.dbo'
        self.cache.write_bytes(b'compiled mesh')

    def sync(self):
        return synchronize(self.art, self.stamp)

    def test_first_run_then_unchanged(self):
        self.assertEqual(self.sync()['invalidated'], ['Lab.dbo'])
        self.cache.write_bytes(b'fresh compiled mesh')
        self.assertEqual(self.sync()['invalidated'], [])
        self.assertEqual(self.cache.read_bytes(), b'fresh compiled mesh')

    def test_mesh_change_even_with_preserved_timestamp(self):
        self.sync()
        self.cache.write_bytes(b'cached')
        mesh = self.art / 'Lab.x'
        old = mesh.stat()
        mesh.write_bytes(b'revised mesh')
        os.utime(mesh, ns=(old.st_atime_ns, old.st_mtime_ns))
        self.assertEqual(self.sync()['invalidated'], ['Lab.dbo'])

    def test_texture_and_material_changes(self):
        self.sync()
        for filename in ('atlas.png', 'Lab.fpe'):
            self.cache.write_bytes(b'cached')
            with (self.art / filename).open('ab') as stream:
                stream.write(b'\n; material revision')
            self.assertEqual(self.sync()['invalidated'], ['Lab.dbo'])

    def test_unowned_caches_survive(self):
        unowned = [self.root / 'DLC.dbo', self.art / 'Unrelated.dbo']
        for path in unowned:
            path.write_bytes(b'untouched')
        self.sync()
        for path in unowned:
            self.assertEqual(path.read_bytes(), b'untouched')

    def test_external_model_fails_before_deletion(self):
        (self.art / 'Lab.fpe').write_text('model = ../DLC.x')
        with self.assertRaises(ValueError):
            self.sync()
        self.assertTrue(self.cache.is_file())
        self.assertFalse(self.stamp.exists())

    def test_missing_model_fails_before_deletion(self):
        (self.art / 'Lab.x').unlink()
        with self.assertRaises(FileNotFoundError):
            self.sync()
        self.assertTrue(self.cache.is_file())
        self.assertFalse(self.stamp.exists())


if __name__ == '__main__':
    unittest.main()
