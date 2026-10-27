from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms.validators import InputRequired


class DayForm(FlaskForm):
    day = DateField("Dzień", validators=[InputRequired("Podaj dzień.")])


class RangeForm(FlaskForm):
    start_date = DateField("Od", validators=[InputRequired("Podaj datę początkową.")])
    end_date = DateField("Do", validators=[InputRequired("Podaj datę końcową.")])
