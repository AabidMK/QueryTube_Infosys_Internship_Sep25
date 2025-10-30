# frontend

This directory contains the web-based user interface component for QueryTube's semantic video search system.

- **index1.html**: The main HTML file for the frontend, providing a browser-based form for users to submit search queries and view search results for YouTube videos.

**Usage**:
- The frontend is served automatically when the Flask backend is started (see `ai_app.py` within the Python modules directory).
- Users interact by entering natural language queries into the UI. These are sent as requests to the backend `/search` API endpoint, which returns relevant video results based on semantic similarity.
- The interface is designed to simplify the process of querying and reviewing YouTube content indexed by QueryTube workflows.
