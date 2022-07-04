import { makeStyles, styled } from '@material-ui/core';
import React from 'react'
import {Typography} from '@mui/material';

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

const useStyles = makeStyles((theme) => ({
    header: {
        paddingLeft: 30,
    },
}))


const Settings = ({open}) => {
	const classes = useStyles();
	return (
        <Main open={open}>
            <DrawerHeader />
            <Typography variant='h5' className={classes.header}>
                Settings
            </Typography>
        </Main>
	)
}

export default Settings