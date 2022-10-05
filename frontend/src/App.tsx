import React, {Component, useEffect, useState} from 'react';
import logo from './logo.svg';
import './App.css';
import axios from "axios";

interface EmployeeProps {
    employee_id: number,
    name: string,
    age: number,
    position: string
    id?: number
}

interface EmployeePage {
    page: number,
    page_size: number,
    total: number,
    results: EmployeeProps[]
}

class Employee extends Component<EmployeeProps> {
    render() {
        const {employee_id, name, age, position} = this.props;
        return (
            <tr>
                <td>{employee_id}</td>
                <td>{name}</td>
                <td>{age}</td>
                <td>{position}</td>
            </tr>
        )
    }
}

function App() {
    const [employeeList, setEmployeeList] = useState<EmployeeProps[]>([]);

    useEffect(() => {
        axios.get<EmployeePage>('http://localhost:5000/api/employee')
            .then(response => {
                console.log(response)
                setEmployeeList(response.data.results)
            }).catch(error => {
                console.log(error)
        });
    }, []);

  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <div>
            <h2>Employee Listing</h2>
            <table>
                <thead>
                    <th>Id</th>
                    <th>Name</th>
                    <th>Age</th>
                    <th>Position</th>
                </thead>
                <tbody>
                {
                    employeeList.map(employee => <Employee {...employee} />)
                }
                </tbody>
            </table>
        </div>
      </header>
    </div>
  );
}

export default App;
