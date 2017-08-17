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
  render() {
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
            <td></td>
            <td></td>
            <td><img src="trash.svg" width="50px"/></td>
            <td><img src="scale.svg" width="80px"/></td>
            <td><img src="water.svg" width="50px"/></td>
            <td></td>
            <td></td>
          </tr>
          <tr>
            <th scope="row">B</th>
            <td><WellPlate /></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
          </tr>
          <tr>
            <th scope="row">A</th>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
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
