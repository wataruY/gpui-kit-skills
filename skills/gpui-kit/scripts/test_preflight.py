"""Contract tests for local-only lookup and reference resolution."""
import tempfile
from pathlib import Path
import unittest

from api_lookup import cached_source, lookup
from resolve_ref import find_references, resolve_reference


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'skill'
        (self.root / 'reference/degraded').mkdir(parents=True)
        (self.root / 'reference/new-work.md').write_text('[role](degraded/documenter.md)')
        (self.root / 'reference/degraded/documenter.md').write_text('role')

    def test_link_is_relative_to_containing_document(self):
        result = resolve_reference(self.root, 'reference/new-work.md', 'degraded/documenter.md#contract')
        self.assertEqual(Path(result['path']), self.root / 'reference/degraded/documenter.md')
        self.assertEqual(result['fragment_unchecked'], 'contract')

    def test_wrong_prefix_is_not_silently_repaired(self):
        with self.assertRaisesRegex(ValueError, 'does not exist'):
            resolve_reference(self.root, 'reference/new-work.md', '../degraded/documenter.md')
        self.assertEqual(find_references(self.root, 'documenter.md'),
                         [str(self.root / 'reference/degraded/documenter.md')])

    def test_escape_and_external_links_are_rejected(self):
        for link in ['../../outside.md', '%2e%2e/%2e%2e/outside.md', '/etc/passwd',
                     'https://example.com/a.md', '//example.com/a.md']:
            with self.subTest(link=link), self.assertRaises(ValueError):
                resolve_reference(self.root, 'reference/new-work.md', link)

    def test_symlink_escape_is_not_listed_or_opened(self):
        outside = Path(self.tmp.name) / 'outside.md'
        outside.write_text('private')
        (self.root / 'reference/outside.md').symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'escapes'):
            resolve_reference(self.root, 'reference/new-work.md', 'outside.md')
        self.assertEqual(find_references(self.root, 'outside.md'), [])


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project = self.root / 'project'
        self.project.mkdir()
        self.cargo = self.root / 'cargo'
        self.lock(['0.8.0'])
        self.source = self.cache('index.crates.io-test', '0.8.0')

    def lock(self, versions, source='registry+https://github.com/rust-lang/crates.io-index'):
        (self.project / 'Cargo.lock').write_text('version = 4\n' + '\n'.join(
            f'[[package]]\nname = "gpui-pre"\nversion = "{v}"\nsource = "{source}"\n'
            for v in versions))

    def cache(self, registry, version):
        path = self.cargo / 'registry/src' / registry / f'gpui-pre-{version}'
        (path / 'src').mkdir(parents=True)
        (path / 'Cargo.toml').write_text(f'[package]\nname="gpui-pre"\nversion="{version}"\n')
        (path / 'src/lib.rs').write_text('pub trait StatefulInteractiveElement {\n'
                                         '    fn role(self, role: Role) -> Self;\n}\n'
                                         'pub enum IconName {\n    Trash2,\n}\n')
        return path

    def test_exact_lock_version_and_definition_location(self):
        self.cache('index.crates.io-test', '0.7.0')
        package, path = cached_source(self.project, self.cargo, 'gpui-pre')
        self.assertEqual(package['version'], '0.8.0')
        self.assertEqual(path, self.source)
        result = lookup(path, 'role')
        self.assertEqual(result['textual_matches'], 1)
        self.assertEqual(result['candidates'][0]['line'], 2)
        self.assertIn('StatefulInteractiveElement',
                      result['candidates'][0]['nearby_textual_owner_not_type_resolution']['text'])

    def test_variant_and_no_textual_match(self):
        self.assertEqual(lookup(self.source, 'Trash2')['textual_matches'], 1)
        self.assertEqual(lookup(self.source, 'Trash')['textual_matches'], 0)

    def test_multiple_versions_require_explicit_selection(self):
        self.lock(['0.7.0', '0.8.0'])
        with self.assertRaisesRegex(ValueError, 'Need one locked'):
            cached_source(self.project, self.cargo, 'gpui-pre')
        self.assertEqual(cached_source(self.project, self.cargo, 'gpui-pre', '0.8.0')[1], self.source)

    def test_duplicate_cache_does_not_pick_first(self):
        self.cache('index.crates.io-second', '0.8.0')
        with self.assertRaisesRegex(ValueError, 'found 2'):
            cached_source(self.project, self.cargo, 'gpui-pre')

    def test_missing_cache_does_not_download_or_create_it(self):
        self.lock(['0.9.0'])
        with self.assertRaisesRegex(ValueError, 'found 0'):
            cached_source(self.project, self.cargo, 'gpui-pre')
        self.assertFalse((self.cargo / 'registry/src/index.crates.io-test/gpui-pre-0.9.0').exists())

    def test_git_source_is_not_misrepresented_as_registry(self):
        self.lock(['0.8.0'], 'git+https://example.com/gpui#abc')
        with self.assertRaisesRegex(ValueError, 'git/path/vendor'):
            cached_source(self.project, self.cargo, 'gpui-pre')


if __name__ == '__main__':
    unittest.main()
