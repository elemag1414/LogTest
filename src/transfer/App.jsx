import { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import MainPanel from './MainPanel';
import { Button, Divider, Modal } from "antd";
import './App.css'

function App() {
  const [selectedData, setSelectedData] = useState(null);
  const [data, setData] = useState(null);
  const [plotData, setPlotData] = useState(null);
  const [smooth, setSmooth] = useState(0.0);
  const [dataConfig, setDataConfig] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [plotTitle, setPlotTitle] = useState(null);

  useEffect(() => {
    fetch(`/api/data_lists`)
        .then(response => response.json())  // 여기서 반환된 Promise를 다음 then에서 처리합니다.
        .then(data => {
            console.log('[App] data: ', data);
            setData(data);
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
    // console.log('[updatePlotData] node_name: ', node_name, {node_name: node_name, item: item});
    setSelectedData({node_name: node_name, item: item});
    fetch(`/api/data/${node_name}/${item}`)
        .then(response => response.json())  // 여기서 반환된 Promise를 다음 then에서 처리합니다.
        .then(data => {
            // console.log("[updatePlotData] data: ", data.data.data);
            setPlotData(data.data.data);
            setDataConfig(data.data.config);
            setPlotTitle(data.data.config.architecture + '/' + data.data.config.baseModel);
            // console.log("[Config] ", data.data.config);
        });
    
  }

  const showModal = () => {
    setIsModalOpen(true);
  };
  const handleOk = () => {
    setIsModalOpen(false);
  };
  const handleCancel = () => {
    setIsModalOpen(false);
  };

  return (
    <div className="App">
      <Sidebar 
            updateHandler={updatePlotData} 
            smooth={smooth} 
            setSmooth={setSmooth}
            data={data}
            showModal={showModal}
      />
      {plotData && (<MainPanel title={plotTitle} data={plotData} smooth={smooth} selectedData={selectedData}/>)}
      <Modal 
              title="Config Description" 
              width={800}
              open={isModalOpen} 
              onOk={handleOk} 
              onCancel={handleCancel}
      >
      {
        dataConfig&&
        Object.entries(dataConfig).map(([key, value]) => (
          <div key={key}>
            <strong style={{color: 'black'}}>{key}</strong>: {value.toString()}
          </div>
        ))
      }
      </Modal>
    </div>
  )
}

export default App
