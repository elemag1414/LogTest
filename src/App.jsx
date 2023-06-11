import { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import MainPanel from './MainPanel';
import './App.css'

function App() {
  const [selectedData, setSelectedData] = useState(null);
  const [data, setData] = useState(null);
  const [plotData, setPlotData] = useState(null);
  const [smooth, setSmooth] = useState(0.0);

  useEffect(() => {
    // fetch(`/api/data/${selectedData}`)
    //     .then(response => response.json())
    //     .then(data => {
    //       setData(data);
    //     });
    
    fetch(`/api/data_lists`)
        .then(response => response.json())  // 여기서 반환된 Promise를 다음 then에서 처리합니다.
        .then(data => {
            setData(data);
            // console.log('fetch data done...');
        });
  }, []);

  const findKeyForItem = (item) => {
    for (let key in data) {
      if (data[key].includes(item)) {
        return key;
      }
    }
    return null; // return null if the value is not found
  }

  const updatePlotData = (item) => {
    const node_name = findKeyForItem(item);
    setSelectedData(node_name);
    fetch(`/api/data/${node_name}/${item}`)
        .then(response => response.json())  // 여기서 반환된 Promise를 다음 then에서 처리합니다.
        .then(data => {
            setPlotData(data.data.data);
        });
    
  }

  return (
    <div className="App">
      <Sidebar 
            updateHandler={updatePlotData} 
            smooth={smooth} 
            setSmooth={setSmooth}
            data={data}
            setData={setData}
      />
      {plotData && (<MainPanel data={plotData} smooth={smooth} selectedData={selectedData}/>)}
    </div>
  )
}

export default App
