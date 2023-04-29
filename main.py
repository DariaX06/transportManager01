from flask import Flask, abort, jsonify, render_template, redirect, make_response, request, session, url_for
from flask import make_response
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
import datetime
from flask_restful import reqparse, abort, Api, Resource

from data import db_session
from data.applications import Applications
from data.customers import Customer
from data.dispatchers import Dispatcher
from data.transport import Transport
from forms.add_application import AddApplicationForm
from forms.add_customer import AddCustomerForm
from forms.add_transport import AddTransportForm
from forms.login import LoginForm
from forms.register import RegisterForm

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/db.db")


@login_manager.user_loader
def load_user(user_id):
    login_type = session.get('login_type')
    db_sess = db_session.create_session()
    if login_type == 'dispatcher':
        return db_sess.query(Dispatcher).get(user_id)
    else:
        return db_sess.query(Customer).get(user_id)


# Личный кабинет диспетчера


@app.route('/dispatcher')
@app.route('/dispatcher/applications')
@login_required
def dispatcher():
    db_sess = db_session.create_session()
    applications = db_sess.query(Applications).filter(Applications.dispatcher_id == current_user.id,
                                                      Applications.reviewed == False)

    return render_template('dispatcher.html', title='Заявки', css_file=url_for('static', filename='css/dispatcher.css'),
                           content='applications', applications=applications)


@app.route('/dispatcher/transport')
@login_required
def dispatcher_transport():
    db_sess = db_session.create_session()
    transport = db_sess.query(Transport).filter(Transport.dispatcher == current_user)
    return render_template('dispatcher.html', title='Транспорт', css_file=url_for('static', filename='css/dispatcher.css'),
                           content='transport', transport=transport)


@app.route('/dispatcher/customers')
@login_required
def dispatcher_customers():
    db_sess = db_session.create_session()
    customers = db_sess.query(Customer).filter(Customer.dispatcher == current_user)
    return render_template('dispatcher.html', title='Заказчики', css_file=url_for('static', filename='css/dispatcher.css'),
                           content='customers', customers=customers)


@app.route('/dispatcher/tasks')
@login_required
def dispatcher_tasks():
    db_sess = db_session.create_session()
    tasks = db_sess.query(Applications).filter(Applications.dispatcher_id == current_user.id,
                                               Applications.accepted == True, Applications.completed == False)
    for item in tasks:
        if item.end.strftime('%d.%m.%Y') == datetime.datetime.now().strftime('%d.%m.%Y'):
            item.completed = True
            db_sess.query(Transport).filter(Transport.id == item.transport_id).first().status = True
            db_sess.commit()
    tasks = db_sess.query(Applications).filter(Applications.dispatcher_id == current_user.id,
                                               Applications.accepted == True, Applications.completed == False)
    return render_template('dispatcher.html', title='Задачи', css_file=url_for('static', filename='css/dispatcher.css'),
                           content='tasks', tasks=tasks)


@app.route('/dispatcher/add_customer', methods=['GET', 'POST'])
@login_required
def add_customer():
    form = AddCustomerForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('add_customer.html', title='Добавить сотрудника',
                                   form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Customer).filter(Customer.email == form.email.data).first():
            return render_template('add_customer.html', title='Добавить сотрудника',
                                   form=form, message="Такой пользователь уже есть")
        user = Customer(
            name=form.name.data,
            job_title=form.job_title.data,
            tel=form.tel.data,
            email=form.email.data,
            dispatcher_id=current_user.id
        )
        user.set_password(form.password.data)
        current_user.customers.append(user)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/dispatcher/customers')
    return render_template('add_customer.html', title='Добавить сотрудника', form=form, message="")


@app.route('/dispatcher/add_transport', methods=['GET', 'POST'])
@login_required
def add_transport():
    form = AddTransportForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        transport = Transport(
            name=form.name.data,
            coordinates=form.coordinates.data,
            state=form.state.data,
            dispatcher_id=current_user.id
        )

        current_user.transports.append(transport)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/dispatcher/transport')
    return render_template('add_transport.html', title='Добавить транспорт', form=form, message="")


