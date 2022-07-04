import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import Leftbar from "./components/Leftbar";
import Create from "./pages/Create";
import Feedback from "./pages/Feedback";
import History from "./pages/History";
import Home from "./pages/Home";
import Plans from "./pages/Plans";
import Settings from "./pages/Settings";
import Table from "./pages/Table";
import Logout from "./pages/Logout";
import SignIn from "./pages/SignIn"
import SignUp from "./pages/SignUp"
import Box from '@mui/material/Box';

import {
	BrowserRouter as Router,
	Routes,
	Route,
} from "react-router-dom";


const App = () => {
    const [open, setOpen] = useState(true);
    const [authType, setAuthType] = useState("login");
    const [division, setDivision] = useState("");
    const [userName, setUserName] = useState("");

    useEffect(() => {
        if(sessionStorage.getItem('division') !== null) {
            setDivision(sessionStorage.getItem('division'))
            setUserName(sessionStorage.getItem('userName'))
            // console.log(sessionStorage.getItem('userName'))
        }
    }, [])


    if (division === "") {
        return (
            <>
                {authType === "login" && <SignIn setAuthType={setAuthType} setDivision={setDivision} setUserName={setUserName} />}
                {authType === "signup" && <SignUp setAuthType={setAuthType} />}
            </>
        )
    };

    return (
        <div className="App">
            <Navbar open={open} setOpen={setOpen}/>
            <Box sx={{ display: "flex" }}>
            <Router>
                <Leftbar open={open}/>
                <Routes>
                <Route exact path="/" element={<Home open={open} division={division}/>}/> 
                <Route path="/create" element={<Create open={open} division={division} userName={userName} />}/>
                <Route path="/plans" element={<Plans open={open} division={division} userName={userName} />}/> 
                <Route path="/history" element={<History open={open} />}/>              
                <Route path="/feedback" element={<Feedback open={open} />}/> 
                <Route path="/settings" element={<Settings open={open} />}/> 
                <Route path="/logout" element={<Logout open={open} setAuthType={setAuthType}/>}/> 
                <Route path="/table" element={<Table open={open} division= {division} userName={userName}/>}/> 
                </Routes>
            </Router>
            </Box>
        </div>
    )
}

export default App;