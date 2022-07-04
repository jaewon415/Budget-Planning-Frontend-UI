import React, {useEffect, useState} from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { BarChart, Bar,ReferenceLine} from 'recharts';
import { DataGridPro } from '@mui/x-data-grid-pro';
import axios from 'axios'
import { createStyles, makeStyles } from "@mui/styles";
import { FormControl, InputLabel, Box, MenuItem, Select} from '@mui/material'
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

const Home = ({open, division}) => {

    const [versions, setVersions] = useState([]); 
    const [dataLine, setDataLine] = useState([]);
    const [dataBar, setDataBar] = useState([]);
    // This two variables are for generating a datagrid
    const [rows, setRows] = useState([]);
    const [columns, setColumns] = useState([]);
    const getTreeDataPath = (row) => row.hierarchy; 

    // when plan page is opened, this function will grab budget graphs from the neo4j database
	useEffect(() => {
        axios.post('/getBudgetPlanPropertyForHome',  JSON.stringify({division}), {
            headers: {
                'Content-Type':'application/json'
            },
        }).then((res) => {
            console.log(res.data)
            setVersions(res.data)
        })
        
    }, [division]);

    const [firstBudget, setFirstBudget] = React.useState('');
    // const [secondBudget, setSecondBudget] = React.useState('');

    const handleFirstBudgetChange = (event) => {
        setFirstBudget(event.target.value);
    };

    // const handleSecondBudgetChange = (event) => {
    //     setSecondBudget(event.target.value);
    // };

    // make changes to datagrid styles
	const useStyles = makeStyles((theme) =>
        createStyles({
            root: {
                '& div[aria-rowindex]' : {
                    fontFamily: 'Georgia, serif',
                    fontSize: 14
                },
                '.MuiDataGrid-columnSeparator': {
                    display: 'none',
                },
            },

            budgetGraph: {
                display: 'flex',
            },
            
            graphHeader: {
                marginLeft: '210px'
            }
        })
    );
    const classes = useStyles();

    useEffect(() => {
        if (firstBudget !== '') {
            axios.post('/getVersionInfoForHome',  JSON.stringify({firstBudgetVersion: firstBudget}), {
				headers: {
				'Content-Type':'application/json'
				}
			}).then((res) => {
                // console.log(GRID_TREE_DATA_GROUPING_FIELD);
                setDataLine(res.data[0])
                setDataBar(res.data[1])

                setColumns(res.data[2])
                setRows(res.data[3])
            })
        }
    }, [firstBudget]);

    return (
        <Main open={open}>
            <DrawerHeader />
                <div className={classes.budgetSelector}>
                <div className="budgetSelectorOne">
                        <Box sx={{ m: 1, maxWidth: 500, minWidth:300 }}>
                            <FormControl fullWidth>
                                <InputLabel id="first-budget-select-label">Budget</InputLabel>
                                <Select
                                labelId="first-budget-select-label"
                                id="first-budget-select"
                                value={firstBudget}
                                label="Budget Plan"
                                onChange={handleFirstBudgetChange}
                                >
                                {
                                    versions.map((ver, idx) => {
                                        return <MenuItem key={idx} value={ver}>Budget {ver}</MenuItem>
                                    })
                                }
                                </Select>
                            </FormControl>
                        </Box>
                    </div>
                </div>
                <div className={classes.budgetGraph}>
                    <div className="budgetLinear">
                        <br/>   
                        <h3 className={classes.graphHeader}>Line Chart</h3>
                        <br/>
                        <div className="graph">
                            <ResponsiveContainer width="100%" height="100%" minWidth='500px' minHeight='300px'>
                                <LineChart
                                    width={700}
                                    height={400}
                                    data={dataLine}
                                    margin={{ top: 10, left: 35, right: 25, bottom: 20 }}
                                    // margin={{ top: 20, left: -50, right: 0, bottom: 20 }} 
                                >
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="name"/>
                                <YAxis />
                                <Tooltip />
                                <Line type="monotone" dataKey="actual" stroke="#8884d8" activeDot={{ r: 5 }} />
                                <Line type="monotone" dataKey="budget" stroke="#82ca9d" />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                    <div className="budgetPie">
                        <br/>
                        <h3 className={classes.graphHeader}>Variance Chart</h3>
                        <br/>
                        <div className="graph">
                            <ResponsiveContainer width="100%" height="100%" minWidth='500px' minHeight='300px'>
                                <BarChart
                                    width={700}
                                    height={400}
                                    data={dataBar}
                                    margin={{ top: 10, left: 35, right: 25, bottom: 20 }}
                                    // margin={{ top: 20, left: -50, right: 0, bottom: 20 }} 
                                >
                                    <CartesianGrid strokeDasharray="3 3" />
                                    <XAxis dataKey="name" />
                                    <YAxis />
                                    <Tooltip />
                                    <ReferenceLine y={0} stroke="#000" />
                                    <Bar dataKey="value" fill="#8884d8" barSize={20} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                <div className="budgetGrid" style={{ height: 300, width: '1000px'}}>
                <DataGridPro
                    treeData
                    groupingColDef={{hideDescendantCount: true, headerName: ' ', width: 200}}
                    columns={columns}
                    rows={rows}
                    rowHeight={35}
                    headerHeight={30}
                    hideFooter={true} // hide the footer block under the table
                    className={classes.root}
                    disableColumnMenu={true}
                    hideFooterRowCount = {true}
                    defaultGroupingExpansionDepth = {-1}
                    getTreeDataPath={getTreeDataPath}
                    disableSelectionOnClick

                />
                </div>
        </Main>
    )
}

export default Home