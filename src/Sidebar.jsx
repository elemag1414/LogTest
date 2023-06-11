import React, { useState, useEffect } from 'react';
import { Button, Select, Slider, Divider } from "antd";

function Sidebar({ updateHandler, smooth, setSmooth, data, setData }) {
    const menuItems = ['home_data', 'electron_data'];
    const [clickedItem, setClickedItem] = useState(null);
    const [fetchWaiting, setFetchWaiting] = useState(false);

    // useEffect(() => {
    //     fetch(`/api/data_lists`)
    //         .then(response => response.json())  // 여기서 반환된 Promise를 다음 then에서 처리합니다.
    //         .then(data => {
    //             setData(data);
    //         });
    // }, [selectedData]);

    const buttonHandler = (val) => {
        setFetchWaiting(true);
        console.log("Button Handler ");
        fetch(`/api/data/new_fetch`)
            .then(response => response.json())  // 여기서 반환된 Promise를 다음 then에서 처리합니다.
            .then(data => {
                console.log(data);
                setFetchWaiting(false);
                updateHandler(clickedItem);
            });
    }


    const handleClick = (item) => {
        setClickedItem(item);
        updateHandler(item);
    }

    return (
        <div className="sidebar">
            <Divider />
            <h2>JEONG's Board</h2>
            <Divider />
            <div className="slider">
                <h3>Smooth</h3>
                <Slider 
                    min={0.0} max={0.9} step={0.1} 
                    value={smooth} 
                    style={{width:'80%'}}
                    onChange={(value) => setSmooth(value)}
                ></Slider>
                <p>{smooth}</p>
            </div>
            <Divider />

            <div className="dropdown">
                <h3>Select Data</h3>
                
                {/* <Select 
                    placeholder={selectedData}
                    style={{width:'80%'}}
                    defaultValue={menuItems[0].toUpperCase()}
                    onChange={(e) => setSelectedData(e)}
                >
                    {menuItems.map((menu, index) => {
                        return <Select.Option key={index} value={menu}>{menu.toUpperCase()}</Select.Option>
                    })}
                </Select> */}

                {data && Object.keys(data).map(key => (
                <div key={key}>
                    <h3>{key}</h3>
                    <ul>
                    {data[key].map(item => (
                        <li 
                            key={item} 
                            onClick={() => handleClick(item)} 
                            className={`hoverable ${clickedItem === item ? 'clicked' : ''}`} // apply the 'clicked' class if this item is the clicked item
                        >
                        {item}
                        </li>
                    ))}
                    </ul>
                </div>
                ))}

            </div>
            <br />
            <div className='fetchbutton'>
                <Button 
                    // type='primary' 
                    type={fetchWaiting?'ghost':'primary'} 
                    style={{width:'80%'}} 
                    onClick={buttonHandler}
                >Fetch Data</Button>
            </div>
        </div>
    );
}

export default Sidebar;