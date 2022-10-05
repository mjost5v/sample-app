from flask_restful import Resource, abort, reqparse
from sqlalchemy.exc import IntegrityError
from flask_api.models import EmployeeModel, db

parser = reqparse.RequestParser(bundle_errors=True)
parser.add_argument('employee_id', type=int, help='Employee id: {error_msg}', required=True)
parser.add_argument('name', type=str, help='Employee name: {error_msg}}', required=True)
parser.add_argument('age', type=int, help='Employee age: {error_msg}', required=True)
parser.add_argument('position', type=str, help='position: {error_msg}', required=True)

list_parser = reqparse.RequestParser()
list_parser.add_argument('page_size', type=int,  choices=(25, 50, 100), help='page_size: {error_msg}', location='args')
list_parser.add_argument('page_number', type=int, help='page_number: {error_msg}', location='args')

patch_parser = reqparse.RequestParser(bundle_errors=True)
patch_parser.add_argument('employee_id', type=int, help='Employee id: {error_msg}', required=False)
patch_parser.add_argument('name', type=str, help='Employee name: {error_msg}}', required=False)
patch_parser.add_argument('age', type=int, help='Employee age: {error_msg}', required=False)
patch_parser.add_argument('position', type=str, help='position: {error_msg}', required=False)


class EmployeeResourceList(Resource):
    def get(self):
        args = list_parser.parse_args()
        if args['page_number'] is None or args['page_number'] < 1:
            page_number = 1
        else:
            page_number = args['page_number']
        page_size = 25 if args['page_size'] is None else args['page_size']
        try:
            pagination = EmployeeModel.query.paginate(page_number, page_size, False)
            items = [employee.to_json() for employee in pagination.items]
            return {
                    'page': pagination.page,
                    'page_size': pagination.per_page,
                    'total': pagination.total,
                    'results': items
                   }, 200
        except Exception:
            abort(500, message="Unable to get employees")

    def post(self):
        args = parser.parse_args()
        employee = EmployeeModel(**args)
        try:
            db.session.add(employee)
            db.session.commit()
            return employee.to_json(), 200
        except IntegrityError:
            abort(400, message=f"employee_id {args['employee_id']} already in use")
        except Exception:
            abort(500, messsage=f"Unable to save employee: {employee}")


class EmployeeResource(Resource):
    def get(self, employee_id):
        try:
            employee = EmployeeModel.query.get(employee_id)
            return employee.to_json()
        except AttributeError:
            abort(404, message=f"Employee {employee_id} does not exist")
        except Exception:
            abort(500, message=f"Unable to get employee")

    def delete(self, employee_id):
        try:
            employee = EmployeeModel.query.get(employee_id)
            db.session.delete(employee)
            db.session.commit()
            return f"Employee {employee_id} deleted", 200
        except AttributeError:
            abort(404, message=f"Employee {employee_id} does not exist")
        except Exception:
            abort(500, message=f"Unable to delete employe: {employee_id}")

    def put(self, employee_id):
        args = parser.parse_args()
        try:
            employee = EmployeeModel.query.get(employee_id)

            employee.employee_id = args['employee_id']
            employee.name = args['name']
            employee.age = args['age']
            employee.position = args['position']
            db.session.add(employee)
            db.session.commit()
            return employee.to_json(), 200
        except AttributeError:
            abort(404, message=f"Employee {employee_id} does not exist")
        except Exception:
            abort(500, message=f"Unable to update employee: {employee_id}")

    def patch(self, employee_id):
        args = parser.parse_args()
        try:
            employee = EmployeeModel.query.get(employee_id)
            if 'employee_id' in args:
                employee.employee_id = args['employee_id']
            if 'name' in args:
                employee.name = args['name']
            if 'age' in args:
                employee.age = args['age']
            if 'position' in args:
                employee.position = args['position']
            db.session.add(employee)
            db.session.commit()
            return employee.to_json(), 200
        except AttributeError:
            abort(404, message=f"Employee {employee_id} does not exist")
        except Exception:
            abort(500, message=f"Unable to update employee: {employee_id}")

