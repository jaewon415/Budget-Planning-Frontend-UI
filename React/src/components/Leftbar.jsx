import * as React from 'react';
import { styled } from '@mui/material/styles';
import Drawer from '@mui/material/Drawer';
import { makeStyles } from '@material-ui/core/styles';
import List from '@mui/material/List';
import Divider from '@mui/material/Divider';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';

import {
	Feedback,
	BackupTable,
	ExitToApp,
	Home,
	NoteAdd,
	History,
	Settings,
  } from "@mui/icons-material";

import { Link } from "react-router-dom";

const drawerWidth = 200;

const data = [
	{name: "Home", icon: <Home />, path: '/'},
	{ name: "Create", icon: <NoteAdd />, path: '/create' },
	{ name: "Plans", icon: <BackupTable />, path: '/plans' },
	{ name: "History", icon: <History />, path: '/history' },
	{ name: "Feedback", icon: <Feedback />, path: '/feedback' },
	{ name: "Settings", icon: <Settings />, path: '/settings' },
	{ name: "Logout", icon: <ExitToApp />, path: '/logout' },
  ];

const DrawerHeader = styled("div")(({ theme }) => ({
	display: "flex",
	alignItems: "center",
	padding: theme.spacing(0, 1),
	// necessary for content to be below app bar
	...theme.mixins.toolbar,
	justifyContent: "flex-end"
}));

const useStyles = makeStyles((theme) => ({
    link: {
        textDecoration: 'none',
		color: theme.palette.text.primary,
		// paddingLeft: 25,
	},
	// linkItem: {
	// 	marginTop: 10,
	// }
}))
  
function Leftbar({open}) {
	const classes = useStyles()

	return (
		<Drawer
			sx={{
				width: drawerWidth,
				flexShrink: 0,
				"& .MuiDrawer-paper": {
					width: drawerWidth,
					boxSizing: "border-box"
				}
			}}
			variant="persistent"
			anchor="left"
			open={open}
		> 
		<DrawerHeader></DrawerHeader>
		<Divider />
		<List>
			{data.map((item, index) => (
				<Link to={item.path} className={classes.link} key={index}>
					<ListItem button key={index} className={classes.linkItem}>
						<ListItemIcon>{item.icon}</ListItemIcon>
						<ListItemText primary={item.name} />
					</ListItem>
				</Link>
			))}
		</List>
		</Drawer>
	);
}

export default Leftbar;