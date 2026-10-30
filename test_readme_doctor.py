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

class T3(unittest.TestCase):
    def test_402_requirements(self):
        from x402_server import requirements
        r = requirements('https://x/score')
        self.assertEqual(r['payTo'], '0xdee5d17120fe5b415858c977555fd0c4ed6d3fda')
        self.assertEqual(r['scheme'], 'exact')

class T4(unittest.TestCase):
    def test_cli_eval_and_md(self):
        from cli import evaluate, to_markdown
        s, f = evaluate('# T\n')
        self.assertLess(s, 100)
        self.assertIn('Score:', to_markdown('x', s, f))
