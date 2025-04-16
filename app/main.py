from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.api import router
from app.core.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Restaurant Order API")
app.include_router(router)

@app.get("/", response_class=HTMLResponse)
def home_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Restaurant API - Home</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f9;
                color: #333;
            }
            header {
                background-color: #4CAF50;
                color: white;
                padding: 1rem;
                text-align: center;
            }
            main {
                padding: 2rem;
            }
            ul {
                list-style-type: none;
                padding: 0;
            }
            li {
                margin: 1rem 0;
            }
            a {
                text-decoration: none;
                color: #4CAF50;
                font-weight: bold;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <header>
            <h1>Welcome to the Restaurant API</h1>
        </header>
        <main>
            <h2>Quick Links</h2>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
            </ul>
        </main>
    </body>
    </html>
    """