@app.route('/dispatcher/edit_customers/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_customers(id):
    form = AddCustomerForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        customer = db_sess.query(Customer).filter(Customer.id == id, Customer.dispatcher == current_user).first()
        if customer:
            form.name.data = customer.name
            form.job_title.data = customer.job_title
            form.tel.data = customer.tel
            form.email.data = customer.email
            form.password.data = customer.password
            form.password_again.data = customer.password
        else:
            abort(404)
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('add_customer.html', title='Редактировать сотрудника',
                                   form=form, message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Customer).filter(Customer.email == form.email.data, Customer.id != id).first():
            return render_template('add_customer.html', title='Редактировать сотрудника',
                                   form=form, message="Такой пользователь уже есть")
        db_sess = db_session.create_session()
        customer = db_sess.query(Customer).filter(Customer.id == id, Customer.dispatcher == current_user).first()
        if customer:
            customer.name = form.name.data
            customer.job_title = form.job_title.data
            customer.tel = form.tel.data
            customer.email = form.email.data
            customer.set_password(form.password.data)
            db_sess.commit()
            return redirect('/dispatcher/customers')
        else:
            abort(404)
    return render_template('add_customer.html', title='Редактировать сотрудника', form=form, message="")


@app.route('/dispatcher/edit_transport/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_transport(id):
    form = AddTransportForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        transport = db_sess.query(Transport).filter(Transport.id == id, Transport.dispatcher == current_user).first()
        if transport:
            form.name.data = transport.name
            form.coordinates.data = transport.coordinates
            form.state.data = transport.state
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        transport = db_sess.query(Transport).filter(Transport.id == id, Transport.dispatcher == current_user).first()
        if transport:
            transport.name = form.name.data
            transport.coordinates = form.coordinates.data
            transport.state = form.state.data
            db_sess.commit()
            return redirect('/dispatcher/transport')
        else:
            abort(404)
    return render_template('add_transport.html', title='Редактировать транспорт', form=form, message="")


@app.route('/dispatcher/customer_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def customer_delete(id):
    db_sess = db_session.create_session()
    customer = db_sess.query(Customer).filter(Customer.id == id, Customer.dispatcher == current_user).first()
    if customer:
        db_sess.query(Applications).filter(Applications.customer_id == customer.id).delete()
        db_sess.delete(customer)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/dispatcher/customers')


@app.route('/dispatcher/transport_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def transport_delete(id):
    db_sess = db_session.create_session()
    transport = db_sess.query(Transport).filter(Transport.id == id, Transport.dispatcher == current_user).first()
    if transport:
        db_sess.query(Applications).filter(Applications.transport_id == transport.id).delete()
        db_sess.delete(transport)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/dispatcher/transport')


@app.route('/dispatcher/accept/<int:id>', methods=['GET', 'POST'])
@login_required
def accept(id):
    db_sess = db_session.create_session()
    application = db_sess.query(Applications).filter(Applications.id == id,
                                                     Applications.dispatcher_id == current_user.id).first()
    db_sess.query(Transport).filter(Transport.id == application.transport_id).first().status = False
    if application:
        application.reviewed = True
        application.accepted = True
        db_sess.commit()
    else:
        abort(404)
    return redirect('/dispatcher/applications')


@app.route('/dispatcher/complete/<int:id>', methods=['GET', 'POST'])
@login_required
def complete(id):
    db_sess = db_session.create_session()
    application = db_sess.query(Applications).filter(Applications.id == id,
                                                     Applications.dispatcher_id == current_user.id).first()
    db_sess.query(Transport).filter(Transport.id == application.transport_id).first().status = True
    if application:
        application.completed = True
        db_sess.commit()
    else:
        abort(404)
    return redirect('/dispatcher/tasks')


@app.route('/dispatcher/reject/<int:id>', methods=['GET', 'POST'])
@login_required
def reject(id):
    db_sess = db_session.create_session()
    application = db_sess.query(Applications).filter(Applications.id == id,
                                                     Applications.dispatcher_id == current_user.id).first()
    if application:
        application.reviewed = True
        application.accepted = False
        db_sess.commit()
    else:
        abort(404)
    return redirect('/dispatcher/applications')


# Личный кабинет заказчика


@app.route('/customer')
@app.route('/customer/applications')
@login_required
def customer():
    db_sess = db_session.create_session()
    applications = db_sess.query(Applications).filter(Applications.customer == current_user, Applications.reviewed == False)
    return render_template('customer.html', title='Заявки', css_file=url_for('static', filename='css/dispatcher.css'),
                           content='applications', applications=applications)


@app.route('/customer/transport')
@login_required
def customer_transport():
    db_sess = db_session.create_session()
    transport = db_sess.query(Transport).filter(Transport.dispatcher_id == current_user.dispatcher_id)
    return render_template('customer.html', title='Транспорт', css_file=url_for('static', filename='css/dispatcher.css'),
                           content='transport', transport=transport)


@app.route('/customer/dispatcher')
@login_required
def customer_dispatcher():
    db_sess = db_session.create_session()
    dispatcher = db_sess.query(Dispatcher).filter(Dispatcher.id == current_user.dispatcher_id).first()
    return render_template('customer.html', title='Диспетчер', css_file=url_for('static', filename='css/dispatcher.css'),
                           content='dispatcher', dispatcher=dispatcher)


@app.route('/customer/tasks')
@login_required
def customer_tasks():
    db_sess = db_session.create_session()
    tasks = db_sess.query(Applications).filter(Applications.customer_id == current_user.id,
                                               Applications.accepted == True, Applications.completed == False)
    return render_template('customer.html', title='Задачи', css_file=url_for('static', filename='css/dispatcher.css'),
                           content='tasks', tasks=tasks)


@app.route('/customer/add_application', methods=['GET', 'POST'])
@login_required
def add_application():
    db_sess = db_session.create_session()
    form = AddApplicationForm()
    form.transport_id.choices = [(item.id, item.name) for item in db_sess.query(Transport).filter(
        Transport.dispatcher_id == current_user.dispatcher_id, Transport.status == True)]
    if form.validate_on_submit():
        if form.start.data < datetime.date.today() or form.end.data < datetime.date.today() or form.start.data > form.end.data:
            return render_template('add_application.html', title='Оформить заявку', form=form,
                                   message='Некорректные даты')
        application = Applications(
            task=form.task.data,
            start=form.start.data,
            end=form.end.data,
            customer_id=current_user.id,
            transport_id=form.transport_id.data,
            dispatcher_id=current_user.dispatcher_id
        )
        current_user.applications.append(application)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/customer/applications')
    return render_template('add_application.html', title='Оформить заявку', form=form)


@app.route('/customer/edit_application/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_application(id):
    form = AddApplicationForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        application = db_sess.query(Applications).filter(Applications.id == id).first()
        if application:
            form.transport_id.data = application.transport_id
            form.task.data = application.task
            form.start.data = application.start
            form.end.data = application.end
        else:
            abort(404)
    if form.validate_on_submit():
        if application.reviewed:
            return render_template('add_application.html', title='Оформить заявку', form=form,
                                   message="Заявка уже рассмотрена")

        db_sess = db_session.create_session()
        application = db_sess.query(Applications).filter(Applications.id == id).first()
        if application:
            application.transport_id = form.transport_id.data
            application.task = form.task.data
            application.start = form.start.data
            application.end = form.end.data
            db_sess.commit()
            return redirect('/customer/applications')
        else:
            abort(404)
    return render_template('add_application.html', title='Оформить заявку', form=form, message="")


@app.route('/customer/delete_application/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_application(id):
    db_sess = db_session.create_session()
    application = db_sess.query(Applications).filter(Applications.id == id).first()
    if application:
        if application.accepted:
            db_sess.query(Transport).filter(Transport.id == application.transport_id).first().status = True
        db_sess.delete(application)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/customer/applications')


# Регистрация / Авторизация


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if form.type.data == 'dispatcher':
            user = db_sess.query(Dispatcher).filter(Dispatcher.email == form.email.data).first()
        else:
            user = db_sess.query(Customer).filter(Customer.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            session['login_type'] = form.type.data
            login_user(user)
            return redirect("/" + form.type.data)
        return render_template('login.html', title='Авторизация',
                               message="Неправильный логин или пароль",
                               form=form, css_file=url_for('static', filename='css/login.css'))
    return render_template('login.html', title='Авторизация', form=form, message='',
                           css_file=url_for('static', filename='css/login.css'))


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Dispatcher).filter(Dispatcher.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть",
                                   css_file=url_for('static', filename='css/login.css'))
        user = Dispatcher(
            name=form.name.data,
            company=form.company.data,
            tel=form.tel.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form,
                           css_file=url_for('static', filename='css/login.css'))


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()