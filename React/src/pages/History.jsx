import React, {useEffect, useState} from 'react'
import { Button, Tooltip } from '@mui/material';
import { DataGridPro } from '@mui/x-data-grid-pro';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { styled } from '@material-ui/core';

const drawerWidth = 200;
const DrawerHeader = styled('div')(({ theme }) => ({
	display: 'flex',
	alignItems: 'center',
	padding: theme.spacing(0, 1),
	...theme.mixins.toolbar, // necessary for content to be below app bar
	justifyContent: 'flex-end',
}));

const Main = styled("main", { shouldForwardProp: (prop) => prop !== "open" })(
	({ theme, open }) => ({
		flexGrow: 1,
		padding: theme.spacing(3),
		transition: theme.transitions.create("margin", {
		easing: theme.transitions.easing.sharp,
		duration: theme.transitions.duration.leavingScreen
		}),
			marginLeft: `-${drawerWidth}px`,
			...(open && {
			transition: theme.transitions.create("margin", {
			easing: theme.transitions.easing.easeOut,
			duration: theme.transitions.duration.enteringScreen
		}),
			marginLeft: 0
		})
	})
);

const History = ({open}) => {
    // For data grid and From data grid
    const [rows, setRows] = useState([]);
	const [columns, setColumns] = useState([]);
    const [selectedIDs, setSelectedIDs] = useState([]);
    
    // This variable will pass in table and form information to Table page on submit
	const navigate = useNavigate();

    // When history page opens, version data will be shown
    useEffect(() => {		
        axios.get('/getVersionBudgetPlanInformation', {
            headers: {
		        'Content-Type':'application/json'
		    },
        }).then((res) => {
            setColumns(res.data[0])
			setRows(res.data[1])
        })
    }, []);

    // get old history data from the version graph database
    // save it back to the budget neo4j graph database
    const handleRetrieve = () => {
        if (selectedIDs.length === 1) {
            const version = rows[selectedIDs[0] - 1]['version']
            axios.post('/retrieve',  JSON.stringify({version: version}), {
                headers: {
                'Content-Type':'application/json'
                }
            }).then((res) => {
                if (res.data === 'fail') {
                    alert('budget is already in the list')
                } else {
                    alert('budget successfully retrieved')
                    axios.get('/getVersionBudgetPlanInformation', {
                        headers: {
                            'Content-Type':'application/json'
                        },
                    }).then((res) => {
                        setColumns(res.data[0])
                        setRows(res.data[1])
                    }) 
                    navigate('/plans')
                }   
            });
        } else {
            alert('select one to retrieve back to your plan list')
        }
    }

	return (
        <Main open={open}>
            <DrawerHeader />
            <Tooltip title="Retrieve Plan">
                <Button onClick={handleRetrieve}>Retrieve Plan</Button>
            </Tooltip>
            <div style={{ height: 700, width: '900px' }}>
                <DataGridPro
                    rows={rows}
                    columns={columns}
                    rowHeight={35}
                    headerHeight={30}
                    hideFooter={true} // hide the footer block under the table
                    hideFooterRowCount = {true}
                    checkboxSelection
                    disableSelectionOnClick
                    onSelectionModelChange = {(selectionModel) =>
                        setSelectedIDs(selectionModel)
                    }
                />
            </div>
        </Main>
	)
}

export default History