import React, {useEffect, useState} from 'react'
import axios from 'axios'
import { DataGridPro } from '@mui/x-data-grid-pro';
import { createStyles, makeStyles } from "@mui/styles";
import { Button, Tooltip, TextField, Grid, Typography, Dialog, DialogTitle, DialogContent, DialogContentText, MenuItem, DialogActions} from '@mui/material';
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

// This variable takes default values of the form
const default_create_form_inputs = {
	plan_name: '',
	start_plan_date: '', end_plan_date: '', 
	plan_base_period: '', 
	plan_description: '',
	plan_constraints: '',
}

const mergeKeys = [
	{
		label: 'Use First Budget',
		value: 'first',
	},
	{
		label: 'Use Second Budget',
		value: 'second',
	},
	{
		label: 'Take Average',
		value: 'average',
	},
	{
		label: 'Leave it as a zero',
		value: 'zero',
	},
  ];

const default_dialog_merge = {
	mergeType: ''
}


const Plans = ({open, division, userName}) => {

	// This variable store default values of the form
	const [mergeForm, setMergeForm] = useState(default_dialog_merge);
	const [openMerge, setOpenMerge] = useState(false);
	const handleMergeClose = () => {
		setMergeForm(default_dialog_merge)
		setOpenMerge(false);
	};

	// This function will disaggregate the budget plan along the hierarchy
	const handleMerge = () => {
		setOpenMerge(true);
	}

	// This function allows user to write on the form 
	const handleMergeChange = (e) => {
		if (e.target !== undefined) {
			const { name, value } = e.target;
			setMergeForm({
				...mergeForm,
				[name]:value,
			});
		}
	}


	// This variable store default values of the form
	const [form, setForm] = useState(default_create_form_inputs);
	// Because we need to make changes to the budget graph that has a specified version on submit
	const [ver, setVer] = useState();
	// This two variables are for generating a datagrid
	const [rows, setRows] = useState([]);
	const [columns, setColumns] = useState([]);
	const getTreeDataPath = (row) => row.hierarchy;
	// Need to keep track of which row in the plan dataset are chosen
	const [selectedIDs, setSelectedIDs] = useState([]);
	// Onclick Edit Plan button
	const navigate = useNavigate();

	// when plan page is opened, this function will grab budget graphs from the neo4j database
	useEffect(() => {
		// console.log(division)
		axios.post('/getBudgetPlanProperty',  JSON.stringify({division}), {
		    headers: {
		        'Content-Type':'application/json'
		    },
		}).then((res) => {
			setColumns(res.data[0])
			setRows(res.data[1])
		})
    }, [division]);

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
			planScreen: {
				display: 'flex',
				// padding: theme.spacing(10),
			},
			planScreenRight: {
				marginLeft: 20,
				marginTop: 0,
				width: '100%',
				textAlign: 'center',
			},
			formDescriptionHeader: {
				marginTop: 5,
				marginBottom: 10,
				fontWeight: 'bold',
				color: '#1565c0',
			}
		})
	);

	
	// Onclick edit, this function will grab selected version budget graph from the neo4j
	// and send it to the table plage.
	const handleEdit = () => {
		if (selectedIDs.length === 1) {
			const version = rows[selectedIDs[0] - 1]['hierarchy']
			const versionToEdit = version[version.length - 1]
			axios.post('/editBudgetPlan', JSON.stringify({version: versionToEdit, division: division}), {
				headers: {
					'Content-Type':'application/json'
				},
			}).then((res) => {
				navigate('/table', {state: {data: [...res.data][0], view: true, version: version, combinedForm: res.data[1]}})
			})
		} else {
			alert("Select One Budget Plan to Edit")
		}
	};
	
	// Onclick merge, this function will grab selected versions budget graph from the neo4j
	// and merge them together. When done, the page will refresh
	const handleMergeSubmit = (e) => {
		if (selectedIDs.length === 2) {
			// get first verion infomr
			const firstVersion = rows[selectedIDs[0] - 1]['hierarchy']
			const secondVersion = rows[selectedIDs[1]- 1]['hierarchy']
			axios.post('/mergeBudgetPlans',  JSON.stringify({
				firstVersion: firstVersion[firstVersion.length - 1], 
				secondVersion: secondVersion[secondVersion.length - 1],
				mergeForm: mergeForm,
			}), {
				headers: {
				'Content-Type':'application/json'
				}
			}).then(() => {
				setOpenMerge(false)
				// need to refresh after merge
				axios.post('/getBudgetPlanProperty',  JSON.stringify({division}), {
					headers: {
						'Content-Type':'application/json'
					},
				}).then((res) => {
					setColumns(res.data[0])
					setRows(res.data[1])
				})
			});
		} else {
			setOpenMerge(false)
			alert('Select Two Budget Plans to Merge')
		}
		setMergeForm(default_dialog_merge)
	}

	// onClick clone button, it will clone the selected rows
	const handleClone = () => {
		if (selectedIDs.length <= 1 && selectedIDs.length > 0) {
			const getPlanVersion = rows[selectedIDs[0] - 1]['hierarchy']
			const version = getPlanVersion[getPlanVersion.length - 1]
			axios.post('/cloneBudgetPlan',  JSON.stringify({version: version, userName: userName}), {
				headers: {
					'Content-Type':'application/json'
				},
			}).then((res) => {
				setColumns(res.data[0])
				setRows(res.data[1])
			})
		} else {
			alert("Select One Budget Plan to Clone")
		}
	}

	// onClick delete budget graph from the neo4j budget graph database
	const handleDelete = () => {
		if (selectedIDs.length <= 1 && selectedIDs.length > 0) {
			const getPlanVersion = rows[selectedIDs[0]- 1]['hierarchy']
			const version = getPlanVersion[getPlanVersion.length - 1]
			axios.post('/delete',  JSON.stringify({version: version, division: division}), {
				headers: {
					'Content-Type':'application/json'
				},
			}).then((res) => {
				setColumns(res.data[0])
				setRows(res.data[1])
			})

		} else {
			alert("Select One Budget Plan for Deletion")
		}
  	};

	// This function allows user to write on the form 
	const handleChange = (e) => {
		if (e.target !== undefined) {
			const { name, value } = e.target;
			setForm({
				...form,
				[name]:value,
			});
		}
	}

	// This function will take the form values and pass them to python to grab table data
	const handleSubmit = (e) => {
		axios.post('/planPropertySaveAsForm',  JSON.stringify({form: form, version: ver}), {
			headers: {
				'Content-Type':'application/json'
			},
		}).then(() => {
			setForm(default_create_form_inputs)
			setVer()
		})
	};

	// OnClick Save As button, previous form data will be retrieved
	const handleSaveAs = () => {
		if (selectedIDs.length === 1) {
			// console.log(rows)
			const getPlanVersion = rows[selectedIDs[0] - 1]['hierarchy']
			const version = getPlanVersion[getPlanVersion.length - 1]
			axios.post('/saveAs',  JSON.stringify({version: version}), {
				headers: {
					'Content-Type':'application/json'
				},
			}).then((res) => {
				// console.log(res)
				setVer(version)
				setForm(prevState => ({
					...prevState,
					plan_name: res.data[0],
					plan_description: res.data[1],
					plan_created: res.data[2],
					plan_base_period: res.data[3],
					start_plan_date: res.data[4],
					end_plan_date: res.data[5],
					plan_constraints: res.data[6],
				 }));
			})
		} else {
			alert('Select One Plan for Save As')
		}
	}

	const classes = useStyles();

	return (
		<Main open={open}>
            <DrawerHeader />
			<div className={classes.planScreen}>
				<div className={classes.planScreenLeft}>
					<Tooltip title="Clone Plan">
						<Button onClick={handleClone}>Clone</Button>
					</Tooltip>
					<Tooltip title="Delete Plan">
						<Button onClick={handleDelete}>Delete</Button>
					</Tooltip>
					<Tooltip title="Merge Plans">
						<Button onClick={handleMerge}>Merge</Button>
					</Tooltip>
					<Tooltip title="Edit Plan">
						<Button onClick={handleEdit}>Edit Plan</Button>
					</Tooltip>
					<Tooltip title="Save As">
						<Button onClick={handleSaveAs}>Save As</Button>
					</Tooltip>
					
					<Dialog open={openMerge} onClose={handleMergeClose} fullWidth maxWidth="xs">
						<DialogTitle>Merge Budget Plan</DialogTitle>
						<DialogContent>
						<DialogContentText>
							On Conflict?
						</DialogContentText>
						<br/>
						<TextField
							id="outlined-select-merge"
							select
							fullWidth
							required
							autoComplete = 'off'
							name = 'mergeType'
							label="Choose Merge Type To Use"
							value={mergeForm.mergeType}
							onChange={handleMergeChange}
							>
							{mergeKeys.map((option) => (
								<MenuItem key={option.value} value={option.value}>
								{option.label}
								</MenuItem>
							))}
						</TextField>
						</DialogContent>
							<DialogActions>
							<Button onClick={handleMergeClose}>Cancel</Button>
							<Button onClick={handleMergeSubmit}>Submit</Button>
						</DialogActions>
					</Dialog>

					<div style={{ height: 400, width: '700px' }}>
						<DataGridPro
							treeData
							groupingColDef={{hideDescendantCount: true, headerName: 'Version', headerAlign: 'center', width: 150}}
							rows={rows}
							columns={columns}
							rowHeight={35}
							headerHeight={30}
							hideFooter={true} // hide the footer block under the table
							className={classes.root}
							disableColumnMenu={true}
							hideFooterRowCount = {true}
							checkboxSelection = {true}
							defaultGroupingExpansionDepth = {-1}
							getTreeDataPath={getTreeDataPath}
							disableSelectionOnClick
							onSelectionModelChange = {(selectionModel) =>
								setSelectedIDs(selectionModel)
							}
						/>
					</div>
				</div>
				<div className={classes.planScreenRight}>
					<div className={classes.formDescriptionHeader}>
						<Typography>
							Plan Information
						</Typography>
					</div>
					<form className="form" onSubmit={handleSubmit} id='myform'>
						<Grid container direction="column" spacing={2}>
							<Grid item>
								<TextField
									name="plan_name"
									label="Plan Name"
									type="text"
									required
									fullWidth
									autoComplete = 'off'
									size='small'
									InputLabelProps={{ shrink: true }} 
									value={form.plan_name || ""}
									onChange={handleChange}
								/>
							</Grid>
							<Grid item>
								<TextField
									name="plan_description"
									label="Plan Description"
									multiline
									required
									fullWidth
									autoComplete = 'off'
									size='small'
									InputLabelProps={{ shrink: true }} 
									value={form.plan_description || ""}
									onChange={handleChange}
								/>
							</Grid>
							<Grid item>
								<TextField
									name="start_plan_date"
									label="Start Plan"
									type="text"
									required
									fullWidth
									autoComplete = 'off'
									size='small'
									InputLabelProps={{ shrink: true }} 
									value={form.start_plan_date || ""}
									onChange={handleChange}
								/>
							</Grid>
							<Grid item>
								<TextField
									name="end_plan_date"
									label="End Plan"
									type="text"
									required
									fullWidth
									autoComplete = 'off'
									size='small'
									InputLabelProps={{ shrink: true }} 
									value={form.end_plan_date || ""}
									onChange={handleChange}
								/>
							</Grid>
							<Grid item>
								<TextField
									name="plan_created"
									label="Date Created"
									type="text"
									required
									fullWidth
									autoComplete = 'off'
									size='small'
									InputLabelProps={{ shrink: true }} 
									value={form.plan_created || ""}
									onChange={handleChange}
								/>
							</Grid>
							<Grid item>
								<TextField
									name="plan_constraints"
									label="Plan Constraints"
									multiline
									fullWidth
									autoComplete = 'off'
									size='small'
									InputLabelProps={{ shrink: true }} 
									value={form.plan_constraints || ""}
									onChange={handleChange}
									inputProps={{
										style: {
										height: "130px",
										},
									}}
								/>
							</Grid>
						</Grid>
					</form>
					<Button type="submit" form="myform">Save</Button>
				</div>	
			</div>
		</Main>
	)
}

export default Plans
