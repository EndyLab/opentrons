import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import TableDragSelect from 'react-table-drag-select';
// import update from 'immutability-helper';
// import 'react-table-drag-select/style.css';


const SERVER = "http://10.34.178.45:5000"
// const SERVER = "http://localhost:5000"


class Labware extends Component {

}

class TipRack extends Labware {
  render() {
    const wells = ["A","B","C","D","E","F","G","H"].map((id) => <td key={id} className='tip'><div className='circle'></div></td>);
    const rows = [12,11,10,9,8,7,6,5,4,3,2,1].map((id) => <tr key={id}>{wells}</tr>);

    return (
      <div className="labware-tiprack-96">
        <table>
            {rows}
        </table>
      </div>
    )
  }
}

class WellPlate extends Labware {
  constructor(props) {
    super(props);

    this.state = {
      model: new TableDragSelect.Model(12, 8) // Specify rows and columns
    };
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
}

class Grid extends Component {
  constructor(props) {
    super(props);

    this.state = {
      labware: {},
      models: {},
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

  // This keeps track of which wells are selected on all the plates
  // So model looks like:
  // this.state.models { 'A1': <model> }
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
      // console.log(key + ": " + this.state.labware[key]);

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
      else if (this.state.labware[key] == 'Scale') grid[key] = <img src="scale.svg" width="80px"/>;
      else if (this.state.labware[key] == 'TipRack') grid[key] = <TipRack />;
      else if (this.state.labware[key] == 'Water') grid[key] = <img src="water.svg" width="50px"/>;
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
              <th scope="row">3</th>
              <td>{grid['A3']}</td>
              <td>{grid['B3']}</td>
              <td>{grid['C3']}</td>
              <td>{grid['D3']}</td>
              <td>{grid['E3']}</td>
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
              <th scope="row">1</th>
              <td>{grid['A1']}</td>
              <td>{grid['B1']}</td>
              <td>{grid['C1']}</td>
              <td>{grid['D1']}</td>
              <td>{grid['E1']}</td>
            </tr>
          </tbody>
        </table>
    )
  }
}

class ProtocolList extends Component {
  constructor(props) {
    super(props);

    this.state = {
      lambdas: {'hi':'test'}
      // lambdas: this.props.protocols,
    }
  }

