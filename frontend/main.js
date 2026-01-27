// Serves frontend UI and proxies requests to Flask API

const express = require('express');
const axios = require('axios');
const path = require('path');
const packageJson = require('./package.json');
console.log(`Frontend version: ${packageJson.version}`);

const app = express();
const PORT = process.env.PORT || 3000;
const FLASK_API_URL = process.env.FLASK_API_URL || 'http://127.0.0.1:5000';

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// View engine setup
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Routes
app.get('/', (_req, res) => {
    res.render('index', {
        title: 'OWASP LLM Security Demo'
    });
});

app.get('/health', (_req, res) => {
    res.json({
        status: 'healthy',
        service: 'owasp-llm-frontend',
        flask_api: FLASK_API_URL
    });
});

// Proxy endpoint to Flask API
app.post('/api/test', async (req, res) => {
    try {
        const { prompt } = req.body;

        if (!prompt) {
            return res.status(400).json({
                error: 'Missing prompt field'
            });
        }

        console.log(`[API] Testing prompt: "${prompt.substring(0, 50)}..."`);

        // Call Flask API
        const response = await axios.post(`${FLASK_API_URL}/api/test`, {
            prompt: prompt
        }, {
            timeout: 120000 // 2 minutes timeout
        });

        console.log(`[API] Response received - Category: ${response.data.category}`);

        res.json(response.data);

    } catch (error) {
        console.error('[API] Error:', error.message);

        if (error.code === 'ECONNREFUSED') {
            return res.status(503).json({
                error: 'Flask API not available',
                detail: 'Make sure Flask server is running on port 5000'
            });
        }

        if (error.response) {
            return res.status(error.response.status).json(error.response.data);
        }

        res.status(500).json({
            error: 'Internal server error',
            detail: error.message
        });
    }
});


// Version endpoint proxy
app.get('/api/version', async (req, res) => {
    try {
        const response = await axios.get(`${FLASK_API_URL}/api/version`);
        res.json(response.data);
    } catch (error) {
        console.error('Version check error:', error.message);
        res.status(500).json({ error: 'Unable to fetch version' });
    }
});

// 404 handler
app.use((_, res) => {
    res.status(404).json({
        error: 'Not found'
    });
});

// Start server
app.listen(PORT, () => {
    console.log('\nFrontend Server Running');
    console.log(`URL: http://localhost:${PORT}`);
    console.log(`\tFlask API: ${FLASK_API_URL}`);
    console.log(`\tEnvironment: ${process.env.NODE_ENV || 'development'}\n`);
});

