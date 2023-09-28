from flask import Flask, render_template, flash, redirect, url_for, abort, request
from werkzeug.security import generate_password_hash, check_password_hash
from databases import sqlalchemy_object, sqlalchemy_databases
from flask_bootstrap import Bootstrap
from flask_login import login_user, LoginManager, current_user, logout_user, UserMixin
from functools import wraps
from forms import RegisterForm, LoginForm, CreateForm
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "SSSHHHHHHHHH It's a secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///user.db"
app.config["SQLALCHEMY_BINDS"] = {"todos": "sqlite:///todos.db"}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = sqlalchemy_object(app)
databases = sqlalchemy_databases(app, UserMixin, db)
User = databases[0]
Todo = databases[1]

Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def restrict_register_login(function):
    @wraps(function)
    def inner_function(*args, **kwargs):
        if current_user.is_authenticated:
            return abort(403, description="Unauthorised, access denied until user has logged out of server.")
        else:
            return function(*args, **kwargs)

    return inner_function


def restrict_todo(function):
    @wraps(function)
    def inner_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(403, description="Unauthorised, access denied until user is logged in.")
        else:
            return function(*args, **kwargs)

    return inner_function


@app.route("/", methods=["GET", "POST"])
@restrict_register_login
def home():
    return render_template("home.html",
                           logged_in=current_user.is_authenticated)


def make_login_expire(function):
    @wraps(function)
    def inner_function(*args, **kwargs):
        user = User.query.filter_by(username=kwargs["username"]).first()
        try:
            date_time = ["year", "month", "day", "hour"]

            current_date_time = str(datetime.now()).replace("-", " ").replace(":", " ").split()[:-2]
            stored_date_and_time = user.log_in_date_time.replace("-", " ").replace(":", " ").split()[:-2]

            stored_hour = int(stored_date_and_time[-1]) + 1
            if stored_hour > 23:
                stored_hour = 0
            stored_date_and_time[-1] = str(stored_hour)

            dict_current_date_time = {date_time[num]: int(current_date_time[num]) for num in range(len(date_time))}
            dict_stored_date_and_time = {date_time[num]: int(stored_date_and_time[num]) for num in range(len(date_time))}

            no_abort = False
            for date_type in date_time:
                if dict_current_date_time[date_type] > dict_stored_date_and_time[date_type]:
                    logout_user()
                    return abort(403, description="Login timeout, login again to access this page.")
                else:
                    no_abort = True
            if no_abort:
                return function(*args, **kwargs)
        except AttributeError:
            return abort(404,
                         description="User doesn't exist.")

    return inner_function


@app.route("/register", methods=["GET", "POST"])
@restrict_register_login
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        emails = [data.email for data in db.session.query(User).all()]
        username = form.username.data
        email = form.email.data
        password = form.password.data

        if email in emails:
            flash("Account exists.")
        else:
            hashed_password = generate_password_hash(password)

            user = User(
                username=username,
                email=email,
                password=hashed_password,
                log_in_date_time=str(datetime.now())
            )
            db.session.add(user)
            db.session.commit()
            login_user(User.query.filter_by(password=hashed_password).first())

            return redirect(url_for("todo_lists", username=user.username))

    return render_template("register_login.html",
                           form=form,
                           header="Register")


@app.route("/login", methods=["GET", "POST"])
@restrict_register_login
def login():
    form = LoginForm()
    if form.validate_on_submit():
        emails = [data.email for data in db.session.query(User).all()]
        email = form.email.data
        if email in emails:
            user = User.query.filter_by(email=email).first()
            password = form.password.data
            hashed_password = user.password
            if check_password_hash(pwhash=hashed_password, password=password):
                login_user(user)
                user.log_in_date_time = str(datetime.now())
                db.session.commit()
                return redirect(url_for("todo_lists", username=user.username))
            else:
                flash("Invalid Password.")
        else:
            flash("Email doesn't exist.")

    return render_template("register_login.html",
                           form=form,
                           header="Login")


@app.route("/logout/<username>")
@make_login_expire
def logout(username):
    logout_user()
    user = User.query.filter_by(username=username).first()
    user.is_logged_in = True
    db.session.commit()
    return redirect(url_for("home"))


def todo_data(username):
    user_todos = [{"todo": data,
                   "name": data.name,
                   "date": data.date,
                   "tasks": data.tasks.split("*")
                   }
                  for data in db.session.query(Todo).all() if data.username == username]

    return user_todos


def delete_task_automatically(username):
    for data in todo_data(username):
        lst = []
        for sub_data in data["tasks"]:
            if sub_data == " " or len(sub_data) == 0:
                lst.append(None)

        if lst.count(None) == 10:
            todo = Todo.query.filter_by(id=data["todo"].id).first()
            db.session.delete(todo)
            db.session.commit()


@app.route("/todo_lists/<username>", methods=["GET", "POST"])
@restrict_todo
@make_login_expire
def todo_lists(username):
    user_todos = todo_data(username)
    if request.method == "POST":
        for num in range(len(user_todos)):
            for num2 in range(10):
                html_id = "lst" + str(num) + "-task" + str(num2)
                is_checked = request.form.get(html_id) is not None
                if is_checked:
                    lst_index = int(html_id[3])
                    task_index = int(html_id[-1])
                    selected_todo = user_todos[lst_index]
                    todo = Todo.query.filter_by(id=selected_todo["todo"].id).first()
                    all_tasks = todo.tasks.split("*")
                    all_tasks[task_index] = " "
                    new_all_tasks = "*".join(all_tasks)
                    todo.tasks = new_all_tasks
                    db.session.commit()

                    delete_task_automatically(username)
        return redirect(url_for("todo_lists", username=username))

    delete_task_automatically(username)
    return render_template("todo_lists.html",
                           todos_len=len(user_todos),
                           todos=user_todos,
                           username=username,
                           )


@app.route("/create_todo/<username>", methods=["GET", "POST"])
@restrict_todo
@make_login_expire
def create_todo(username):
    form = CreateForm()
    if form.validate_on_submit():
        user_date = [int(item) for item in str(form.date.data).split("-")]
        current_date = [int(item) for item in str(datetime.now().date()).split("-")]
        if user_date[1] < current_date[1]:
            flash("Invalid Date: month has already passed.")
        elif user_date[1] == current_date[1] and user_date[2] < current_date[2]:
            flash("Invalid Date: day has already passed.")
        else:
            tasks = [form.task1.data,
                     form.task2.data,
                     form.task3.data,
                     form.task4.data,
                     form.task5.data,
                     form.task6.data,
                     form.task7.data,
                     form.task8.data,
                     form.task9.data,
                     form.task10.data]
            new_tasks = "*".join(tasks)
            
            todo = Todo(username=username,
                        name=form.name.data,
                        date=form.date.data,
                        tasks=new_tasks)
            db.session.add(todo)
            db.session.commit()
            return redirect(url_for("todo_lists", username=username))

    return render_template("create_todo.html",
                           form=form,
                           header="Create List",
                           )


@app.route("/delete_task/<int:id>", methods=["GET", "POST"])
@restrict_todo
def delete_task(id):
    todo = Todo.query.filter_by(id=id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("todo_lists", username=todo.username))


if __name__ == "__main__":
    app.run(debug=True)
