# Frontend

Node.js + Express server with EJS templates.

## Setup
```bash
cd frontend
npm install
npm start
```

Opens at http://localhost:3000

## Structure

| File | Purpose |
|------|---------|
| main.js | Express server, proxies to Flask API |
| views/index.ejs | HTML template |
| public/css/style.css | Styles |
| public/js/form-handler.js | Form logic, API calls |

## Flow
```
User → form-handler.js → main.js → Flask API :5000
```

