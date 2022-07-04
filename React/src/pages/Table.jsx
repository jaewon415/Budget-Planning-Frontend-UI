import React, { useState, useCallback} from 'react'
// import './table.css'
import axios from 'axios';
// import Sidebar from '../../components/sidebar/Sidebar'
import { useLocation, useNavigate } from 'react-router-dom';
import { DataGridPro, useGridApiRef } from '@mui/x-data-grid-pro';
import { createStyles, makeStyles } from "@mui/styles";
import { Button, MenuItem, Tooltip,Grid, TextField, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';
import { styled } from '@material-ui/core';


const drawerWidth = 200;
const DrawerHeader = styled('div')(({ theme }) => ({
	display: 'flex',
	alignItems: 'center',
	padding: theme.spacing(0, 1),
	...theme.mixins.toolbar, // necessary for content to be below app bar
	justifyContent: 'flex-end',
}));

// This variable is to give selection of inequality signs available
const inequality = [
	{ value: '<=', label: '<=' },
	{ value: '<', label: '<' },
	{ value: '>=', label: '>=' },
	{ value: '>', label: '>' },
	{ value: '=', label: '=' },
	{ value: 'None', label: 'None' }
];

// This variable is to give selection of operations  available
const operator = [
	{ value: '*', label: '*' },
	{ value: '+', label: '+' },
	{ value: '-', label: '-' },
	{ value: 'None', label: 'None' }
];


const Main = styled("main", { shouldForwardProp: (prop) => prop !== "open" })(
	({ theme, open }) => ({
		flexGrow: 1,
		padding: theme.spacing(2),
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
const default_dialog_form_inputs = {
	disaggregateType: '',
	hierarchyOfInterest: '',
	periodOfInterest: '', 
	amount: '', 
	referential: '',
	lock: '',
}

const disaggregateFormula = [
	{
		label: 'Referential Disaggregation',
		value: 'Referential',
	},
	{
		label: 'Interval Disaggregation',
		value: 'Interval',
	},
	{
		label: 'Proportional Disaggregation',
		value: 'Proportional',
	},
	{
		label: 'Row Average',
		value: 'Average',
	},
  ];

const Table = ({open, division, userName}) => {
	// This variable store default values of the form
	const [form, setForm] = useState(default_dialog_form_inputs);

	const [formula, setFormula] = useState('');

	const apiRef = useGridApiRef();
	const location = useLocation();
	const column_values = location.state.data[0]
	const row_values = location.state.data[1];
	const combinedForm = location.state.combinedForm
	const viewBoolean = location.state.view
	const viewVersion = location.state.version

	const budgetNameView = location.state.budgetNameView
	const budgetNameEdit = location.state.budgetNameEdit


	// This variable is for storing constraint values 
	const [constraints, setConstraints] = useState([
		{ hierarchyOne: 'None', 
		inequality: 'None', 
		values: 'None',
		operator: 'None', 
		hierarchyTwo: 'None'}
	])
	
	// This function will handle changes in the constraint entry fields
	const handleConstraintChange = (event, index) => {
		const { name, value } = event.target;
		const constraintsTemp = [...constraints];
		constraintsTemp[index][name] = value;
		setConstraints(constraintsTemp);
	};

	const handleConstraintDelete = (index) => {
		const constraintsTemp = [...constraints]
		constraintsTemp.splice(index, 1)
		setConstraints(constraintsTemp)
	};

	// This function will add the constraint entry field
	const handleConstraintAdd = () => {
		setConstraints([...constraints, { hierarchyOne: 'None', inequality: 'None', values: 'None', operator: 'None', hierarchyTwo: 'None'}])
	}

	// This variable will pass in table and form information to Table page on submit
	const navigate = useNavigate();

	// This variable is for datagrid pro 
	const getTreeDataPath = (row) => row.hierarchy;

	// Redo because redo array will append only ones that are undo-ed.
	const [redo, setRedo] = useState([]);
	const [undo, setUndo] = useState([row_values]);

	// Rows and Columns are initialized with the values from the Create Component
	const [rows, setRows] = useState(row_values);
	const [columns, setColumns] = useState(column_values);

	// These two variables keep track of the editted rows 
	const [editRowsModel, setEditRowsModel] = useState({});
    const [editRowData, setEditRowData] = useState({});

	// This is for designing datagrid component below
	const useStyles = makeStyles((theme) =>
		createStyles({
			root: {
				'.MuiDataGrid-columnSeparator': {
					display: 'none',
				},
				'& .super-app-theme--cell': {
					backgroundColor: 'rgb(233, 233, 231)',
				},
				'& div[aria-rowindex]' : {
					fontFamily: 'Georgia, serif',
					fontSize: 12
				}
			}
		})
	);
	const classes = useStyles();

	// This function will reaggregate the budget along the hierarchy
    const handleEditRowsModelChange = useCallback((model) => {
        const editedIds = Object.keys(model);
        const apiRef_map = apiRef.current.getRowModels()
		setFormula('')
		if (editedIds.length === 0) {
			
            const apiRef_values =  Array.from(apiRef_map.values())
            axios.post('/reaggregate',  JSON.stringify({state: {editRowsModel, editRowData, apiRef_values, combinedForm}}), {
                headers: {
                	'Content-Type':'application/json'
                },
            }).then((res) => {
				// add reaggregated budget to the undo array
                const newUndoList = undo.concat({...res.data})
				setUndo(newUndoList);
				setRows(res.data);
				// All redo action disappear like that of Word Documents
				setRedo([]);
            });
        } else {
            setEditRowData(model[editedIds[0]]);
        }
		setEditRowsModel(model);
	},[apiRef, editRowData, editRowsModel, undo, combinedForm]);

	// This function is connected to Save Button in the Table Page. When
	// When clicked, budget data will be saved (graph database)
	const handleSave = () => {
		const apiRef_v = apiRef.current.getRowModels()
		const apiRef_values =  Array.from(apiRef_v.values())
		console.log(userName)
		if (!viewBoolean) {
		console.log(budgetNameView)
			axios.post('/commit',  JSON.stringify({state: {apiRef_values, combinedForm, division, budgetNameEdit, budgetNameView, userName}}), {
				headers: {
				'Content-Type':'application/json'
				}
			}).then((res) => {
				if (res.data[0] === 'fail') {
					alert('Save Aborted Check Your Constraints!')
					// alert("ABORTED! " +
					// 	res.data[1]['hierarchyOne'] + " Should be " +
					// 	res.data[1]['inequality'] + " " +
					// 	res.data[1]['hierarchyTwo'] + " " +
					// 	res.data[1]['operator'] + " " +
					// 	res.data[1]['values'])
					// alert(res.data[1])
				} else {
					alert("Budget Plan Saved!");
					navigate('/plans', res.data);
				}
			});
		} else {
			// handle editted data and commit them
			axios.post('/commitEdittedBudget',  JSON.stringify({state: {apiRef_values, viewVersion, combinedForm, userName}}), {
				headers: {
				'Content-Type':'application/json'
				}
			}).then((res) => {
				if (res.data[0] === 'fail') {
					alert('Save Aborted Check Your Constraints!')

				} else {
					alert("Budget Plan Saved!");
					navigate('/plans');
				}
			});
		}
  	};

	// This function is connected to Undo Button in the Table Page. When clicked,
	// values in the budget plan will reverse the last one. 
	const handleUndo = () => {
		if (undo.length > 1) {
			setRows(Object.values(undo[undo.length - 2]))
			const undoElementPopped = undo.pop()
			const newRedoList = redo.concat({...undoElementPopped})
			setRedo(newRedoList)

		}
  	};

	// This function is connected to Redo Button in the Table Page. When clicked,
	// values in the budget plan will reverse back from what has been undo-ed.
	const handleRedo = () => {
		if (redo.length !== 0) {
			const redoElementPopped = redo.pop(0)
			setRows(Object.values(redoElementPopped))
			const newUndoList = undo.concat({...redoElementPopped})
			setUndo(newUndoList)
		}
	};

	// This will revert the budget plan to its inital state. 
	const handleRevert = () => {
		setColumns(column_values);
		setRows(row_values);
		setUndo([row_values]);
		setRedo([]);
  	};

	const [openDisaggregate, setOpenDisaggregate] = useState(false);
	const handleDisaggregateClose = () => {
		setOpenDisaggregate(false);
		setConstraints([{ hierarchyOne: 'None', inequality: 'None', values: 'None', operator: 'None', hierarchyTwo: 'None'}])
	};

	// This function allows user to write on the form 
	const handleChange = (e) => {
		console.log(form)
		if (e.target !== undefined) {
			const { name, value } = e.target;
			setForm({
				...form,
				[name]:value,
			});
		}
	}
	// This function will disaggregate the budget plan along the hierarchy
	const handleDisaggregate = () => {
		setOpenDisaggregate(true);
		
	}

	const handleDisaggregateSubmit= () => {
		const apiRef_map = apiRef.current.getRowModels()
		const apiRef_values =  Array.from(apiRef_map.values())
		axios.post('/disaggregate',  JSON.stringify({apiRef_values, form, combinedForm, constraints}), {
			headers: {
			'Content-Type':'application/json'
			}
		}).then((res) => {
			// add reaggregated budget to the undo array
			console.log(res.data)
			const newUndoList = undo.concat({...res.data})
			setUndo(newUndoList);
			setRows(res.data);
			// All redo action disappear like that of Word Documents
			setRedo([]);
		})
		setOpenDisaggregate(false)
		setForm(default_dialog_form_inputs)
		setConstraints([{ hierarchyOne: 'None', inequality: 'None', values: 'None', operator: 'None', hierarchyTwo: 'None'}])
	}

	const handleFormula = (event) => {
		const { value } = event.target;
		setFormula(value)
	}

	const handleFormulaChange = (event) => {
		const id_val = event['id'].toString()
		const field_val = event['field'].toString()
		const hierarchyType = row_values[id_val]['hierarchy']
		const hierarchyIdentifier = hierarchyType[hierarchyType.length - 1]
		setFormula(formula + " " + hierarchyIdentifier + field_val)
	}

	const submitFormula = () => {
		console.log(formula)
		const apiRef_v = apiRef.current.getRowModels()
		const apiRef_values =  Array.from(apiRef_v.values())
		axios.post('/formula',  JSON.stringify({formula, apiRef_values}), {
			headers: {
			'Content-Type':'application/json'
			}
		}).then((res) => {
			// add reaggregated budget to the undo array
			console.log(res.data)
			const newUndoList = undo.concat({...res.data})
			setUndo(newUndoList);
			setRows(res.data);
			// All redo action disappear like that of Word Documents
			setRedo([]);
		})
		setFormula("")
	}

	

	return (
		<Main open={open}>
            <DrawerHeader />
				<Tooltip title="Save">
					<Button onClick={handleSave}>Save</Button>
				</Tooltip>
				<Tooltip title="Revert">
					<Button onClick={handleRevert}>Revert</Button>
				</Tooltip>
				<Tooltip title="Undo">
					<Button onClick={handleUndo}>Undo</Button>
				</Tooltip>
				<Tooltip title="Redo">
					<Button onClick={handleRedo}>Redo</Button>
				</Tooltip>
				<Tooltip title="Disaggregate">
					<Button onClick={handleDisaggregate}>Disaggregate</Button>
				</Tooltip>
				<Grid>
					<input type="text"
						name="name"
						value={formula}
						onChange={handleFormula}
						size="60"
						autoComplete='off'
						autoFocus
					/>
					&nbsp;
					<button onClick={submitFormula}>✔️</button>
				</Grid>
				<br/>

				<Dialog sx={{"& .MuiDialog-container": { "& .MuiPaper-root": { width: "100%", maxWidth: "900px"},},}} open={openDisaggregate} onClose={handleDisaggregateClose}>
					<DialogTitle>Disaggregation</DialogTitle>
					<DialogContent>
					<DialogContentText>
						To disaggregate values in this plan, please fill out the required information.
					</DialogContentText>
					&nbsp;
					<TextField
						id="outlined-select-disaggregate"
						select
						fullWidth
						required
						autoComplete = 'off'
						name = 'disaggregateType'
						label="Choose One Disaggregation Method To Use"
						value={form.disaggregateType}
						onChange={handleChange}
						>
						{disaggregateFormula.map((option) => (
							<MenuItem key={option.value} value={option.value}>
							{option.label}
							</MenuItem>
						))}
					</TextField>
						
					<TextField
						autoFocus
						margin="dense"
						id="name1"
						label="Hierarchy Of Interest"
						type="text"
						name = 'hierarchyOfInterest'
						fullWidth
						autoComplete = 'off'
						required
						variant="standard"
						value = {form.hierarchyOfInterest}
						onChange={handleChange}
					/>
					<TextField
						autoFocus
						margin="dense"
						id="name0"
						label="Reference Period"
						type="text"
						name = 'referential'
						fullWidth
						autoComplete = 'off'
						required
						variant="standard"
						value = {form.referential}
						onChange={handleChange}
					/>
					<TextField
						autoFocus
						margin="dense"
						id="name2"
						label="Period Of Interest"
						type="text"
						name='periodOfInterest'
						fullWidth
						required
						autoComplete = 'off'
						variant="standard"
						value = {form.periodOfInterest}
						onChange={handleChange}
					/>
					<TextField
						autoFocus
						margin="dense"
						id="name3"
						label="Hierarchy Total Amount"
						name='amount'
						value={form.amount}
						type="number"
						fullWidth
						required
						autoComplete = 'off'
						variant="standard"
						onChange={handleChange}
					/>
					<TextField
						autoFocus
						margin="dense"
						id="name5"
						label="Lock"
						name='lock'
						value={form.lock}
						type="text"
						fullWidth
						required
						autoComplete = 'off'
						variant="standard"
						onChange={handleChange}
					/>
						&nbsp;
						<Grid item container rowSpacing={2}>
                            {constraints.map((x, i) => {
                                return (
                                    <Grid item container columnSpacing={1} key={i}>
                                        <Grid item xs={2}>	
                                            <TextField
                                                variant = 'outlined'
                                                autoComplete = 'off'
                                                size='small'
                                                label = 'Name1'
                                                name = 'hierarchyOne'
                                                required
                                                fullWidth
                                                value = {x.hierarchyOne}
                                                onChange = {e => handleConstraintChange(e, i)}
                                            />
                                        </Grid>
                                        <Grid item xs={2}>	
                                            <TextField
                                                select={true}
                                                variant = 'outlined'
                                                autoComplete = 'off'
                                                size='small'
                                                label = 'Inequality'
                                                name = 'inequality'
                                                required
                                                fullWidth
                                                value = {x.inequality}
                                                onChange = {e => handleConstraintChange(e, i)}
                                            >
                                                {
                                                    inequality.map((option) => (
                                                    <MenuItem key={option.value} value={option.value}>
                                                        {option.label}
                                                    </MenuItem>))
                                                }
                                            </TextField>
                                        </Grid>
                                        <Grid item xs={2}>	
                                            <TextField
                                                variant = 'outlined'
                                                autoComplete = 'off'
                                                size='small'
                                                label = 'Values'
                                                name = 'values'
                                                required
                                                fullWidth
                                                value = {x.values}
                                                onChange = {e => handleConstraintChange(e, i)}
                                            />
                                        </Grid>
										
										<Grid item xs={2}>	
                                            <TextField
                                                select={true}
                                                variant = 'outlined'
                                                autoComplete = 'off'
                                                size='small'
                                                label = 'Operator'
                                                name = 'operator'
                                                required
                                                fullWidth
                                                value = {x.operator}
                                                onChange = {e => handleConstraintChange(e, i)}
                                            >
                                                {
                                                    operator.map((option) => (
                                                    <MenuItem key={option.value} value={option.value}>
                                                        {option.label}
                                                    </MenuItem>))
                                                }
                                            </TextField>
                                        </Grid>

										<Grid item xs={2}>	
                                            <TextField
                                                variant = 'outlined'
                                                autoComplete = 'off'
                                                size='small'
                                                label = 'Name2'
                                                name = 'hierarchyTwo'
                                                required
                                                fullWidth
                                                value = {x.hierarchyTwo}
                                                onChange = {e => handleConstraintChange(e, i)}
                                            />
                                        </Grid>


                                        <Grid item xs={1}>
                                                {
                                                    constraints.length - 1 === i && <Button onClick={handleConstraintAdd}>+</Button>
                                                }
                                        </Grid>
                                        <Grid item xs={1}>
                                                {
                                                    constraints.length !== 1 && <Button
                                                    onClick={() => handleConstraintDelete(i)}>-</Button>
                                                }
                                            
                                        </Grid>
                                    </Grid>
                                )
                            })}
						</Grid>
					</DialogContent>
						<DialogActions>
						<Button onClick={handleDisaggregateClose}>Cancel</Button>
						<Button onClick={handleDisaggregateSubmit}>Submit</Button>
					</DialogActions>
				</Dialog>

				<div className="mainPage" style={{ height: 500 , width: '90%' }}> 
					<DataGridPro
						treeData
						apiRef={apiRef}
						rowHeight={20}
						headerHeight={30}
						hideFooter={true} // hide the footer block under the table
						className={classes.root} // for style purpose
						rows = {rows}
						columns={columns}
						disableColumnMenu={true} // disable column menu
						getTreeDataPath={getTreeDataPath}
						hideFooterRowCount = {true} // hide footer row count
						groupingColDef={{hideDescendantCount: true, headerName: ' ', width: 250}}
						// defaultGroupingExpansionDepth = {-1} // expand tree rows
						editRowsModel={editRowsModel}
						onEditRowsModelChange={handleEditRowsModelChange}
						onCellClick={handleFormulaChange}
					/>
				</div>
		</Main>
	)
}

export default Table;


