import React, {useRef} from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import html2canvas from 'html2canvas';
import { FaDownload } from 'react-icons/fa';
import {CiFloppyDisk} from 'react-icons/ci';
import {CgSoftwareDownload} from 'react-icons/cg';

function PlotData({ title, data, max, min, epoch, selectedData}) {

  const width = 700;
  const height = 500;
  const ref = useRef();

  let lastKey = Object.keys(data)[Object.keys(data).length - 1];
  let lastObject = data[lastKey];
  if (lastObject == undefined) return <></>
  const lastEpoch = lastObject.name;
  const lastEpochValue = lastObject.eval;

  // console.log('[PlotData] selectedData: ', selectedData);
  const download = () => {
    html2canvas(ref.current).then((canvas) => {
      const imgData = canvas.toDataURL('image/png');
      const link = document.createElement('a');
      console.log('download: ', title);
      link.href = imgData;
      link.download = selectedData.node_name + '_' + selectedData.item + '_' + title + '_chart.png';
      link.click();
    });
  };

  return (
    <div className="plotdata" style={{ position: 'relative' }}>
        <h3>{title}</h3>
        <button onClick={download} style={{ position: 'absolute', zIndex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
          {/* <FaDownload /> */}
          {/* <CiFloppyDisk /> */}
          <CgSoftwareDownload />
        </button>
        <div style={{display: 'flex', marginLeft: '1rem'}} ref={ref}>
          <LineChart
            width={width}
            height={height}
            data={data}
            margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="train" stroke="#8884d8" dot={false} strokeWidth={3} />
            <Line type="monotone" dataKey="eval" stroke="#82ca9d" dot={false} strokeWidth={3} />
          </LineChart>

          <div style={{
            textAlign: 'left',
            lineHeight: '0px'
          }}>
          {max && (
            max > 95?
              <h5 style={{color: 'red'}}>{max}% @{epoch} (max)</h5>
              :  
              <h5>{max.toFixed(2)}% @{epoch} (max)</h5>
            )
          }

          {min && (
              <h5>{min}% @{epoch} (min)</h5>
            )
          }

          <h5>{min?lastEpochValue:lastEpochValue.toFixed(2)}% @{lastEpoch} (latest)</h5>
          
          </div>

        </div>
      </div>
  )
}

export default PlotData
