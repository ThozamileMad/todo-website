from flask_sqlalchemy import SQLAlchemy


def sqlalchemy_object(app):
    return SQLAlchemy(app)


def sqlalchemy_databases(app, usermixin, db):
    with app.app_context():
        class User(usermixin, db.Model):
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.String, unique=False, nullable=False)
            email = db.Column(db.String, unique=True, nullable=False)
            password = db.Column(db.String, unique=False, nullable=False)
            log_in_date_time = db.Column(db.String, nullable=False)

        class Todo(db.Model):
            __bind_key__ = "todos"
            id = db.Column(db.Integer, primary_key=True)
            username = db.Column(db.Integer, nullable=False, unique=False)
            name = db.Column(db.String, nullable=True)
            date = db.Column(db.String, nullable=False)
            tasks = db.Column(db.String, nullable=False)
        db.create_all()

    return [User, Todo]
