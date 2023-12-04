import requests
import os
import re
from datetime import datetime

from . import db
from .exceptions import InvalidResponse
from .forms import SiteForm
from .utils import ModelMixin


class Scrape(db.Model, ModelMixin):

    __tablename__ = 'scraped'

    id = db.Column(db.Integer, primary_key=True)
    url: db.Mapped[str] = db.Column(db.String(255), nullable=False)
    word: db.Mapped[str] = db.Column(db.String(255), nullable=False)
    hits: db.Mapped[int] = db.Column(db.Integer, default=0)
    time_to_load: db.Mapped[float] = db.Column(db.Float, default=0)
    created_at: db.Mapped[datetime] = db.mapped_column(
        db.DateTime, insert_default=db.func.now())

    def __str__(self):
        return f'<Scrape: {self.url[:25]} {self.word} | {self.hits}>'

    @classmethod
    def seed(cls) -> "Scrape":
        from faker import Faker
        f = Faker()
        ttl = float(
            '{}.{}{}'.format(
                f.random_int(0, 9),
                f.random_int(),
                f.random_int()
            )
        )
        return cls(
            url=f.uri(),
            word=f.word(),
            hits=f.random_int(),
            time_to_load=ttl,
            created_at=f.date_time_this_month(before_now=True, after_now=True)
        )

    @classmethod
    def create(cls, form: SiteForm) -> "Scrape":
        page = requests.get(form.url.data,
                            timeout=os.environ.get('REQUEST_TIMEOUT', 1))
        if not page.ok:
            raise InvalidResponse(
                f'Supplied URL resulted in {page.status_code} {page.reason}'
            )

        partial = r''
        if not form.partial.data:
            partial = r'\b'

        search_string = r''
        search_string += re.escape(form.word.data)

        total_matches = 0
        for p in page.iter_content(1024, True):
            matches = re.findall(partial + search_string + partial, p)
            total_matches += len(matches)

        return cls(url=form.url.data,
                   word=form.word.data,
                   hits=total_matches,
                   time_to_load=page.elapsed.total_seconds())

    @staticmethod
    def get_all_rows():
        return db.select(Scrape).order_by(Scrape.created_at.desc())

    @staticmethod
    def get_by_id(id: int):
        return db.select(Scrape).filter(Scrape.id == id)
