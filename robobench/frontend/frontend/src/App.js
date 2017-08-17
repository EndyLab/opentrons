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
        </thead>
        <tbody>
          <tr className="slot-grid">
            <th scope="row">C</th>
            <td>{grid['C1']}</td>
            <td>{grid['C2']}</td>
            <td>{grid['C3']}</td>
            <td>{grid['C4']}</td>
            <td>{grid['C5']}</td>
          </tr>
          <tr className="slot-grid">
            <th scope="row">B</th>
            <td>{grid['B1']}</td>
            <td>{grid['B2']}</td>
            <td>{grid['B3']}</td>
            <td>{grid['B4']}</td>
            <td>{grid['B5']}</td>
          </tr>
          <tr className="slot-grid">
            <th scope="row">A</th>
            <td>{grid['A1']}</td>
            <td>{grid['A2']}</td>
            <td>{grid['A3']}</td>
            <td>{grid['A4']}</td>
            <td>{grid['A5']}</td>
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
              <li>
                  <div className="input-group">
                  <input type="text" className="form-control" placeholder="Volume...">
                  <span className="input-group-btn">
                    <button className="btn btn-default" type="button">Set</button>
                  </span>
                  </div>
                </li>
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
