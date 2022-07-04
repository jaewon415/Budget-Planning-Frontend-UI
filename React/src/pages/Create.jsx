import React, {useState,Fragment, useEffect} from 'react'
import axios from 'axios';
import { Button, TextField, Grid, MenuItem, Box, 
    Select, OutlinedInput, Chip} from '@mui/material';
import AdapterDateFns from '@mui/lab/AdapterDateFns';
import { useNavigate } from 'react-router-dom';
import { Typography } from '@mui/material';
import { makeStyles, styled, useTheme } from '@material-ui/core';
import { DateRangePicker, LocalizationProvider} from '@mui/x-date-pickers-pro'


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



const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

  
function getStyles(name, budgetName, theme) {
    return {
        fontWeight:
        budgetName.indexOf(name) === -1
            ? theme.typography.fontWeightRegular
            : theme.typography.fontWeightMedium,
    };
}

const useStyles = makeStyles((theme) => ({
    form: {
        padding: 30,
    },
    header: {
        paddingLeft: 30,
    },
    subHeader: {
        fontSize: 15,
        paddingLeft: 5,
    }
}))

// This variable takes default values of the form
const default_create_form_inputs = {
	plan_name: '',
	plan_date: [null, null], plan_base_period: '',
	plan_constraints: 'None',
	plan_description: '',
}

// This variable base periods of how budget plan should be dividded
const periods = [
	{ value: 'Monthly', label: 'Monthly' },
	{ value: 'Quarterly', label: 'Quarterly' },
	{ value: 'Yearly', label: 'Yearly' },
];

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

