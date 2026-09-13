"""실제 탐색 오류, 입력 손상과 본문 보존을 검사한다."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
import structure


class StructureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'docs').mkdir()
        self.item = dict(path='guides/sample', type='guide', hero='assets/hero.webp',
                         chapters=['01-start.md', '02-end.md'], support=['VALIDATION.md'],
                         first_diagram=None, diagram_note='실행 표로 설명')
        folder = self.root / self.item['path']
        (folder / 'assets').mkdir(parents=True)
        (folder / self.item['hero']).write_bytes(b'image fixture')
        (self.root / 'README.md').write_text('![표지](guides/sample/assets/hero.webp)\n')
        (folder / 'README.md').write_text('# 소개\n\n![표지](assets/hero.webp)\n\n## 시작\n\n본문\n')
        for name in self.item['chapters'] + self.item['support']:
            (folder / name).write_text(f'# {name}\n\n본문\n\n```md\n# 코드 제목\n**/*.py\n```\n')
        self.save()
        self.assertEqual(structure.run(self.root, True)[0], [])

    def save(self):
        (self.root / 'docs/content-index.json').write_text(json.dumps(dict(version=1, items=[self.item])))

    def test_wrong_destination_detected_and_repaired(self):
        path = self.root / self.item['path'] / '01-start.md'
        path.write_text(path.read_text().replace('(02-end.md)', '(README.md)', 1))
        self.assertTrue(structure.run(self.root)[0])
        self.assertFalse(structure.run(self.root, True)[0])
        self.assertFalse(structure.run(self.root)[0])

    def test_missing_footer(self):
        path = self.root / self.item['path'] / '02-end.md'
        path.write_text(path.read_text().split(structure.MARKERS[2])[0])
        self.assertTrue(structure.run(self.root)[0])

    def test_idempotence_and_body_preservation(self):
        path = self.root / self.item['path'] / '01-start.md'
        before = path.read_bytes()
        self.assertEqual(structure.run(self.root, True), ([], 0))
        self.assertEqual(path.read_bytes(), before)
        body = structure.strip_managed(path.read_text())
        self.assertIn('```md\n# 코드 제목\n**/*.py\n```', body)

    def test_chapter_order_is_explicit(self):
        self.item['chapters'].reverse()
        self.save()
        self.assertTrue(structure.run(self.root)[0])
        nav = structure.navigation(self.root, self.item, '02-end.md')
        self.assertIn('다음: 01-start.md', nav)

    def test_unregistered_document(self):
        (self.root / self.item['path'] / 'CARD.md').write_text('# 카드\n')
        with self.assertRaisesRegex(ValueError, '미등록'):
            structure.run(self.root, True)

    def test_duplicate_document(self):
        self.item['support'].append('01-start.md')
        self.save()
        with self.assertRaisesRegex(ValueError, '중복'):
            structure.run(self.root)

    def test_path_escape(self):
        self.item['hero'] = '../../../outside.webp'
        self.save()
        with self.assertRaisesRegex(ValueError, '밖 경로'):
            structure.run(self.root)

    def test_real_second_h1_is_rejected(self):
        path = self.root / self.item['path'] / '01-start.md'
        path.write_text(path.read_text()+'\n# 두 번째 제목\n')
        with self.assertRaisesRegex(ValueError, 'H1'):
            structure.run(self.root)

    def test_fenced_markers_are_content(self):
        text = '# 제목\n\n```md\n'+structure.MARKERS[0]+'\n코드\n'+structure.MARKERS[1]+'\n```\n'
        rendered = structure.render(text, '[목차](README.md)')
        self.assertIn('```md\n'+structure.MARKERS[0], structure.strip_managed(rendered))
        self.assertEqual(structure.render(rendered, '[목차](README.md)'), rendered)

    def test_broken_marker_fails_before_writing(self):
        path = self.root / self.item['path'] / '02-end.md'
        path.write_text(path.read_text().replace(structure.MARKERS[3], ''))
        before = {p:p.read_bytes() for p in self.root.rglob('*.md')}
        with self.assertRaisesRegex(ValueError, '손상'):
            structure.run(self.root, True)
        self.assertEqual(before, {p:p.read_bytes() for p in before})

    def test_catalog_hero_mismatch(self):
        (self.root / 'README.md').write_text('# 목록\n')
        self.assertTrue(structure.run(self.root, True)[0])

    def test_diagram_needs_real_embed(self):
        folder = self.root / self.item['path']
        (folder / 'map.svg').write_text('<svg/>')
        self.item['first_diagram'] = dict(page='README.md', asset='map.svg')
        self.save()
        self.assertTrue(structure.run(self.root)[0])

    def test_duplicate_registration_does_not_mutate(self):
        before = (self.root / 'docs/content-index.json').read_bytes()
        with self.assertRaisesRegex(ValueError, '이미 등록'):
            structure.register(self.root, self.item['path'])
        self.assertEqual(before, (self.root / 'docs/content-index.json').read_bytes())

    def test_label_escapes_link_brackets(self):
        path = self.root / self.item['path'] / '02-end.md'
        path.write_text('# [검증] 결과\n\n본문\n')
        self.assertIn(r'\[검증\]', structure.navigation(self.root, self.item, '01-start.md'))


if __name__ == '__main__':
    unittest.main()
