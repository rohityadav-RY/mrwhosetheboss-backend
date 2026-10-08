# Mrwhosetheboss Community Backend

A small Python standard-library backend for the OSPC community form. It accepts the fields already used by the frontend and stores submissions in `submissions.json`.

## Requirements

- Python 3.10+
- No external Python packages

## Run locally

From this folder:

```bash
python app.py
```

The API will run on `http://localhost:8000`.

Health check:

```text
GET http://localhost:8000/health
```

Form endpoint:

```text
POST http://localhost:8000/submit
```

Example JSON:

```json
{
  "name": "Rohit",
  "email": "rohit@example.com",
  "category": "AI",
  "message": "I love the future technology videos."
}
```

## Frontend connection

In `js/script.js`, replace the simulated `submitToBackend()` function with a `fetch()` call to your deployed backend URL:

```js
function submitToBackend(formData) {
  return fetch("https://YOUR-BACKEND-URL/submit", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(formData)
  }).then((response) => ({ ok: response.ok }));
}
```

For local testing, use `http://localhost:8000/submit`.

## CORS

The backend currently allows cross-origin requests so GitHub Pages can call it. After deployment, set the `ALLOWED_ORIGIN` environment variable to your exact GitHub Pages origin for tighter security.

## Deployment

This server reads the hosting platform's `PORT` environment variable and binds to `0.0.0.0`, so it can run as a simple Python web service on a host that supports long-running Python processes. Use the start command:

```bash
python app.py
```

Keep `submissions.json` writable on the chosen host. Some serverless/static platforms do not provide persistent local disk storage; if the host has ephemeral storage, use a database instead.