const Create = ({open, division, userName}) => {

    const theme = useTheme();
    const [names, setNames] = React.useState([]);
    const [namesHierarchy, setNamesHierarchy] = React.useState([]);
    const [budgetNameRollup, setBudgetNameRollup] = React.useState([]);
    const [budgetNameEdit, setBudgetNameEdit] = React.useState([]);
    const [budgetNameView, setBudgetNameView] = React.useState([]);

    useEffect(() => {
        // console.log(userName)
        axios.post('/getCreateRollupPlans',  JSON.stringify({division}), {
			headers: {
				'Content-Type':'application/json'
			},
		}).then((res) => {
            setNames(res.data)
        })
    }, [division]);

    useEffect(() => {
        axios.post('/editViewCreatePlans',  JSON.stringify({division}), {
			headers: {
				'Content-Type':'application/json'
			},
		}).then((res) => {
            setNamesHierarchy(res.data)
        })
    }, [division]);

    const handleMultipleSelectChangeRollup = (event) => {
        const {
        target: { value },
        } = event;
        setBudgetNameRollup(
        // On autofill we get a stringified value.
        typeof value === 'string' ? value.split(',') : value,
        );
    };

    const handleMultipleSelectChangeView = (event) => {
        const {
        target: { value },
        } = event;
        setBudgetNameView(
        // On autofill we get a stringified value.
        typeof value === 'string' ? value.split(',') : value,
        );
    };

    const handleMultipleSelectChangeEdit = (event) => {
        const {
        target: { value },
        } = event;
        setBudgetNameEdit(
        // On autofill we get a stringified value.
        typeof value === 'string' ? value.split(',') : value,
        );
    };
    
	// This variable store default values of the form
	const [form, setForm] = useState(default_create_form_inputs);
	// This variable will pass in table and form information to Table page on submit
	const navigate = useNavigate();

	// Checks if there is an attribute called target 
	// This function will differentiate date and other elements
	const handleChange = (e) => {
		if (e.target !== undefined) {
			const { name, value } = e.target;
			setForm({
				...form,
				[name]:value,
			});
		} else {
			// For date range picker in the form
			if (e.every(element => element !== null)) {
				setForm({
					...form,
					plan_date: [e[0], e[1]]
				});
			}
		}
    };

	// This variable is for storing constraint values 
	const [constraints, setConstraints] = useState([{ hierarchyOne: 'None', inequality: 'None', values: 'None', operator: 'None', hierarchyTwo: 'None'}])
	
	// This function will handle changes in the constraint entry fields
	const handleConstraintChange = (event, index) => {
		const { name, value } = event.target;
		const constraintsTemp = [...constraints];
		constraintsTemp[index][name] = value;
		setConstraints(constraintsTemp);
	};

	// This function will delete the constraint entry field
	const handleConstraintDelete = (index) => {
		const constraintsTemp = [...constraints]
		constraintsTemp.splice(index, 1)
		setConstraints(constraintsTemp)
	};

	// This function will add the constraint entry field
	const handleConstraintAdd = () => {
		setConstraints([...constraints, { hierarchyOne: '', inequality: '', values: '', hierarchyTwo: ''}])
	}

	// This function will take the form values and pass them to python to grab table data
	const handleSubmit = (e) => {
		e.preventDefault();
		const combinedForm = {...form, ...{plan_constraints: constraints}, plan_created: new Date().toLocaleString() + ''}

		// axios.post('/create',  JSON.stringify({combinedForm}), {
		axios.post('/create',  JSON.stringify({combinedForm, budgetNameRollup}), {
		    headers: {
		        'Content-Type':'application/json'
		    },
		})
        .then((res) => {
            // console.log('here')
            // console.log(userName)
            // console.log(division)
            // console.log(combinedForm)
            // console.log(budgetNameEdit)
            // console.log(budgetNameView)
			navigate('/table', {state: {data: [...res.data], combinedForm: combinedForm, division: division,  budgetNameEdit: budgetNameEdit,budgetNameView: budgetNameView, userName: userName}})
		})
	};

    const classes = useStyles();
  	return (
        <Main open={open}>
            <DrawerHeader />

            <Typography variant='h6' className={classes.header}>
                Create Budget Plan
            </Typography>
            <div className={classes.form}>
                <form onSubmit={handleSubmit} id="myform">
                    <Grid container direction={"column"} spacing={2}>
                        <Grid item>
                            <TextField
                                variant = 'outlined'
                                autoComplete = 'off'
                                size='small'
                                label = 'Name of the Plan'
                                name = 'plan_name'
                                required
                                fullWidth
                                value = {form.plan_name}
                                onChange = {handleChange}
                            />
                        </Grid>
                        <Grid item>
                        <LocalizationProvider dateAdapter={AdapterDateFns}>
                            <DateRangePicker
                                startText="Start-of-Plan"
                                endText="End-of-Plan"
                                value={form.plan_date}
                                onChange={handleChange}
                                renderInput={(startProps, endProps) => (
                                <Fragment>
                                    <TextField fullWidth size = 'small' autoComplete = 'off' required {...startProps} />
                                    <Box sx={{ mx: 2 }}> to </Box>
                                    <TextField fullWidth size = 'small'  autoComplete = 'off' required {...endProps} />
                                </Fragment>
                                )}
                            />
                            </LocalizationProvider>
                        </Grid>

                        <Grid item>
                            <TextField
                                select={true}
                                name = 'plan_base_period'
                                label = 'Base Planning Period'
                                required={true}
                                fullWidth={true}
                                size='small'
                                value={form.plan_base_period}
                                onChange={handleChange}>
                                {periods.map((option) => (
                                    <MenuItem key={option.value} value={option.value}>
                                        {option.label}
                                    </MenuItem>
                                ))}
                            </TextField>
                        </Grid>

                        <Grid item>
                            <Typography className={classes.subHeader}>
                                <u><em>Select plans to roll up:</em></u>
                            </Typography>
                        </Grid>
                        <Grid item>
                            <Select
                            labelId="demo-multiple-chip-label"
                            id="demo-multiple-chip"
                            multiple
                            fullWidth
                            value={budgetNameRollup}
                            onChange={handleMultipleSelectChangeRollup}
                            input={<OutlinedInput id="select-multiple-chip"/>}
                            renderValue={(selected) => (
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                {selected.map((value) => (
                                    <Chip key={value} label={value} />
                                ))}
                                </Box>
                            )}
                            MenuProps={MenuProps}
                            >
                            {names.map((name, i) => (
                                <MenuItem
                                key={i}
                                value={name}
                                style={getStyles(name, budgetNameRollup, theme)}
                                >
                                {name}
                                </MenuItem>
                            ))}
                            </Select>
                        </Grid>

                        <Grid item>
                            <Typography className={classes.subHeader}>
                                <u><em>Add constraints:</em></u>
                            </Typography>
                        </Grid>    
                            {constraints.map((x, i) => {
                                return (
                                    <Grid item container spacing={2} key={i}>
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
                                                defaultValue = {'None'}
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
                        <Grid item>
                            <Typography className={classes.subHeader}>
                                <u><em>Plan View Access:</em></u>
                            </Typography>
                        </Grid>
                        <Grid item>
                            <Select
                            labelId="demo-multiple-chip-label"
                            id="demo-multiple-chip"
                            multiple
                            fullWidth
                            value={budgetNameView}
                            onChange={handleMultipleSelectChangeView}
                            input={<OutlinedInput id="select-multiple-chip"/>}
                            renderValue={(selected) => (
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                {selected.map((value) => (
                                    <Chip key={value} label={value} />
                                ))}
                                </Box>
                            )}
                            MenuProps={MenuProps}
                            >
                            {namesHierarchy.map((name) => (
                                <MenuItem
                                key={name}
                                value={name}
                                style={getStyles(name, budgetNameView, theme)}
                                >
                                {name}
                                </MenuItem>
                            ))}
                            </Select>
                        </Grid>
                        
                        <Grid item>
                            <Typography className={classes.subHeader}>
                                <u><em>Plan Edit Access:</em></u>
                            </Typography>
                        </Grid>
                        <Grid item>
                            <Select
                            labelId="demo-multiple-chip-label"
                            id="demo-multiple-chip"
                            multiple
                            fullWidth
                            value={budgetNameEdit}
                            onChange={handleMultipleSelectChangeEdit}
                            input={<OutlinedInput id="select-multiple-chip"/>}
                            renderValue={(selected) => (
                                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                {selected.map((value) => (
                                    <Chip key={value} label={value} />
                                ))}
                                </Box>
                            )}
                            MenuProps={MenuProps}
                            >
                            {namesHierarchy.map((name) => (
                                <MenuItem
                                key={name}
                                value={name}
                                style={getStyles(name, budgetNameEdit, theme)}
                                >
                                {name}
                                </MenuItem>
                            ))}
                            </Select>
                        </Grid>
                        <Grid item>
                            <TextField
                                multiline
                                variant = 'outlined'
                                autoComplete = 'off'
                                label = 'Description of the Plan'
                                name = 'plan_description'
                                required
                                fullWidth
                                value = {form.plan_description}
                                onChange = {handleChange}
                                inputProps={{
                                    style: {
                                    height: "130px",
                                    },
                                }}
                            />
                        </Grid>
                    </Grid>
                </form>
                <Button type="submit" form="myform">Submit</Button>
            </div>
        </Main>
  	)
}

export default Create