  render() {
      Object.keys(this.state.lambdas).forEach((key) => {
      console.log("protocol list")
      console.log(key + ": " + this.state.lambdas[key]);
      var protocolList = this.props.protocols
      console.log(protocolList)
      console.log("rip me")
    })

    var list_items = [];
    for (var i = 0; i < this.props.protocols.length; i++) {
      var curr_protocol = this.props.protocols[i]
      console.log("name:")
      console.log(curr_protocol)
      list_items.push(<li key={i}>{curr_protocol['protocol']}</li>);
    }
    return (
       <div>
       <ol>
        {list_items}
        </ol>
       </div>
    );

    // return (
    //   <div>{this.state.lambdas['hi']}</div>
    // );
  }
}

var AdaptiveButton = React.createClass({
  render() {
    return (
      <div>{this.props.message}</div>
    );
  }
});


class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      parameters: {},
      show_lambdas: false,
      lambdas: {}
    }

    this.handleChange = this.handleChange.bind(this);
    this.selectProtocol = this.selectProtocol.bind(this);
    this.runRobot = this.runRobot.bind(this);
    this.resetGrid = this.resetGrid.bind(this);
    this.recordStart = this.recordStart.bind(this);
    this.recordStop = this.recordStop.bind(this);
    this.recordRun = this.recordRun.bind(this);
    this.recordShow = this.recordShow.bind(this);
  }

  runRobot() {
    if (!this.grid.state.source || !this.grid.state.dest) {
      alert("Please select source or destination wells.");
      return;
    }

    var source = this.grid.state.models[this.grid.state.source].getCellsSelected();
    var dest = this.grid.state.models[this.grid.state.dest].getCellsSelected();

    var sourceWells = [];
    var destWells = [];

    ["A","B","C","D","E","F","G","H"].forEach((col, c) => {
      [12,11,10,9,8,7,6,5,4,3,2,1].forEach((row, r) => {
        if (source[r][c]) sourceWells.push(col + row);
        if (dest[r][c]) destWells.push(col + row);
      })
    })

    this.setState({ running: true })

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
        }, 
        tiprack: {
          labware: 'TipRack',
          slot: this.grid.state.tiprack,
        }
      })
    })
      .then((response) => { return response.json() })
      .then((json) => {
        console.log(json);
        this.setState({ running: false });
        this.resetGrid();

        if (json.status == "ok") {
        } else {
          alert("Error running robot: " + json.status);
        }
      });
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
    this.setState({ protocol: event.target.id })
  }

  resetGrid() {
    var newModels = {}
    Object.keys(this.grid.state.models).forEach((key) => {
      newModels[key] = this.grid.state.models[key].clone()
      newModels[key] = this.grid.state.models[key].clear()
    })

    this.setState({ models: newModels });
    this.setState({ source: null });
    this.setState({ dest: null });
    this.setState({ protocol: null });
    this.setState({ record: false });
  }

  recordShow() {
    this.setState({ show_lambdas: true });

    // response from backend
    fetch(SERVER + '/record/show')
      .then((response) => response.json())
      .then((json) => this.setState(json))
    console.log("showing stored protocols")
    console.log(this.state.lambdas)

  }

  // recording user protocol command stack
  recordStart() {
    this.setState({ record: true });
    fetch(SERVER + '/record', {
      method: 'post',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        record: true
      })
    })
  }

  recordStop() {
    this.setState({ record: false });
    fetch(SERVER + '/record', {
      method: 'post',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        record: false
      })
    })
  }

  recordRun() {
    this.setState({ running: true })
    fetch(SERVER + '/record/run', {
      method: 'post',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        running_record: true
      })
    })

   .then((response) => { return response.json() })
    .then((json) => {
      console.log(json);
      this.setState({ running: false });
      this.resetGrid();

      if (json.status == "ok") {
      } else {
        alert("Error running protcol list: " + json.status);
      }
    });
  }

  render() {
    // console.log(this.state)

    // shows busy icon
    var running = "d-none";
    if (this.state.running) running = "";

    return (
        <div className="row fill">
          {/* right window */}
          <div className="col-sm-2" id="dashboard">

            <ul id="protocols">
              {/* dilution */}
              <li className={this.state.protocol == "dilution" ? "active-protocol" : ""}>
                <button type="button" id="dilution" className="btn" onClick={this.selectProtocol}>Dilution</button>
                <div className="protocol-parameters">
                  <div className="form-group row">
                    <label className="col-sm-2 col-form-label ratio-label">1:</label>
                    <div className="col-sm-10"><input type="text" id="ratio" className="form-control" placeholder="Ratio" onChange={this.handleChange} value={this.state.parameters['ratio']} /></div>
                    </div>
                </div>
              </li>

              {/* trasnfer */}
              <li className={this.state.protocol == "transfer" ? "active-protocol" : ""}>
                <button type="button" id="transfer" className="btn" onClick={this.selectProtocol}>Transfer</button>
                <div className="protocol-parameters">
                  <div className="input-group">
                    <input type="text" id="volume" className="form-control" placeholder="Volume..." onChange={this.handleChange} value={this.state.parameters['volume']} />
                  </div>
                </div>
              </li>

              <li><button type="button" className="btn btn-info" onClick={this.runRobot}><i className="fa fa-play" aria-hidden="true"></i> Run</button></li>
              <li><button type="button" className="btn btn-info" onClick={this.resetGrid}><i className="fa fa-refresh" aria-hidden="true"></i> Reset</button></li>
              <li><button type="button" className="btn btn-info" onClick={this.recordStart}><i className="fa fa-video-camera" aria-hidden="true"></i> Record</button></li>
              <li><button type="button" className="btn btn-info" onClick={this.recordStop}><i className="fa fa-stop" aria-hidden="true"></i> Stop</button></li>
              <li><button type="button" className="btn btn-info" onClick={this.recordRun}><i className="fa fa-play" aria-hidden="true"></i> Run Lambdas</button></li>
              <li><button type="button" className="btn btn-info" id={this.state.show_lambdas == true ? "show-btn" : "hide-btn"} onClick={this.recordShow}><i className="fa fa-eye" aria-hidden="true"></i> Show Lambdas</button></li>
              
              <li className={this.state.show_lambdas == true ? "active-protocol" : "d-none"}>
                <ProtocolList protocols={this.state.lambdas}/>
              </li>

              <div className={running}>
                <img src="loading.gif" />
              </div>
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
