from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.exc import IntegrityError
from flask_api.models import EmployeeModel, db
from flask import Blueprint, abort, request, jsonify

employee_resource = Blueprint('employee_resource', __name__)

class EmployeeSchema(Schema):
    employee_id = fields.Integer(required=True)
    name = fields.String(required=True, validate=validate.Length(min=1))
    age = fields.Integer(required=True, validate=validate.Range(min=0))
    position = fields.String(required=True, validate=validate.Length(min=1))

class ListSchema(Schema):
    page_size = fields.Integer(validate=validate.OneOf([25, 50, 100]), missing=25)
    page_number = fields.Integer(missing=1)

@employee_resource.route('/', methods=['GET'])
def list_employees():
    try:
        data = ListSchema().load(request.args)
        pagination = EmployeeModel.query.paginate(data['page_number'], data['page_size'], False)
        items = [employee.to_json() for employee in pagination.items]
        return {
                'page': pagination.page,
                'page_size': pagination.per_page,
                'total': pagination.total,
                'results': items
               }, 200
    except ValidationError as e:
        return e.normalized_messages(), 400
    except Exception:
        return "Unable to get employees", 500

@employee_resource.route('/', methods=['POST'])
def create_new_employee():
    try:
        data = EmployeeSchema().load(request.json)
        employee = EmployeeModel(**data)
    except ValidationError as e:
        return e.normalized_messages(), 400

    try:
        db.session.add(employee)
        db.session.commit()
        return employee.to_json(), 200
    except IntegrityError:
        return f"employee_id {data['employee_id']} already in use", 400
    except Exception:
        return "Unable to save employee: {employee}", 500


@employee_resource.route('/<int:employee_id>', methods=['GET'])
def read_employee(employee_id):
    try:
        employee = EmployeeModel.query.get(employee_id)
        return employee.to_json()
    except AttributeError:
        return f"Employee {employee_id} does not exist", 400
    except Exception:
        return f"Unable to get employee", 500


@employee_resource.route('/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    try:
        employee = EmployeeModel.query.get(employee_id)
        db.session.delete(employee)
        db.session.commit()
        return f"Employee {employee_id} deleted", 200
    except AttributeError:
        return "Employee {employee_id} does not exist", 400
    except Exception:
        return f"Unable to delete employee: {employee_id}", 500


@employee_resource.route('/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    data_employee_id = None
    try:
        data = EmployeeSchema().load(request.json)
        data_employee_id = data['employee_id']
        employee = EmployeeModel.query.get(employee_id)
        employee.employee_id = data_employee_id
        employee.name = data['name']
        employee.age = data['age']
        employee.position = data['position']
        db.session.add(employee)
        db.session.commit()
        return employee.to_json(), 200
    except ValidationError as e:
        return e.normalized_messages(), 400
    except AttributeError:
        return f"Employee {employee_id} does not exist", 400
    except IntegrityError:
        return f"employee_id: {data_employee_id} is already in use"
    except Exception as e:
        return f"Unable to update employee: {employee_id}", 500


@employee_resource.route('/<int:employee_id>', methods=['PATCH'])
def patch_employee(employee_id):
    try:
        data = EmployeeSchema().load(request.json, partial=True)
        employee = EmployeeModel.query.get(employee_id)
        if 'employee_id' in data:
            employee.employee_id = data['employee_id']
        if 'name' in data:
            employee.name = data['name']
        if 'age' in data:
            employee.age = data['age']
        if 'position' in data:
            employee.position = data['position']
        db.session.add(employee)
        db.session.commit()
        return employee.to_json(), 200
    except ValidationError as e:
        return e.normalized_messages(), 400
    except AttributeError:
        abort(404, {"message": "Employee {employee_id} does not exist"})
    except Exception:
        abort(500, {"message": f"Unable to update employee: {employee_id}"})

