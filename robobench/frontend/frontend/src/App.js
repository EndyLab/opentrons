import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import TableDragSelect from 'react-table-drag-select';
// import update from 'immutability-helper';
// import 'react-table-drag-select/style.css';


// const SERVER = "http://10.34.183.189:5000"
const SERVER = "http://localhost:5000"


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

// list of protocols
// currently veyr :JANKY: but #itworks

//  protocol parameters, shown on click, hidden otherwisde
class ProtocolCard extends Component {
  constructor(props) {
    super(props);

  }

  render() {
    var keys = Object.keys(this.props.protocol_data)

    // dont display protocol field since the lit heading is already the protocol
    var index = keys.indexOf('protocol');
    if (index > -1) {
      keys.splice(index, 1);
    }
    var index = keys.indexOf('tiprack');
    if (index > -1) {
      keys.splice(index, 1);
    }

    var paramsList = keys.map((key, id) => <li className={key} key={id}><b>{key}:</b> {JSON.stringify(this.props.protocol_data[key])}</li>);
    
    console.log("keys of protocol data")
    console.log(keys)
    console.log(this.props.protocol_data[keys[0]])
    console.log(JSON.stringify(this.props.protocol_data[keys[1]]))

    return (
      <ul className="protocol-card">
        {paramsList}
      </ul>
    );
  }
}

// a protocol list item
//  <ProtocolCard protocol_data={this.props.protocol_data}/>
class ProtocolItem extends Component {
  constructor(props) {
    super(props);

    this.state = {
      hover_flag: false,
    }
    this.hoverEvent = this.hoverEvent.bind(this);
  }

  hoverEvent() {
    this.setState({hover_flag: !this.state.hover_flag})
  }

  render() {
   var protocol_list_style = {
          // 'background-color': '#eeeeee'
          'background': '#90A4AE'
          // 'background' : '#78909C'
      };
      if (this.props.isSelected || this.state.hover_flag) {
          protocol_list_style['background'] = '#546E7A';
      }
    return (
      <li  className={this.props.isSelected == true ? "protocol-card-active" : ""}>
        <div 
          className="protocol-card-title"
          style={protocol_list_style}
          id={this.props.id_string} 
          onClick={this.props.clickMethod} 
          onMouseEnter={this.hoverEvent} 
          onMouseLeave={this.hoverEvent} 
        >
          {this.props.protocol_name} 
          <button type="button" className="delete-protocol" onClick={this.props.deleteMethod}><i className="fa fa-times-circle" aria-hidden="true"></i></button>
        </div>
        <ProtocolCard protocol_data={this.props.protocol_data} isSelected={this.props.isSelected}/>
      </li>
    );
  }
}

class ProtocolList extends Component {
  constructor(props) {
    super(props);

    this.state = {
      hover_flag: false,
      delete_item: -1,
    }

    this.hoverEvent = this.hoverEvent.bind(this);
    this.handleClick = this.handleClick.bind(this);
    this.deleteProtocol = this.deleteProtocol.bind(this);
  }

  deleteProtocol(event) {
    // find the list item that contained the delete button that got hit
    console.log("delete button hit", event.target.parentNode.parentNode.id)
    var base = 'protocol-item-'
    var str = event.target.parentNode.parentNode.id
    var index = parseInt(str.substr(str.length - (str.length - base.length)))
    console.log("index: ", index)
    this.setState({delete_item: index})
  }

  hoverEvent() {
    this.setState({hover_flag: !this.state.hover_flag})
  }

  handleClick(event) {
    this.setState({selectedItem: event.target.id});
    console.log('list item clicked')
    console.log(event.target)
  }

  render() {
    // delete list items as needed
    // TODO: fix so that the parent this.props.protocols is changed not the child's version
    var index = this.state.delete_item
    if (index > -1) {
      this.props.protocols.splice(index, 1);
      this.setState({delete_item: -1})
    }
    var list_items = [];
    for (var i = 0; i < this.props.protocols.length; i++) {
      var base = 'protocol-item-'
      var id_string = base.concat(i.toString())

      var curr_protocol = this.props.protocols[i]
      var is_selected = this.state.selectedItem === id_string
      console.log(this.state)
      console.log("IS SELECTED PROP")
      console.log(i)
      console.log(is_selected)
      
      list_items.push(<ProtocolItem 
                        key={i} 
                        id_string={id_string}
                        protocol_data={curr_protocol}
                        protocol_name={curr_protocol['protocol']} 
                        isSelected={is_selected}
                        clickMethod={this.handleClick}
                        deleteMethod={this.deleteProtocol}
                      />);
    }
    
    return (
        <ol id="protocol-list">
          {list_items}
        </ol>
    );
  }
}


