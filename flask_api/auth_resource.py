from flask import Blueprint, request
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import generate_password_hash, check_password_hash

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth(scheme='Bearer')

tokens = {
    'secret-token-1': 'username',
    'secret-token-2': 'admin'
}

users = {
    "username": generate_password_hash("password"),
    "admin": generate_password_hash("admin")
}

roles = {
    "username": ["user"],
    "admin": ["admin", "user"]
}

auth_resource = Blueprint('auth', __name__)

@auth_resource.route('/basic')
@basic_auth.login_required
def protected_by_http_basic():
    return f"Hello {basic_auth.current_user()}! You have {get_user_roles(basic_auth.current_user())} assigned!"

@auth_resource.route("/basic/admin")
@basic_auth.login_required(role='admin')
def basic_admin():
    return f"Hello {basic_auth.current_user()}! You're an admin!"

@basic_auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username
    return None

@basic_auth.get_user_roles
def get_user_roles(user):
    return roles.get(user, [])

@auth_resource.route("/token")
@token_auth.login_required()
def token_access():
    return f"Hello {token_auth.current_user()}!"

@token_auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]
    return None
