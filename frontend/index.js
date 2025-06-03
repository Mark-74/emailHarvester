const express = require('express');
const path = require('path');
const dotenv = require('dotenv');
dotenv.config();

const app = express();
const PORT = process.env.PORT || 3000;

// express settings
app.use(express.static(path.join(__dirname, 'static')));
app.set('view engine', 'ejs');
app.use(express.json());

// static files
app.use('/bootstrap', express.static(path.join(__dirname, 'node_modules/bootstrap/dist')));
app.use('/bootstrap-icons', express.static(path.join(__dirname, 'node_modules/bootstrap-icons')));
app.set('views', path.join(__dirname, 'templates'));

// routes
app.get('/', (req, res) => {
  res.render('index');
});

app.get('/results', (req, res) => {
    const domain = req.query.domain;
    
    res.render('results', { domain: domain });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
