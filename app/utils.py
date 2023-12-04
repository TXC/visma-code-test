from . import db


class ModelMixin:

    def save(self):
        # Save this model to the database.
        db.session.add(self)
        db.session.commit()
        return self
