from flask import Flask, send_from_directory, request, jsonify
from flask_restful import Api
from flask_api.employee_resource import EmployeeResource, EmployeeResourceList
from flask_api.models import db
from graphql_queries import get_employee, list_employees, update_employee, delete_employee, create_employee
from ariadne import make_executable_schema, ObjectType, load_schema_from_path, snake_case_fallback_resolvers, \
    graphql_sync
from ariadne.constants import PLAYGROUND_HTML

app = Flask(__name__, static_url_path='', static_folder='../frontend/build')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
api = Api(app)


@app.before_request
def create_table():
    db.create_all()


query = ObjectType('Query')
query.set_field('employees', list_employees)
query.set_field('employee', get_employee)

mutation = ObjectType('Mutation')
mutation.set_field('createEmployee', create_employee)
mutation.set_field('updateEmployee', update_employee)
mutation.set_field('deleteEmployee', delete_employee)

type_defs = load_schema_from_path('schema.graphql')
schema = make_executable_schema(type_defs, query, mutation, snake_case_fallback_resolvers)

@app.route("/", defaults={'path': ''})
def serve(path):
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/graphql', methods=['GET'])
def playground():
    return PLAYGROUND_HTML, 200


@app.route('/graphql', methods=['POST'])
def server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request, debug=app.debug)
    status_code = 200 if success else 400
    return jsonify(result), status_code


api.add_resource(EmployeeResourceList, '/api/employee')
api.add_resource(EmployeeResource, '/api/employee/<int:employee_id>')

app.run(host='localhost', port=5000)
