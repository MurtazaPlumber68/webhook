A Flask-based webhook receiver and processor that listens for GitHub repository events, parses them into a standardized schema, and persists them in MongoDB. This service serves as the backend for tracking “push”, “pull request” and “merge” actions from your action-repo, making the raw GitHub payloads available for downstream UIs or analytics tools.

Key Features
Flask endpoint at /webhook that handles POST requests from GitHub

Event parsing to extract:

author (actor login)

action (push, pull_request, merge)

from_branch and to_branch

timestamp (ISO-formatted UTC datetime)

MongoDB integration via PyMongo, storing each event in the events collection

Configurable via a .env file (for MONGO_URI, FLASK_ENV, SECRET_KEY)

Lightweight API endpoint (/api/events/latest) returning the most recent events in human-readable format
