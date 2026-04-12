# FastAPI to Vercel

This project is a small FastAPI API that uses `uv` for project management and stores its car inventory in a local JSON file instead of a database server.

## What the API does

- List cars for sale
- Filter cars by availability and category
- Create a car
- Replace a car with `PUT`
- Partially update a car with `PATCH`
- Delete a car
- List car categories

## Project structure

```text
.
├── app.py
├── data/
│   └── cars.json
├── main.py
├── pyproject.toml
└── uv.lock
```

## Requirements

- Python 3.12+
- `uv`

## Install and run locally

Initialize and install dependencies:

```bash
uv sync
```

Start the development server:

```bash
uv run fastapi dev main.py
```

Open these URLs in your browser:

- API root: `http://127.0.0.1:8000/`
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Example endpoints

List all cars:

```bash
curl http://127.0.0.1:8000/cars
```

List only available SUVs:

```bash
curl "http://127.0.0.1:8000/cars?available_only=true&category=SUV"
```

Create a car:

```bash
curl -X POST http://127.0.0.1:8000/cars \
  -H "Content-Type: application/json" \
  -d '{
    "make": "Mazda",
    "model": "CX-5",
    "year": 2023,
    "price": 33400,
    "category": "SUV",
    "color": "Red",
    "mileage": 9800,
    "available": true,
    "description": "Low-mileage crossover with a premium interior."
  }'
```

Replace a car with `PUT`:

```bash
curl -X PUT http://127.0.0.1:8000/cars/2 \
  -H "Content-Type: application/json" \
  -d '{
    "make": "Honda",
    "model": "Accord",
    "year": 2022,
    "price": 26990,
    "category": "Sedan",
    "color": "White",
    "mileage": 18000,
    "available": true,
    "description": "Upgraded family sedan with excellent fuel economy."
  }'
```

Patch a car:

```bash
curl -X PATCH http://127.0.0.1:8000/cars/1 \
  -H "Content-Type: application/json" \
  -d '{
    "price": 27999,
    "available": false
  }'
```

Delete a car:

```bash
curl -X DELETE http://127.0.0.1:8000/cars/3
```

List categories:

```bash
curl http://127.0.0.1:8000/categories
```

## Notes

- The data layer uses `data/cars.json`.
- File-based storage is simple to work with locally, but it is not a durable production data store.
- For production use, switch to a real database such as Postgres.

## References

- FastAPI documentation: https://fastapi.tiangolo.com/
