import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

function PlotData({ title, data, max, min, epoch}) {

  const width = 600;
  const height = 400;

  let lastKey = Object.keys(data)[Object.keys(data).length - 1];
  let lastObject = data[lastKey];
  if (lastObject == undefined) return <></>
  const lastEpoch = lastObject.name;
  const lastEpochValue = lastObject.eval;

  return (
    <div className="plotdata">
        <h3>{title}</h3>
        <div style={{display: 'flex'}}>
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
              <h5>{min.toFixed(2)}% @{epoch} (min)</h5>
            )
          }

          <h5>{lastEpochValue}% @{lastEpoch} (latest)</h5>
          </div>

        </div>
      </div>
  )
}

export default PlotData