from flask import Flask, send_from_directory
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from employee_resource import employee_resource
from graphql_queries import graphql_queries
from auth_resource import auth_resource

app = Flask(__name__, static_url_path='', static_folder='../frontend/build')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)


@app.before_request
def create_table():
    db.create_all()


@app.route("/", defaults={'path': ''})
def serve(path):
    return send_from_directory(app.static_folder, 'index.html')


app.register_blueprint(auth_resource, url_prefix='/api/auth')
app.register_blueprint(employee_resource, url_prefix='/api/employee')
app.register_blueprint(graphql_queries, url_prefix='/graphql')
app.run(host='localhost', port=5000)
