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
app.get('/', async (req, res) => {
  res.render('index');
});

app.get('/results', async (req, res) => {
    const domain = req.query.domain;
    if (!domain) {
        return res.status(400).send('Domain is required');
    }

    try {
        const fetch_id = (await (await fetch('http://backend/api/fetch')).json()).get('id');
        if (!fetch_id) {
            return res.status(500).send('Failed to fetch data');
        }
    } catch (error) {
        return res.status(500).json({error: error.message});
    }

    res.render('results', { domain: domain, id: fetch_id });
});

app.get('/api/fetch', async (req, res) => {
    const id = req.query.id;
    if (!id) {
        return res.status(400).json({ error: 'ID is required' });
    }

    try {
        const response = await fetch(`http://backend/api/fetch?id=${id}`);
        if (!response.ok) {
            return res.status(response.status).json({ error: 'Failed to fetch data from backend' });
        }
        const data = await response.json();
        res.json(data);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
