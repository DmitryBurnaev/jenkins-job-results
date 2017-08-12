# coding=utf-8

from wtforms import Form, StringField
from wtforms.validators import DataRequired, Length


class JenkinsJobForm(Form):
    name = StringField(
        'Job Name', [DataRequired(), Length(5, 256, u'Too more symbols...')]
    )
