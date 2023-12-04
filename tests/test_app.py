from unittest import TestCase, main

from app import db, create_app
from app.models import Scrape

app = create_app(environment='testing')


class TestApp(TestCase):
    url = 'https://en.wikipedia.org/wiki/List_of_Advanced_Dungeons' \
          '_%26_Dragons_2nd_edition_monsters'
    subtests = [
        ('monsters', 313),
        ('unique', 6),
        ('Monstr', 0),
        ('Monster', 250),
        ('Manual', 381),
        ('navbox', 154),
        ('padding', 70),
        ('Blue', 5),
        ('blue', 1),
    ]

    subtests_partial = [
        ('monsters', 422),
        ('unique', 6),
        ('Monstr', 815),
        ('Monster', 415),
        ('Manual', 416),
        ('navbox', 154),
        ('padding', 70),
        ('Blue', 5),
        ('blue', 8),
    ]

    def setUp(self):
        self.client = app.test_client()
        self.app_ctx = app.app_context()
        self.app_ctx.push()
        db.create_all()
        for _ in range(50):
            seed = Scrape.seed()
            seed.save()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_ctx.pop()

    def create(self, url: str, word: str, partial: bool = False):
        data = dict(url=url, word=word)
        if partial:
            data['partial'] = 'y'

        return self.client.post('/',
                                data=data,
                                follow_redirects=True)

    def get_result(self, id: int = None):
        return self.client.get(f'/{id}', follow_redirects=True)

    def test_index_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        for test in self.subtests:
            with self.subTest(f'Testing word: {test[0]}'):
                response = self.create(self.url, test[0])
                self.assertIn(b'Supplied URL successfully indexed.',
                              response.data)

                found_str = 'Found \'%s\' <strong>%d</strong> times.' % test
                self.assertIn(found_str.encode('ascii'), response.data)

    def test_create_partial(self):
        for test in self.subtests_partial:
            with self.subTest(f'Testing word: {test[0]}'):
                response = self.create(self.url, word=test[0], partial=True)
                print(response.data.decode('utf-8'))
                self.assertIn(b'Supplied URL successfully indexed.',
                              response.data)

                found_str = 'Found \'%s\' <strong>%d</strong> times.' % test
                self.assertIn(found_str.encode('ascii'), response.data)

    def test_results(self):
        for test in self.subtests:
            with self.subTest(f'Testing word: {test[0]}'):
                response = self.create(self.url, test[0])
                query = db.select(Scrape).filter(Scrape.word == test[0]
                                                 ).order_by(Scrape.id.desc())
                row = db.session.scalar(query)

                response = self.get_result(row.id)
                self.assertNotIn(b'Supplied URL successfully indexed.',
                                 response.data)

                self.assertIn(f'<td>{test[0]}</td>',
                              response.data.decode('utf-8'))
                self.assertIn(f'<td>{test[1]}</td>',
                              response.data.decode('utf-8'))
                self.assertIn(f'<td>{row.hits}</td>',
                              response.data.decode('utf-8'))
                self.assertIn(f'<td>{row.url}</td>',
                              response.data.decode('utf-8'))
                self.assertIn(f'<td>{row.word}</td>',
                              response.data.decode('utf-8'))
                self.assertIn(f'<td>{row.time_to_load}s</td>',
                              response.data.decode('utf-8'))
                self.assertIn(f'<td>{row.created_at}</td>',
                              response.data.decode('utf-8'))

    def test_results_partial(self):
        for test in self.subtests_partial:
            with self.subTest(f'Testing word: {test[0]}'):
                response = self.create(self.url, test[0], partial=True)
                query = db.select(Scrape).filter(Scrape.word == test[0]
                                                 ).order_by(Scrape.id.desc())
                row = db.session.scalar(query)

                response = self.get_result(row.id)
                self.assertNotIn(b'Supplied URL successfully indexed.',
                                 response.data)

                self.assertIn(f'<td>{test[0]}</td>',
                              response.data.decode('utf-8'))
                self.assertIn(f'<td>{test[1]}</td>',
                              response.data.decode('utf-8'))
                self.assertIn(f'<td>{row.hits}</td>',
                              response.data.decode('utf-8'))
                self.assertIn(f'<td>{row.url}</td>',
                              response.data.decode('utf-8'))
                self.assertIn(f'<td>{row.word}</td>',
                              response.data.decode('utf-8'))
                self.assertIn(f'<td>{row.time_to_load}s</td>',
                              response.data.decode('utf-8'))
                self.assertIn(f'<td>{row.created_at}</td>',
                              response.data.decode('utf-8'))


if __name__ == "__main__":
    main()
