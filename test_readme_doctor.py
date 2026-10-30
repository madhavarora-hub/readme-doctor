import unittest
from server import score

class T(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(score('')['score'], 0)
    def test_full(self):
        t = '# Title\n\nThis project does a useful thing for many people daily.\n\n## Install\n\n```\npip install x\n```\n\n## Usage\n\nexample\n\n## License\n\nMIT\n\n## Contributing\n\nPRs welcome\n\n![b](https://img.shields.io/x)\n'
        self.assertEqual(score(t)['score'], 100)

if __name__ == '__main__':
    unittest.main()

class T2(unittest.TestCase):
    def test_template_fills_gaps(self):
        from templater import suggest
        from server import score
        out = suggest('# T\n')
        self.assertIn('## License', out)
        self.assertGreater(score('# T\n' + out)['score'], score('# T\n')['score'])
