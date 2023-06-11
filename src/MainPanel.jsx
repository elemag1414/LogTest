import { useState, useEffect } from 'react';
import PlotData from './PlotData';
import { Divider } from "antd";

function calculateEMA(data, smooth) {
  let emaData = [];
  let multiplier = smooth / (1 + smooth);
  let previousEMA = data[0];

  if (smooth == 1.0) return data;

  for (let i = 0; i < data.length; i++) {
    let currentEMA = (data[i] - previousEMA) * multiplier + previousEMA;
    emaData.push(currentEMA);
    previousEMA = currentEMA;
  }

  return emaData;
}

function cvtData(tdata, edata, smooth) {
  const trainData = calculateEMA(tdata, (1.0 - smooth));
  const evalData = calculateEMA(edata, (1.0 - smooth));
  
  return trainData.map((value, index) => ({
    name: `${index+1}`, 
    train: value, 
    eval: evalData[index]
  }));
}

const MainPanel = ({ data, smooth, selectedData }) => {

  if (!data) return (<div></div>);

  const [F1Data, setF1Data] = useState(null)
  const [iouData, setIouData] = useState(null)
  const [accuData, setAccuData] = useState(null);
  const [lossData, setLossData] = useState(null);
  const [maxF1, setMaxF1] = useState(null);
  const [maxAccu, setMaxAccu] = useState(null);
  const [maxIou, setMaxIou] = useState(null);
  const [minLoss, setMinLoss] = useState(null);
  const [maxF1Epoch, setMaxF1Epoch] = useState(null);
  const [maxAccuEpoch, setMaxAccuEpoch] = useState(null);
  const [maxIouEpoch, setMaxIouEpoch] = useState(null);
  const [minLossEpoch, setMinLossEpoch] = useState(null);

  const width = 600;
  const height = 400;

  useEffect(() => {
    const calculatedMax = (_data) => Math.max(..._data);
    const calculatedMin = (_data) => Math.min(..._data);
    setMaxAccu(calculatedMax(data.eval.accu));
    setMaxIou(calculatedMax(data.eval.iou));
    setMinLoss(calculatedMin(data.eval.loss));
    setMaxAccuEpoch(data.eval.accu.indexOf(calculatedMax(data.eval.accu)) + 1);
    setMaxIouEpoch(data.eval.iou.indexOf(calculatedMax(data.eval.iou)) + 1);
    setMinLossEpoch(data.eval.loss.indexOf(calculatedMin(data.eval.loss)) + 1);

    if (data.eval.f1) {
      const calculatedMaxF1 = Math.max(...data.eval.f1);
      setMaxF1(calculatedMaxF1);
      setMaxF1Epoch(data.eval.f1.indexOf(calculatedMaxF1) + 1);
      setF1Data(cvtData(data.train.f1, data.eval.f1, smooth));
    } else {
      setF1Data(null);
    }
    setIouData(cvtData(data.train.iou, data.eval.iou, smooth));
    setAccuData(cvtData(data.train.accu, data.eval.accu, smooth));
    setLossData(cvtData(data.train.loss, data.eval.loss, smooth));
  }, [data, smooth, selectedData])

  return (
    <div className="mainwindow">
      <Divider />
      { F1Data && (
          <PlotData title="F1" data={F1Data} max={maxF1} epoch={maxF1Epoch} />
        )
      }
      {iouData && (
      <PlotData title="IOU" data={iouData} max={maxIou} epoch={maxIouEpoch} />)}
      {accuData && (
      <PlotData title="ACCU" data={accuData} max={maxAccu} epoch={maxAccuEpoch} />)}
      {lossData && (
      <PlotData title="Loss" data={lossData} min={minLoss} epoch={minLossEpoch} />)}
    </div>
  );
};

export default MainPanel;
