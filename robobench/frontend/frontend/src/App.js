import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';

import TableDragSelect from 'react-table-drag-select';
// import 'react-table-drag-select/style.css';

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
    const wells = [1,2,3,4,5,6,7,8].map((id) => <td className='well'><div className='circle'></div></td>);
    const rows = [1,2,3,4,5,6,7,8,9,10,11,12].map((id) => <tr key={id}>{wells}</tr>);

    return (
      <div className="labware-well-96">
        <TableDragSelect className={this.props.mode} model={this.state.model} onModelChange={this.handleModelChange}>
            {rows}
        </TableDragSelect>
      </div>
    )
  }

  handleModelChange(model) {
    this.props.updateMode();
    this.setState({model});
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

  updateMode(key) {
    console.log(key)
    if (!this.state.source) {
      this.setState({ source: key })
    } else if (!this.state.dest && this.state.source != key) {
      this.setState({ dest: key })
    }
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
      if (this.state.labware[key] == 'WellPlate') {
        var mode = 'none'
        if (this.state.source == key) mode = 'source'
        else if (this.state.dest == key) mode = 'dest'

        grid[key] = <WellPlate key={key} mode={mode} updateMode={() => this.updateMode(key)}/>;
      }
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
          <div className="col-sm-10 fill">
            <Grid />
          </div>
        </div>
    );
  }
}

export default App;
