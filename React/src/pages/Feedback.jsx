import React from 'react'
import emailjs from "emailjs-com";
import { makeStyles, styled } from '@material-ui/core';
import { Button, Grid, TextField, Typography } from '@mui/material';


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
    feedbackForm: {
        padding: 30,
    },
    button: {
        paddingLeft: 30,
    }
}))


const Feedback = ({open}) => {

    function sendEmail(e) {
        e.preventDefault();
        emailjs.sendForm('budget', 'template_9zoufue', e.target, 'ejbS80IfOW-ZKH6lN')
        .then((result) => {
            console.log(result.text);
        }, (error) => {
            console.log(error.text);
        });
        e.target.reset()
    }

    const classes = useStyles();
	return (
        <Main open={open}>
            <DrawerHeader />
                <Typography variant='h6' className={classes.header}>
                    Send us feedback!
                </Typography>
                <form onSubmit={sendEmail} className={classes.feedbackForm} id='myform'>
                <Grid container direction={"column"} spacing={2}>
                    <Grid item>
                        <TextField
                            variant = 'outlined'
                            autoComplete = 'off'
                            size='small'
                            label = 'Your Name'
                            name = 'name'
                            required
                            fullWidth
                        />
                    </Grid>
                    <Grid item>
                        <TextField
                            variant = 'outlined'
                            autoComplete = 'off'
                            size='small'
                            label = 'Email Address'
                            name = 'email'
                            required
                            fullWidth
                        />
                    </Grid>
                    <Grid item>
                        <TextField
                            variant = 'outlined'
                            autoComplete = 'off'
                            size='small'
                            label = 'Subject'
                            name = 'subject'
                            required
                            fullWidth
                        />
                    </Grid>
                    <Grid item>
                        <TextField
                            multiline
                            variant = 'outlined'
                            autoComplete = 'off'
                            size='small'
                            label = 'Your Message'
                            name = 'message'
                            required
                            fullWidth
                            inputProps={{
                                style: {
                                height: "130px",
                                },
                            }}
                        />
                    </Grid>
                </Grid>
            </form>
            <div className={classes.button}>
                <Button type="submit" form="myform">Submit</Button>
            </div>
        </Main>
	)
}

export default Feedback