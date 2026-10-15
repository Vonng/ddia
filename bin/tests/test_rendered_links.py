from pathlib import Path
import importlib.util
import tempfile
import unittest


spec = importlib.util.spec_from_file_location(
    'rendered_links', Path(__file__).resolve().parents[1]/'check-rendered-links.py'
)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


class RenderedLinksTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(); self.addCleanup(directory.cleanup)
        self.root = Path(directory.name); self.public = self.root/'public'
        (self.root/'content/zh').mkdir(parents=True)
        (self.root/'content/zh/ch1.md').write_text('Chapter source')
        (self.public/'ch1').mkdir(parents=True)
        (self.public/'index.html').write_text('<a href="/ch1/#section">Chapter</a>')
        (self.public/'ch1/index.html').write_text('<h2 id="section">Section</h2>')

    def test_existing_fragment_and_same_site_absolute_url_pass(self):
        (self.public/'index.html').write_text('<a href="https://ddia.vonng.com/ch1/#section">Chapter</a>')
        self.assertEqual(qa.run_checks(self.root, self.public)['errors'], [])

    def test_missing_fragment_and_resource_fail(self):
        (self.public/'index.html').write_text('<a href="/ch1/#missing">X</a><img src="/missing.png">')
        errors = qa.run_checks(self.root, self.public)['errors']
        self.assertEqual({e['check'] for e in errors}, {'missing rendered fragment', 'missing rendered target'})

    def test_cached_generated_destination_does_not_mutate_source_iteration(self):
        (self.public/'generated').mkdir()
        (self.public/'generated/index.html').write_text('<h2 id="extra">Generated</h2>')
        (self.public/'index.html').write_text('<a href="/generated/#extra">X</a>')
        report = qa.run_checks(self.root, self.public)
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['totals']['source_pages'], 2)
        self.assertEqual(report['totals']['parsed_pages'], 3)

    def test_default_scope_skips_other_editions_but_all_scope_checks_them(self):
        (self.public/'index.html').write_text('<a href="/v1/ch1/#missing">Old</a>')
        self.assertEqual(qa.run_checks(self.root, self.public)['errors'], [])
        self.assertTrue(qa.run_checks(self.root, self.public, all_pages=True)['errors'])

    def test_missing_build_fails_instead_of_reporting_empty_success(self):
        (self.public/'index.html').unlink(); (self.public/'ch1/index.html').unlink()
        self.assertTrue(qa.run_checks(self.root, self.public, all_pages=True)['errors'])

    def test_second_edition_checks_generated_pages_and_old_edition_destinations(self):
        for edition in ('v1', 'v1_tw'):
            (self.public/edition/'ch1').mkdir(parents=True)
            (self.public/edition/'ch1/index.html').write_text(
                '<h2 id="archive">Archive</h2><a href="/legacy-missing/">Existing old error</a>')
        for page in ('tw/_print', 'alias'):
            (self.public/page).mkdir(parents=True)
            (self.public/page/'index.html').write_text('<a href="/ch1/#section">Valid</a>')
        (self.public/'index.html').write_text('<a href="/v1/ch1/#archive">Old target</a>')
        report = qa.run_checks(self.root, self.public, second_edition=True)
        self.assertEqual(report['errors'], [])
        self.assertEqual(report['totals']['source_pages'], 4)
        self.assertTrue(qa.run_checks(self.root, self.public, all_pages=True)['errors'])
        (self.public/'index.html').write_text('<a href="/v1/nonexistent/">Bad old target</a>')
        (self.public/'tw/_print/index.html').write_text('<a href="/ch1/#missing">Bad print target</a>')
        errors = qa.run_checks(self.root, self.public, second_edition=True)['errors']
        self.assertEqual({error['target'] for error in errors}, {'/v1/nonexistent/', '/ch1/#missing'})

    def test_all_scope_checks_first_edition_heading_and_figure_links_in_print(self):
        for edition, word in (('v1', '树'), ('v1_tw', '樹')):
            chapter = self.public / edition / 'ch3' / 'index.html'
            printed = self.public / edition / '_print' / 'index.html'
            chapter.parent.mkdir(parents=True)
            printed.parent.mkdir(parents=True)
            links = f'<a href="/{edition}/ch3/#B{word}">Tree</a><a href="fig3-11.png">Figure</a>'
            chapter.write_text(f'<h2 id="b{word}">Tree</h2><figure id="fig_ddia_0311"></figure>' + links)
            printed.write_text(links)

        report = qa.run_checks(self.root, self.public, all_pages=True)
        self.assertEqual(report['totals']['source_pages'], 6)
        self.assertEqual(len(report['errors']), 8)
        self.assertEqual({error['source'] for error in report['errors']},
                         {'/v1/ch3/', '/v1/_print/', '/v1_tw/ch3/', '/v1_tw/_print/'})
        self.assertEqual({error['check'] for error in report['errors']},
                         {'missing rendered fragment', 'missing rendered target'})

        for edition, word in (('v1', '树'), ('v1_tw', '樹')):
            for relative in ('ch3/index.html', '_print/index.html'):
                path = self.public / edition / relative
                path.write_text(path.read_text().replace(f'#B{word}', f'#b{word}')
                                .replace('fig3-11.png', f'/{edition}/ch3/#fig_ddia_0311'))
        self.assertEqual(qa.run_checks(self.root, self.public, all_pages=True)['errors'], [])


if __name__ == '__main__':
    unittest.main()
