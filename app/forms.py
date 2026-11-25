from flask_wtf import FlaskForm
from wtforms import DateField, EmailField, IntegerField, PasswordField, StringField
from wtforms.validators import EqualTo, InputRequired, Length, Optional


class DayForm(FlaskForm):
    day = DateField("Dzień", validators=[InputRequired("Podaj dzień.")])
    trip_id = IntegerField(validators=[Optional()])


class RangeForm(FlaskForm):
    start_date = DateField("Od", validators=[InputRequired("Podaj datę początkową.")])
    end_date = DateField("Do", validators=[InputRequired("Podaj datę końcową.")])
    trip_id = IntegerField(validators=[Optional()])


class LoginForm(FlaskForm):
    email = EmailField("E-mail", validators=[InputRequired("Podaj e-mail.")])
    password = PasswordField("Hasło", validators=[InputRequired("Podaj hasło.")])


class RegisterForm(FlaskForm):
    name = StringField("Imię", validators=[InputRequired("Podaj imię."), Length(max=80)])
    email = EmailField("E-mail", validators=[InputRequired("Podaj e-mail."), Length(max=120)])
    password = PasswordField("Hasło", validators=[InputRequired("Podaj hasło."),
                                                  Length(min=8, message="Hasło musi mieć co najmniej 8 znaków.")])
    confirm = PasswordField("Powtórz hasło", validators=[EqualTo("password", "Hasła nie są takie same.")])
