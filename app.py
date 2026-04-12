from __future__ import annotations

import json
from pathlib import Path
from threading import Lock
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "cars.json"
DATA_LOCK = Lock()

DEFAULT_CARS = [
    {
        "id": 1,
        "make": "Toyota",
        "model": "RAV4",
        "year": 2022,
        "price": 28500.0,
        "category": "SUV",
        "color": "Silver",
        "mileage": 21500,
        "available": True,
        "description": "Fuel-efficient compact SUV with a clean service record.",
    },
    {
        "id": 2,
        "make": "Honda",
        "model": "Civic",
        "year": 2021,
        "price": 21990.0,
        "category": "Sedan",
        "color": "Blue",
        "mileage": 30200,
        "available": True,
        "description": "Reliable sedan with lane assist and a reverse camera.",
    },
    {
        "id": 3,
        "make": "Ford",
        "model": "Ranger",
        "year": 2020,
        "price": 31850.0,
        "category": "Truck",
        "color": "Black",
        "mileage": 41200,
        "available": False,
        "description": "Double-cab pickup currently reserved by a buyer.",
    },
]


class CarBase(BaseModel):
    make: str = Field(..., min_length=2, max_length=50)
    model: str = Field(..., min_length=1, max_length=50)
    year: int = Field(..., ge=1900, le=2100)
    price: float = Field(..., gt=0)
    category: str = Field(..., min_length=2, max_length=30)
    color: str = Field(..., min_length=2, max_length=30)
    mileage: int = Field(..., ge=0)
    available: bool = True
    description: str = Field(..., min_length=10, max_length=300)


class CarCreate(CarBase):
    pass


class CarUpdate(CarBase):
    pass


class CarPatch(BaseModel):
    make: str | None = Field(default=None, min_length=2, max_length=50)
    model: str | None = Field(default=None, min_length=1, max_length=50)
    year: int | None = Field(default=None, ge=1900, le=2100)
    price: float | None = Field(default=None, gt=0)
    category: str | None = Field(default=None, min_length=2, max_length=30)
    color: str | None = Field(default=None, min_length=2, max_length=30)
    mileage: int | None = Field(default=None, ge=0)
    available: bool | None = None
    description: str | None = Field(default=None, min_length=10, max_length=300)


class Car(CarBase):
    id: int


def ensure_data_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        DATA_FILE.write_text(json.dumps(DEFAULT_CARS, indent=2), encoding="utf-8")


def load_cars() -> list[dict[str, Any]]:
    ensure_data_file()
    with DATA_LOCK:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def save_cars(cars: list[dict[str, Any]]) -> None:
    with DATA_LOCK:
        DATA_FILE.write_text(json.dumps(cars, indent=2), encoding="utf-8")


def find_car(cars: list[dict[str, Any]], car_id: int) -> tuple[int, dict[str, Any]]:
    for index, car in enumerate(cars):
        if car["id"] == car_id:
            return index, car
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")


app = FastAPI(
    title="Cars For Sale API",
    description="A small FastAPI project that stores its inventory in a JSON file.",
    version="0.1.0",
)


@app.on_event("startup")
def startup() -> None:
    ensure_data_file()


@app.get("/")
def read_root() -> dict[str, str]:
    return {
        "message": "Cars For Sale API is running.",
        "docs": "/docs",
    }


@app.get("/cars", response_model=list[Car])
def list_cars(
    available_only: bool = Query(default=False),
    category: str | None = Query(default=None, min_length=2, max_length=30),
) -> list[dict[str, Any]]:
    cars = load_cars()
    filtered_cars = cars

    if available_only:
        filtered_cars = [car for car in filtered_cars if car["available"]]

    if category:
        normalized_category = category.strip().lower()
        filtered_cars = [
            car for car in filtered_cars if car["category"].strip().lower() == normalized_category
        ]

    return filtered_cars


@app.get("/cars/{car_id}", response_model=Car)
def get_car(car_id: int) -> dict[str, Any]:
    _, car = find_car(load_cars(), car_id)
    return car


@app.post("/cars", response_model=Car, status_code=status.HTTP_201_CREATED)
def create_car(payload: CarCreate) -> dict[str, Any]:
    cars = load_cars()
    next_id = max((car["id"] for car in cars), default=0) + 1
    new_car = {"id": next_id, **payload.model_dump()}
    cars.append(new_car)
    save_cars(cars)
    return new_car


@app.put("/cars/{car_id}", response_model=Car)
def replace_car(car_id: int, payload: CarUpdate) -> dict[str, Any]:
    cars = load_cars()
    index, _ = find_car(cars, car_id)
    updated_car = {"id": car_id, **payload.model_dump()}
    cars[index] = updated_car
    save_cars(cars)
    return updated_car


@app.patch("/cars/{car_id}", response_model=Car)
def update_car(car_id: int, payload: CarPatch) -> dict[str, Any]:
    cars = load_cars()
    index, current_car = find_car(cars, car_id)
    updated_fields = payload.model_dump(exclude_unset=True)
    cars[index] = {**current_car, **updated_fields}
    save_cars(cars)
    return cars[index]


@app.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(car_id: int) -> Response:
    cars = load_cars()
    index, _ = find_car(cars, car_id)
    cars.pop(index)
    save_cars(cars)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/categories")
def list_categories() -> list[dict[str, Any]]:
    cars = load_cars()
    category_map: dict[str, dict[str, Any]] = {}

    for car in cars:
        category_name = car["category"]
        if category_name not in category_map:
            category_map[category_name] = {
                "name": category_name,
                "total_cars": 0,
                "available_cars": 0,
            }

        category_map[category_name]["total_cars"] += 1
        if car["available"]:
            category_map[category_name]["available_cars"] += 1

    return sorted(category_map.values(), key=lambda item: item["name"].lower())
