from flask import Blueprint, render_template, redirect, url_for, flash, request
from . import db
from .exceptions import InvalidResponse
from .forms import SiteForm
from .models import Scrape

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/', methods=['GET', 'POST'])
def index():
    form = SiteForm(request.form)
    if form.validate_on_submit():
        try:
            row = Scrape.create(form)
            row.save()

            flash(
                f'Supplied URL successfully indexed.<br/>'
                f'Found \'{row.word}\' <strong>{row.hits}</strong> times.',
                'success'
            )
            return redirect(url_for('main.show', id=row.id))
        except InvalidResponse as e:
            flash(e, 'warning')

    elif form.is_submitted():
        flash('The given data was invalid.', 'danger')

    rows = Scrape.get_all_rows()
    return render_template('index.jinja',
                           form=form,
                           rows=db.paginate(rows,
                                            max_per_page=5))


@main_blueprint.route('/<int:id>', methods=['GET'])
def show(id):
    form = SiteForm(request.form)
    rows = Scrape.get_by_id(id)
    return render_template('index.jinja',
                           form=form,
                           rows=db.paginate(rows,
                                            page=1,
                                            per_page=1,
                                            max_per_page=1))
