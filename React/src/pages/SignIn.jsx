import * as React from 'react';
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import CssBaseline from '@mui/material/CssBaseline';
import TextField from '@mui/material/TextField';
import Link from '@mui/material/Link';
import Grid from '@mui/material/Grid';
import Box from '@mui/material/Box';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import Typography from '@mui/material/Typography';
import Container from '@mui/material/Container';
import { createTheme, ThemeProvider } from '@mui/material/styles';
import axios from 'axios';

function Copyright(props) {
    return (
        <Typography variant="body2" color="text.secondary" align="center" {...props}>
        {'Copyright © '}
        <Link color="inherit">
            Plan Ahead And Prepare
        </Link>{' '}
        {new Date().getFullYear()}
        {'.'}
        </Typography>
    );
}

    const theme = createTheme();

    export default function SignIn(props) {
    const { setAuthType, setDivision, setUserName } = props;


    const handleSubmit = (event) => {
        event.preventDefault();
        const data = new FormData(event.currentTarget);
        axios.post('/signIn',  JSON.stringify({
            email: data.get('email'),
            password: data.get('password')
        }), {
            headers: {
                'Content-Type':'application/json'
            },
        }).then((res) => {
            if (res.data[1] === 'Fail') {
                alert('Wrong Email or Password!')
            } else {
                // setAuthType('page')
                console.log(res.data)
                setDivision(res.data[0])
                setUserName(res.data[2])
                sessionStorage.setItem('division', res.data[0])
                sessionStorage.setItem('userName', res.data[2])
            }
        })
        // document.location.href = '/'
    };

    return (
        <ThemeProvider theme={theme}>
        <Container component="main" maxWidth="xs">
            <CssBaseline />
            <Box
            sx={{
                marginTop: 8,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
            }}
            >
            <Avatar sx={{ m: 1, bgcolor: 'secondary.main' }}>
                <LockOutlinedIcon />
            </Avatar>
            <Typography component="h1" variant="h5">
                Sign in
            </Typography>
            <Box component="form" onSubmit={handleSubmit} noValidate sx={{ mt: 1 }}>
                <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="Email Address"
                name="email"
                //   autoComplete="email"
                autoComplete="off"
                autoFocus
                />
                <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                //   autoComplete="current-password"
                autoComplete="off"
                />
                <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                >
                Sign In
                </Button>
                <Grid container alignItems="center" justifyContent="center">
                <Grid item>
                    <Button
                        onClick={() => setAuthType("signup")}
                        style={{
                        textTransform: "initial",
                        }}
                    >
                        Don't have an account? Sign Up
                    </Button>
                
                </Grid>
                </Grid>
            </Box>
            </Box>
            <Copyright sx={{ mt: 8, mb: 4 }} />
        </Container>
        </ThemeProvider>
    );
}