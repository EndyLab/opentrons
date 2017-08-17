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
      <div className="labware-well-96">
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
      <div id="grid-holder">
        <table id="grid">
          <tr>
            <th ></th>
            <th>1</th>
            <th>2</th>
            <th>3</th>
            <th>4</th>
            <th>5</th>
          </tr>
          <tr className="slot-grid">
            <th>C</th>
            <td></td>
            <td></td>
            <td><img src="trash.svg" width="50px"/></td>
            <td><img src="scale.svg" width="80px"/></td>
            <td><img src="water.svg" width="50px"/></td>
          </tr>
          <tr className="slot-grid">
            <th>B</th>
            <td><WellPlate /></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
          </tr>
          <tr className="slot-grid">
            <th>A</th>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
            <td></td>
          </tr>
        </table>
      </div>
    )
  }
}

class App extends Component {
  render() {
    return (
      <div>
        <nav className="navbar navbar-expand-md navbar-dark sticky-top bg-dark">
          <a className="navbar-brand" href="#">
            <i className="fa fa-cubes" aria-hidden="true"></i> Dashboard
          </a>
          <button className="navbar-toggler d-lg-none" type="button" data-toggle="collapse" data-target="#navbarsExampleDefault" aria-controls="navbarsExampleDefault" aria-expanded="false" aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>

          <div className="collapse navbar-collapse" id="navbarsExampleDefault">
            <ul className="navbar-nav mr-auto">
              <li className="nav-item active">
                <a className="nav-link" href="#">Home <span className="sr-only">(current)</span></a>
              </li>
              <li className="nav-item">
                <a className="nav-link" href="#">Settings</a>
              </li>
              <li className="nav-item">
                <a className="nav-link" href="#">Help</a>
              </li>
            </ul>

          </div>
        </nav>
      
        <div className="row fill">
          {/* right window */}
          <div className="col-sm-2" id="dashboard">
          <ul id="protocols">
            <li><button type="button" className="btn">Dilution</button></li>
            <li>
              <button type="button" className="btn">Transfer</button>
            </li>
            <li>
                <div className="input-group">
                <input type="text" className="form-control" placeholder="Volume..." />
                <span className="input-group-btn">
                  <button className="btn btn-default" type="button">Set</button>
                </span>
                </div>
              </li>
      
            <li><button type="button" className="btn btn-success"><i className="fa fa-play" aria-hidden="true"></i> Run </button></li>
          </ul>
        </div>


        {/* deck grid */}
          <div className="col-sm-10" id="grid">
            <Grid />
          </div>
        </div>
      </div>
    );
  }
}

export default App;
