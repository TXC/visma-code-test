from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, SubmitField
from wtforms.validators import InputRequired, Length, URL, ValidationError


class SiteForm(FlaskForm):
    url = StringField(
        'URL to visit',
        validators=[InputRequired('You need to enter a valid URL'),
                    URL(True, 'You must enter a valid URL'),
                    Length(4, 250)],
        description='An url to a webpage that may or may not contain the word'
    )

    word = StringField(
        'Word to search for',
        validators=[InputRequired('You need to enter a word to search for'),
                    Length(2)],
        description='A single word to search for.'
    )

    partial = BooleanField('Partial match',
                           description='If the word should partially match.')

    submit = SubmitField('Search')

    def validate_url(form, field):
        if field.data[:4] != 'http' and field.data[:4] != 'www.':
            raise ValidationError('URL must begin with http or https'
                                  'We got: %s' % field.data[:4])
