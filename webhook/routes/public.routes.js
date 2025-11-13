const express = require('express');

const router = express.Router();
const path = require('path');

router.get('/login',(req,res)=>{
    res.sendFile(path.join(__dirname,"..","public","login.html"))
});

router.get('/game/crash',(req,res)=>{
    res.sendFile(path.join(__dirname,"..","public","crash_game.html"));
})

module.exports = router;