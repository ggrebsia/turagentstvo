from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, FloatField, IntegerField, SubmitField, SelectField, FileField, PasswordField
from wtforms.validators import DataRequired, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])  # Изменено на PasswordField
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])  # Изменено на PasswordField
    submit = SubmitField('Зарегистрироваться')

class TourForm(FlaskForm):
    title = StringField('Название тура', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    image = FileField('Изображение')
    country = SelectField('Страна', choices=[
        ('Japan', 'Япония'), ('France', 'Франция'), ('Italy', 'Италия'),
        ('Spain', 'Испания'), ('USA', 'США'), ('Thailand', 'Таиланд'),
        ('Australia', 'Австралия'), ('Brazil', 'Бразилия'), ('Egypt', 'Египет'),
        ('Greece', 'Греция')
    ], validators=[DataRequired()])
    price = FloatField('Цена ($)', validators=[DataRequired()])
    duration = IntegerField('Длительность (дни)', validators=[DataRequired()])
    submit = SubmitField('Добавить')
    
class CreateTourForm(FlaskForm):
    title = StringField('Название тура', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    image = FileField('Изображение')
    country = SelectField('Страна', choices=[
        ('Japan', 'Япония'), ('France', 'Франция'), ('Italy', 'Италия'),
        ('Spain', 'Испания'), ('USA', 'США'), ('Thailand', 'Таиланд'),
        ('Australia', 'Австралия'), ('Brazil', 'Бразилия'), ('Egypt', 'Египет'),
        ('Greece', 'Греция')
    ], validators=[DataRequired()])
    price = FloatField('Цена ($)', validators=[DataRequired()])
    duration = IntegerField('Длительность (дни)', validators=[DataRequired()])
    submit = SubmitField('Отправить на утверждение')

class EditTourForm(FlaskForm):
    title = StringField('Название тура', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    image = FileField('Изображение')
    country = SelectField('Страна', choices=[
        ('Japan', 'Япония'), ('France', 'Франция'), ('Italy', 'Италия'),
        ('Spain', 'Испания'), ('USA', 'США'), ('Thailand', 'Таиланд'),
        ('Australia', 'Австралия'), ('Brazil', 'Бразилия'), ('Egypt', 'Египет'),
        ('Greece', 'Греция')
    ], validators=[DataRequired()])
    price = FloatField('Цена ($)', validators=[DataRequired()])
    duration = IntegerField('Длительность (дни)', validators=[DataRequired()])
    is_draft = SelectField('Статус', choices=[('True', 'Черновик'), ('False', 'Опубликован')])
    submit = SubmitField('Сохранить')
class BookingForm(FlaskForm):
    date = DateField('Дата поездки', validators=[DataRequired()], format='%Y-%m-%d')
    submit = SubmitField('Забронировать')