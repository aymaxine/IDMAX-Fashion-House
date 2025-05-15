# IDMAX Fashion Catalog Flask Application

A database-driven Flask web application that displays fashion product data from an open source dataset. This application is developed as part of a programming assignment to demonstrate skills in developing web applications with Flask.

## Features

- Browse a catalog of fashion products
- Filter products by gender, brand, color, and price range
- View detailed product information
- Explore fashion brands and their statistics
- View analytics on products, colors, and brands

## Technology Stack

- **Flask**: Python web framework
- **SQLAlchemy**: ORM for database interaction
- **SQLite**: Database (development)
- **PostgreSQL**: Database (production on Render)
- **Flask-Migrate**: Database migration management
- **Pandas**: Data processing for import

## Installation and Setup

### Prerequisites

- Python 3.8+
- Pip package manager

### Local Development Setup

1. Clone the repository:
bash
git clone https://github.com/yourusername/fashion-catalog.git
cd fashion-catalog

2. Create and activate a virtual environment:
bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install required packages:
bash
pip install -r requirements.txt

4. Initialize the database:
bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

5. Load data from the CSV file:
bash
python load_data.py

6. Run the application:
bash
python run.py

7. Access the application in your browser at `http://localhost:5000`

## Testing

Run the test suite with pytest:

```bash
pytest
```

## Project Structure

```
fashion-catalog/
├── app/
│   ├── __init__.py        # Flask application factory
│   ├── handlers.py        # Error handlers
│   ├── models/            # Database models
│   │   └── models.py
│   ├── routes/            # Route blueprints
│   │   ├── brands.py
│   │   ├── main.py
│   │   └── products.py
│   ├── static/            # Static files (CSS, JS, images)
│   │   └── css/
│   │       └── style.css
│   └── templates/         # Jinja2 templates
│       ├── base.html
│       ├── index.html
│       ├── product_detail.html
│       ├── brand_list.html
│       ├── brand_detail.html
│       └── errors/
│           ├── 404.html
│           └── 500.html
├── migrations/           # Database migrations
├── tests/                # Test suite
│   ├── conftest.py
│   ├── test_models.py
│   └── test_routes.py
├── load_data.py          # Data import script
├── manage.py             # Flask-Migrate management
├── requirements.txt      # Project dependencies
├── run.py                # Application entry point
└── README.md             # Project documentation
```

## Deployment to Render

1. Create a new web service on Render.
2. Link your GitHub repository.
3. Configure the following settings:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn run:app`
4. Add the following environment variables:
   - `SECRET_KEY`: A secure random string
   - `DATABASE_URL`: Your PostgreSQL database URL
5. Deploy the application.
6. Access the application at the provided Render URL.

## Maintenance

### Adding New Data

To update the dataset with new products:

1. Update the CSV file with new data.
2. Run the load script:

```bash
python load_data.py
```

### Database Migrations

When changing models:

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

## License

This project uses open data and is developed for educational purposes.

## Author

[Your Name]
