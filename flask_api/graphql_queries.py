from models import EmployeeModel, db
from ariadne import graphql_sync, convert_kwargs_to_snake_case, ObjectType, load_schema_from_path, make_executable_schema, snake_case_fallback_resolvers
from ariadne.constants import PLAYGROUND_HTML
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, request, jsonify

graphql_queries = Blueprint('graphql', __name__)



def list_employees(obj, info):
    try:
        employees = [employee.to_json() for employee in EmployeeModel.query.all()]
        payload = {
            'success': True,
            'employees': employees
        }
    except Exception as error:
        payload = {
            'success': False,
            'errors': [str(error)]
        }
    return payload


@convert_kwargs_to_snake_case
def get_employee(obj, info, id):
    try:
        employee = EmployeeModel.query.get(id)
        return {
            'success': True,
            'employee': employee.to_json()
        }
    except AttributeError:
        return {
            'success': False,
            'errors': ["Employee with {employee_id} does not exist"]
        }
    except Exception as e:
        return {
            'success': False,
            'errors': [str(e)]
        }


@convert_kwargs_to_snake_case
def create_employee(obj, info, employee_id, name, age, position):
    employee = EmployeeModel(employee_id, name, age, position)
    try:
        db.session.add(employee)
        db.session.commit()
        return {
            'success': True,
            'employee': employee
        }
    except IntegrityError:
        return {
            'success': False,
            'errors': [f'employee_id: {employee_id} already in use']
        }
    except Exception as e:
        return {
            'success': False,
            'errors': [str(e)]
        }


@convert_kwargs_to_snake_case
def update_employee(obj, info, id, employee_id=None, name=None, age=None, position=None):
    try:
        employee = EmployeeModel.query.get(id)
        if employee_id:
            employee.employee_id = employee_id
        if name:
            employee.name = name
        if age:
            employee.age = age
        if position:
            employee.position = position
        db.session.add(employee)
        db.session.commit()

        return {
            'success': True,
            'employee': employee.to_json()
        }
    except AttributeError:
        return {
            'success': False,
            'errors': ["Employee with {employee_id} does not exist"]
        }
    except Exception as e:
        return {
            'success': False,
            'errors': [str(e)]
        }


@convert_kwargs_to_snake_case
def delete_employee(obj, info, id):
    try:
        employee = EmployeeModel.query.get(id)
        db.session.delete(employee)
        db.session.commit()
        return {
            'success': True
        }
    except AttributeError:
        return {
            'success': False,
            'errors': [f'employee {id} does not exist']
        }
    except Exception as e:
       return {
           'success': False,
           'errors': [str(e)]
       }

query = ObjectType('Query')
query.set_field('employees', list_employees)
query.set_field('employee', get_employee)

mutation = ObjectType('Mutation')
mutation.set_field('createEmployee', create_employee)
mutation.set_field('updateEmployee', update_employee)
mutation.set_field('deleteEmployee', delete_employee)

type_defs = load_schema_from_path('schema.graphql')
schema = make_executable_schema(type_defs, query, mutation, snake_case_fallback_resolvers)

@graphql_queries.route('/', methods=['GET'])
def playground():
    return PLAYGROUND_HTML, 200


@graphql_queries.route('/', methods=['POST'])
def server():
    data = request.get_json()
    success, result = graphql_sync(schema, data, context_value=request)
    status_code = 200 if success else 400
    return jsonify(result), status_code
