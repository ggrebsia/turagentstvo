from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Tour, Booking
from forms import LoginForm, RegisterForm, TourForm, CreateTourForm, EditTourForm, BookingForm
from config import Config
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config.from_object(Config)

# Папка для загрузки изображений
UPLOAD_FOLDER = 'static/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Инициализация базы данных
db.init_app(app)

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Создание таблиц и тестовых данных
with app.app_context():
    db.drop_all()  # Удаляем старые таблицы
    db.create_all()  # Создаём новые таблицы
    if Tour.query.count() == 0:
        tours = [
            Tour(title="Тур в Париж", description="Романтическое путешествие", price=1200.0, duration=5, is_draft=False, country="France", image_url="images/paris.jpg"),
            Tour(title="Тур в Токио", description="Знакомство с Японией", price=2000.0, duration=7, is_draft=False, country="Japan", image_url="images/tokyo.jpg"),
            Tour(title="Тур в Рим", description="Историческое приключение", price=1500.0, duration=6, is_draft=False, country="Italy", image_url="images/rome.jpg")
        ]
        db.session.add_all(tours)
        db.session.commit()
    if User.query.filter_by(username="admin").first() is None:
        admin = User(username="admin", is_admin=True)
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

# Главная страница
@app.route('/')
def index():
    login_form = LoginForm()
    register_form = RegisterForm()
    # Выбираем 2 популярных тура (или все утверждённые)
    popular_tours = Tour.query.filter_by(is_draft=False).limit(2).all()
    return render_template('index.html', login_form=login_form, register_form=register_form, popular_tours=popular_tours)

# Страница туров
@app.route('/tours')
def tours():
    login_form = LoginForm()
    register_form = RegisterForm()
    approved_tours = Tour.query.filter_by(is_draft=False).all()
    user_drafts = []
    if current_user.is_authenticated:
        user_drafts = Tour.query.filter_by(user_id=current_user.id, is_draft=True).all()
    return render_template('tours.html', approved_tours=approved_tours, user_drafts=user_drafts, login_form=login_form, register_form=register_form)
# Страница конкретного тура
@app.route('/tour/<int:id>', methods=['GET', 'POST'])
def tour_detail(id):
    login_form = LoginForm()
    register_form = RegisterForm()
    tour = Tour.query.get_or_404(id)
    form = BookingForm()
    if request.method == 'POST' and current_user.is_authenticated and form.validate_on_submit():
        booking = Booking(
            user_id=current_user.id,
            tour_id=tour.id,
            date=form.date.data
        )
        db.session.add(booking)
        db.session.commit()
        flash('Тур успешно забронирован!', 'success')
        return redirect(url_for('tours'))
    elif request.method == 'POST' and current_user.is_authenticated:
        flash('Ошибка при бронировании. Проверьте дату.', 'danger')
    return render_template('tour_detail.html', tour=tour, form=form, login_form=login_form, register_form=register_form)

# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    login_form = LoginForm()
    register_form = RegisterForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(username=login_form.username.data).first()
        if user and user.check_password(login_form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('index.html', login_form=login_form, register_form=register_form)

# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    login_form = LoginForm()
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        existing_user = User.query.filter_by(username=register_form.username.data).first()
        if existing_user:
            flash('Уже есть профиль с таким логином', 'danger')
            return render_template('index.html', login_form=login_form, register_form=register_form)
        user = User(username=register_form.username.data)
        user.set_password(register_form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('index'))
    for field, errors in register_form.errors.items():
        for error in errors:
            flash(f'Ошибка в поле {field}: {error}', 'danger')
    return render_template('index.html', login_form=login_form, register_form=register_form)

# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Создание своего тура
@app.route('/create_tour', methods=['GET', 'POST'])
@login_required
def create_tour():
    login_form = LoginForm()
    register_form = RegisterForm()
    form = CreateTourForm()
    if form.validate_on_submit():
        image_url = None
        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = f"images/{filename}"
        
        tour = Tour(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            duration=form.duration.data,
            is_draft=True,
            user_id=current_user.id,
            country=form.country.data,
            image_url=image_url
        )
        db.session.add(tour)
        db.session.commit()
        flash('Ваш тур отправлен на утверждение администратору!', 'success')
        return redirect(url_for('tours'))
    return render_template('create_tour.html', form=form, login_form=login_form, register_form=register_form)

# Личный кабинет
@app.route('/profile')
@login_required
def profile():
    login_form = LoginForm()
    register_form = RegisterForm()
    bookings = Booking.query.filter_by(user_id=current_user.id).all()
    user_drafts = Tour.query.filter_by(user_id=current_user.id, is_draft=True).all()
    booked_tours = [(booking, Tour.query.get(booking.tour_id)) for booking in bookings]
    return render_template('profile.html', booked_tours=booked_tours, user_drafts=user_drafts, username=current_user.username, login_form=login_form, register_form=register_form)

# Удаление бронирования
@app.route('/delete_booking/<int:id>', methods=['POST'])
@login_required
def delete_booking(id):
    login_form = LoginForm()
    register_form = RegisterForm()
    booking = Booking.query.get_or_404(id)
    if booking.user_id != current_user.id:
        flash('Вы не можете удалить это бронирование!', 'danger')
        return redirect(url_for('profile'))
    db.session.delete(booking)
    db.session.commit()
    flash('Бронирование успешно удалено!', 'success')
    return redirect(url_for('profile'))

# Админ-панель
@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    login_form = LoginForm()
    register_form = RegisterForm()
    form = TourForm()
    if form.validate_on_submit():
        image_url = None
        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = f"images/{filename}"
        
        tour = Tour(
            title=form.title.data,
            description=form.description.data,
            price=form.price.data,
            duration=form.duration.data,
            is_draft=False,
            country=form.country.data,
            image_url=image_url
        )
        db.session.add(tour)
        db.session.commit()
        flash('Тур успешно добавлен!', 'success')
        return redirect(url_for('admin'))
    tours = Tour.query.filter_by(is_draft=False).all()
    drafts = Tour.query.filter_by(is_draft=True).all()
    return render_template('admin.html', form=form, tours=tours, drafts=drafts, login_form=login_form, register_form=register_form)

# Редактирование тура
@app.route('/edit_tour/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_tour(id):
    if not current_user.is_admin:
        return redirect(url_for('index'))
    login_form = LoginForm()
    register_form = RegisterForm()
    tour = Tour.query.get_or_404(id)
    form = EditTourForm()
    if form.validate_on_submit():
        tour.title = form.title.data
        tour.description = form.description.data
        tour.price = form.price.data
        tour.duration = form.duration.data
        tour.country = form.country.data
        tour.is_draft = form.is_draft.data == 'True'
        if form.image.data and allowed_file(form.image.data.filename):
            filename = secure_filename(form.image.data.filename)
            form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            tour.image_url = f"images/{filename}"
        db.session.commit()
        flash('Тур успешно отредактирован!', 'success')
        return redirect(url_for('admin'))
    elif request.method == 'GET':
        form.title.data = tour.title
        form.description.data = tour.description
        form.price.data = tour.price
        form.country.data = tour.country
        form.is_draft.data = str(tour.is_draft)
    return render_template('edit_tour.html', form=form, tour=tour, login_form=login_form, register_form=register_form)

# Утверждение тура
@app.route('/approve_tour/<int:id>', methods=['GET'])
@login_required
def approve_tour(id):
    if not current_user.is_admin:
        flash('Доступ запрещён.', 'danger')
        return redirect(url_for('index'))
    tour = Tour.query.get_or_404(id)
    if not tour.is_draft:
        flash('Тур уже опубликован.', 'warning')
        return redirect(url_for('admin'))
    tour.is_draft = False
    db.session.commit()
    flash('Тур успешно утверждён!', 'success')
    return redirect(url_for('admin'))

# Обработка ошибок
@app.errorhandler(404)
def page_not_found(e):
    login_form = LoginForm()
    register_form = RegisterForm()
    return render_template('404.html', login_form=login_form, register_form=register_form), 404

if __name__ == '__main__':
    app.run(debug=True)