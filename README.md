# Restaurant API

This is a RESTful API for managing a restaurant's operations, including tables, menu, orders, kitchen, and more. The API is built using FastAPI and is ready for deployment on Vercel.

## Features

-   Manage tables, menu items, and orders.
-   Track kitchen orders and inventory.
-   Generate reports and handle bills.
-   Health check and database status endpoints.

## Requirements

-   Python 3.9+
-   PostgreSQL database

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/restaurant-api.git
    cd restaurant-api
    ```

2. Create a virtual environment and activate it:

    ```bash
    python -m venv venv
    source venv/bin/activate # On Windows: venv\Scripts\activate
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

4. Set up the database:

    - Create a PostgreSQL database.
    - Update the database connection string in `app/core/config.py`.
    - Initialize the database:
        ```bash
        python init_db.py
        ```

5. Run the application locally:

    ```bash
    uvicorn app.main:app --reload
    ```

6. Access the API documentation at `http://127.0.0.1:8000/docs`.

## Deployment

This project is configured for deployment on Vercel. To deploy:

1. Install the Vercel CLI:

    ```bash
    npm install -g vercel
    ```

2. Deploy the project:
    ```bash
    vercel
    ```

## File Structure

```
restaurant-api/
├── app/
│   ├── api/                # API endpoints
│   ├── core/               # Core configurations and database setup
│   ├── crud/               # CRUD operations
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── main.py             # Application entry point
├── database.sql            # SQL script for database setup
├── init_db.py              # Script to initialize the database
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel configuration
└── README.md               # Project documentation
```

## License

This project is licensed under the MIT License.
