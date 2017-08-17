import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

class Labware extends Component {

}

class Well extends Component {
  render() {
    return (<td className='well'><div className='circle'></div></td>)
  }
}

class WellPlate extends Labware {
  render() {
    const wells = [1,2,3,4,5,6,7,8].map((id) => <Well key={id} />);
    const rows = [1,2,3,4,5,6,7,8,9,10,11,12].map((id) => <tr key={id}>{wells}</tr>);

    return (
      <div className="labware well-96">
        <table>
          <tbody>
          {rows}
          </tbody>
        </table>
      </div>)
  }
}

class Grid extends Component {
  constructor(props) {
    super(props);

    this.state = {
      labware: {}
    }
  }

  componentDidMount() {
    this.timerID = setInterval(
      () => this.refresh(),
      1000
    )
  }

  refresh() {
    fetch('http://localhost:5000/grid')
      .then((response) => response.json())
      .then((json) => this.setState(json))
  }

  componentWillUnmount() {
    clearInterval(this.timerID);
  }

  render() {
    var grid = {
        'A1': '',
        'A2': '',
        'A3': '',
        'A4': '',
        'A5': '',
        'B1': '',
        'B2': '',
        'B3': '',
        'B4': '',
        'B5': '',
        'C1': '',
        'C2': '',
        'C3': '',
        'C4': '',
        'C5': '',
    }

    Object.keys(this.state.labware).forEach((key) => {
      if (this.state.labware[key] == 'WellPlate') grid[key] = <WellPlate />;
      else if (this.state.labware[key] == 'Trash') grid[key] = <img src="trash.svg" width="50px"/>;
    })

    return (
      <table id="grid">
        <thead>
          <tr>
            <th></th>
            <th>1</th>
            <th>2</th>
            <th>3</th>
            <th>4</th>
            <th>5</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <th scope="row">C</th>
            <td>{grid['C1']}</td>
            <td>{grid['C2']}</td>
            <td>{grid['C3']}</td>
            <td>{grid['C4']}</td>
            <td>{grid['C5']}</td>
          </tr>
          <tr>
            <th scope="row">B</th>
            <td>{grid['B1']}</td>
            <td>{grid['B2']}</td>
            <td>{grid['B3']}</td>
            <td>{grid['B4']}</td>
            <td>{grid['B5']}</td>
          </tr>
          <tr>
            <th scope="row">A</th>
            <td>{grid['A1']}</td>
            <td>{grid['A2']}</td>
            <td>{grid['A3']}</td>
            <td>{grid['A4']}</td>
            <td>{grid['A5']}</td>
          </tr>
        </tbody>
      </table>
    )
  }
}

class App extends Component {
  render() {
    return (
      <div className="row fill">
        <div className="col-sm-2" id="protocol">
          <button type="button" className="btn">Dilution</button>
          <button type="button" className="btn">Transfer</button>
        </div>
        <div className="col-sm-8" id="grid">
        <Grid />
        </div>
        <div className="col-sm-2" id="feedback">
          <button type="button" className="btn btn-success">Run</button>
        </div>
      </div>
    );
  }
}

export default App;