class App extends Component {
  constructor(props) {
    super(props)
    this.state = {
      parameters: {},
      show_lambdas: false,
      lambdas: {},
      record: false,
      curr_user_data: {},
    }

    this.handleChange = this.handleChange.bind(this);
    this.selectProtocol = this.selectProtocol.bind(this);
    this.runRobot = this.runRobot.bind(this);
    this.resetGrid = this.resetGrid.bind(this);
    this.recordStart = this.recordStart.bind(this);
    this.recordStop = this.recordStop.bind(this);
    this.recordRun = this.recordRun.bind(this);
    this.recordShow = this.recordShow.bind(this);
    this.recordHide = this.recordHide.bind(this);
    this.recordClear = this.recordClear.bind(this);
    this.recordSave = this.recordSave.bind(this);
    this.getData = this.getData.bind(this);
  }

  // gets user data from web app
  getData() {
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

    var user_data = {
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
      };

    return user_data;
  }
  runRobot() {
    var user_data = this.getData()
    this.setState(
      { running: true },
    )
    // the run button basically calls the save button 
    this.setState({ curr_user_data: user_data }, () => {
      if (this.state.record) {
        this.recordSave();
      }
    }); 

    fetch(SERVER + '/run', {
      method: 'post',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(user_data)
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
    console.log("this is protocol button PRESSED")
    console.log(event)
    console.log(event.target.id)
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
  }

  //  clears the protocol list
  recordClear() {
    // tell backend to clear protocol list
    fetch(SERVER + '/record/clear')
      .then((response) => response.json())
      .then((json) => this.setState(json))
    console.log("clear button hit")
    console.log(this.state.lambdas)
  }


  // TODO: the difference between save and run is that save does NOT require record button to be hit first
  recordSave() {
    // tell backend to do stuff
    var data = this.getData()
     fetch(SERVER + '/record/save', {
      method: 'post',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })
      .then((response) => response.json())
      .then((json) => this.setState(json))
    console.log("saved button hit")
    console.log(this.state.lambdas)
  }

  // shows/hides the protocol list
  recordShow() {
    this.setState({ show_lambdas: true });

    // response from backend
    fetch(SERVER + '/record/show')
      .then((response) => response.json())
      .then((json) => this.setState(json))
    console.log("show button hit")
    console.log(this.state.lambdas)
  }

  recordHide() {
     this.setState({ show_lambdas: false });
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
    console.log("record start button hit")
  }

  // stops recording
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
    console.log("record stop button hit")
  }

  // runs every protocol in the list
  recordRun() {
    this.setState({ running: true })
    fetch(SERVER + '/record/run')
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

              {/* transfer */}
              <li className={this.state.protocol == "transfer" ? "active-protocol" : ""}>
                <button type="button" id="transfer" className="btn" onClick={this.selectProtocol}>Transfer</button>
                <div className="protocol-parameters">
                  <div className="input-group">
                    <input type="text" id="volume" className="form-control" placeholder="Volume..." onChange={this.handleChange} value={this.state.parameters['volume']} />
                  </div>
                </div>
              </li>

              <li><button type="button" className="btn btn-success" onClick={this.runRobot}><i className="fa fa-play" aria-hidden="true"></i> Run</button></li>
              <li><button type="button" className="btn btn-success" onClick={this.resetGrid}><i className="fa fa-refresh" aria-hidden="true"></i> Reset</button></li>
              <li><button type="button" className="btn btn-info" onClick={this.state.record == true ? this.recordStop: this.recordStart}><i className={this.state.record == true ? "fa fa-stop" : "fa fa-video-camera"} aria-hidden="true"></i> {this.state.record == true ? "Stop Recording" : "Record"}</button></li>
              <li><button type="button" className="btn btn-info" onClick={this.recordSave}><i className="fa fa-floppy-o" aria-hidden="true"></i> Save to List</button></li>
              <li><button type="button" className="btn btn-info" onClick={this.recordRun}><i className="fa fa-play" aria-hidden="true"></i> Run List</button></li>
              <li><button type="button" className="btn btn-info" onClick={this.recordClear}><i className="fa fa-trash" aria-hidden="true"></i> Clear List</button></li>
              <li><button type="button" className="btn btn-info" onClick={this.state.show_lambdas == true ? this.recordHide: this.recordShow}><i className={this.state.show_lambdas == true? "fa fa-eye-slash":"fa fa-eye"} aria-hidden="true"></i> {this.state.show_lambdas == true ? "Hide List" : "Show List"} </button></li>
              
              <div className={this.state.show_lambdas == true ? "show-protocols" : "d-none"}>
                <ProtocolList protocols={this.state.lambdas}/>
              </div>

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
