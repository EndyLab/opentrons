import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import TableDragSelect from 'react-table-drag-select';
// import update from 'immutability-helper';
// import 'react-table-drag-select/style.css';

const SERVER = "http://localhost:5000"

class Labware extends Component {

}

class WellPlate extends Labware {
  constructor(props) {
    super(props);

    this.state = {
      model: new TableDragSelect.Model(12, 8) // Specify rows and columns
    };

    this.handleModelChange = this.handleModelChange.bind(this);
  }

  render() {
    const wells = ["A","B","C","D","E","F","G","H"].map((id) => <td key={id} className='well'><div className='circle'></div></td>);
    const rows = [12,11,10,9,8,7,6,5,4,3,2,1].map((id) => <tr key={id}>{wells}</tr>);

    return (
      <div className="labware-well-96">
        <TableDragSelect className={this.props.mode} model={this.props.model} onModelChange={this.props.updateModel}>
            {rows}
        </TableDragSelect>
      </div>
    )
  }

  handleModelChange(model) {
    this.props.updateModel(model);
  }
}

class Grid extends Component {
  constructor(props) {
    super(props);

    this.state = {
      labware: {},
      models: {}
    }
  }

  componentDidMount() {
    this.timerID = setInterval(
      () => this.refresh(),
      1000
    )
  }

  refresh() {
    fetch(SERVER + '/grid')
      .then((response) => response.json())
      .then((json) => this.setState(json))
  }

  componentWillUnmount() {
    clearInterval(this.timerID);
  }

  updateModel(key, model) {
    console.log(model)

    this.state.models[key] = model
    this.setState({ models: this.state.models })

    if (!this.state.source) {
      this.setState({ source: key });
    } else if (!this.state.dest && this.state.source != key) {
      this.setState({ dest: key });
    }
  }

  render() {
    var grid = {
        'A1': '',
        'A2': '',
        'A3': '',
        'B1': '',
        'B2': '',
        'B3': '',
        'C1': '',
        'C2': '',
        'C3': '',
        'D1': '',
        'D2': '',
        'D3': '',
        'E1': '',
        'E2': '',
        'E3': '',
    }

    Object.keys(this.state.labware).forEach((key) => {
      if (this.state.labware[key] == 'WellPlate') {
        var mode = 'none'
        if (this.state.source == key) mode = 'source'
        else if (this.state.dest == key) mode = 'dest'

        var model;
        if (key in this.state.models) model = this.state.models[key];
        else model = new TableDragSelect.Model(12, 8);

        grid[key] = <WellPlate key={key} mode={mode} model={model} updateModel={(model) => this.updateModel(key, model)}/>;
      }
      else if (this.state.labware[key] == 'Trash') grid[key] = <img src="trash.svg" width="50px"/>;
    })

    return (
        <table id="grid">
          <thead>
            <tr>
              <th></th>
              <th>A</th>
              <th>B</th>
              <th>C</th>
              <th>D</th>
              <th>E</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <th scope="row">1</th>
              <td>{grid['A1']}</td>
              <td>{grid['B1']}</td>
              <td>{grid['C1']}</td>
              <td>{grid['D1']}</td>
              <td>{grid['E1']}</td>
            </tr>
            <tr>
              <th scope="row">2</th>
              <td>{grid['A2']}</td>
              <td>{grid['B2']}</td>
              <td>{grid['C2']}</td>
              <td>{grid['D2']}</td>
              <td>{grid['E2']}</td>
            </tr>
            <tr>
              <th scope="row">3</th>
              <td>{grid['A3']}</td>
              <td>{grid['B3']}</td>
              <td>{grid['C3']}</td>
              <td>{grid['D3']}</td>
              <td>{grid['E3']}</td>
            </tr>
          </tbody>
        </table>
    )
  }
}

class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      parameters: {}
    }

    this.handleChange = this.handleChange.bind(this);
    this.selectProtocol = this.selectProtocol.bind(this);
    this.runRobot = this.runRobot.bind(this);
  }

  runRobot() {
    var source = this.grid.state.models[this.grid.state.source]._cellsSelected;
    var dest = this.grid.state.models[this.grid.state.dest]._cellsSelected;

    var sourceWells = [];
    var destWells = [];

    ["A","B","C","D","E","F","G","H"].forEach((col, c) => {
      [12,11,10,9,8,7,6,5,4,3,2,1].forEach((row, r) => {
        if (source[r][c]) sourceWells.push(col + row);
        if (dest[r][c]) destWells.push(col + row);
      })
    })

    fetch(SERVER + '/run', {
      method: 'post',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        protocol: 'transfer',
        parameters: this.state.parameters,
        source: {
          labware: 'WellPlate',
          slot: this.grid.state.source,
          wells: sourceWells
        },
        dest: {
          labware: 'WellPlate',
          slot: this.grid.state.dest,
          wells: destWells
        }
      })
    })
  }

  componentDidMount() {
    console.log('ok');
  }

  handleChange(event) {
    this.state.parameters[event.target.id] = event.target.value;
    console.log(this.state.parameters);
    this.setState({ parameters: this.state.parameters });
  }

  selectProtocol(event) {

  }

  render() {
    console.log(this.state)

    return (
        <div className="row fill">
          {/* right window */}
          <div className="col-sm-2" id="dashboard">

          <ul id="protocols">
            <li><button type="button" id="dilution" className="btn" onClick={this.selectProtocol}>Dilution</button></li>
            <li>
              <button type="button" id="transfer" className="btn" onClick={this.selectProtocol}>Transfer</button>
              <div className="protocol-parameters">
                <div className="input-group">
                  <input type="text" id="volume" className="form-control" placeholder="Volume..." onChange={this.handleChange} value={this.state.parameters['volume']} />
                </div>
              </div>
              </li>

              <li><button type="button" className="btn btn-success" onClick={this.runRobot}><i className="fa fa-play" aria-hidden="true"></i>Run</button></li>
          </ul>
        </div>


        {/* deck grid */}
          <div className="col-sm-10 fill">
            <Grid ref={(grid) => { this.grid = grid }} />
          </div>
        </div>
    );
  }
}

export default App;
