import React from "react";
import { makeStyles, styled } from '@material-ui/core/styles';
import {Badge, Toolbar, Typography, IconButton } from '@mui/material';
import { Notifications, Menu, Mail } from "@mui/icons-material";
import { Avatar } from "@mui/material";
import MuiAppBar from "@mui/material/AppBar";

const useStyles = makeStyles((theme) => ({
    logoLg: {
        display: 'none',
        [theme.breakpoints.up('sm')]: {
            display: 'block',
        }
    },
    logoSm: {
        display: 'block',
        [theme.breakpoints.up('sm')]: {
            display: 'none',
        }
    },
    toolbar: {
        display: 'flex',
        justifyContent: 'space-between'
    },
    icons: {
        display: 'flex',
        alignItems: 'center'
    },
    badge: {
        marginRight: theme.spacing(2),
        cursor: 'pointer'
    },
    togglebar: {
        color: "inherit",
    },
}))

const drawerWidth = 200;
const AppBar = styled(MuiAppBar, {
    shouldForwardProp: (prop) => prop !== "open"
  })(({ theme, open }) => ({
    transition: theme.transitions.create(["margin", "width"], {
      easing: theme.transitions.easing.sharp,
      duration: theme.transitions.duration.leavingScreen
    }),
    ...(open && {
      width: `calc(100% - ${drawerWidth}px)`,
      transition: theme.transitions.create(["margin", "width"], {
        easing: theme.transitions.easing.easeOut,
        duration: theme.transitions.duration.enteringScreen
      }),
      marginRight: drawerWidth
    })
  }));

const Navbar = ({open, setOpen}) => {
    
    const handleDrawer = () => {
        setOpen(!open);
    };

    // const [openAvatar, setOpenAvatar] = useState(false);

    const classes = useStyles()
    return (
        <AppBar className={classes.appbar} position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
            <Toolbar className={classes.toolbar}>
                <Typography variant='h6' className={classes.logoLg}>
                <IconButton className={classes.togglebar} onClick={handleDrawer} edge="start" sx={{ mr: 2}}><Menu /></IconButton>
                    Budget Planning Application
                </Typography>
                <Typography variant='h6' className={classes.logoSm}>
                <IconButton className={classes.togglebar} onClick={handleDrawer} edge="start" sx={{ mr: 2}}><Menu /></IconButton>
                    BPA
                </Typography>
                <div className={classes.icons}>
                    <Badge anchorOrigin={{ vertical: 'top', horizontal: 'right' }} badgeContent={2} max={9} overlap="rectangular" color='error' className={classes.badge}>
                        <Mail/>
                    </Badge>
                    <Badge anchorOrigin={{ vertical: 'top', horizontal: 'right' }} badgeContent={2} max={9} overlap="rectangular" color='error' className={classes.badge}>
                        <Notifications/>
                    </Badge>
                    <Avatar className={classes.badge} alt='Spongebob' src='data:image/png;base64,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'></Avatar>
                </div>
            </Toolbar>
        </AppBar>
    );
}

export default Navbar;
