from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
import pandas as pd
import csv
import redis
import asyncio
from geopy.distance import distance as geopy_distance
from geopy.point import Point

router = APIRouter()
data = pd.read_csv('data/cities_canada-usa.tsv', sep='\t')

ca_codes = {}
with open('data/ca_province_codes.csv', mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        code, name = row
        ca_codes[code.strip()] = name.strip()

# Initialize Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

class CitySuggestion(BaseModel):
    name: str
    latitude: float
    longitude: float
    score: float = Field(..., ge=0.0, le=1.0)

class ErrorResponse(BaseModel):
    detail: str

async def fetch_suggestions_from_redis(key: str) -> Optional[List[CitySuggestion]]:
    if redis_client.exists(key):
        cached_data = redis_client.get(key)
        return eval(cached_data.decode())  # Example; ensure security measures here
    return None

async def store_suggestions_in_redis(key: str, suggestions: List[CitySuggestion]):
    redis_client.setex(key, 3600, str(suggestions))

@router.get('/', response_model=dict, responses={
    200: {"description": "Successful response with suggestions.", "model": dict},
    400: {"description": "Invalid input data. Latitude/longitude out of range or bad input.", "model": ErrorResponse},
    422: {"description": "Validation error. Missing or invalid query parameters.", "model": ErrorResponse},
    500: {"description": "Internal server error.", "model": ErrorResponse}
})
async def get_suggestions(
    q: str = Query(..., min_length=1),
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> dict:
    '''
    Returns suggestions for cities based on query term, latitude, and longitude.
    '''
    # Checking ranges of data
    if latitude is not None and not (-90 <= latitude <= 90):
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90 degrees.")
    if longitude is not None and not (-180 <= longitude <= 180):
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180 degrees.")

    try:
        suggestions = []

        # Construct unique key for Redis cache
        key = f"suggestions:{q}:{latitude}:{longitude}"

        # Attempt to fetch from Redis asynchronously
        cached_suggestions = await fetch_suggestions_from_redis(key)

        if cached_suggestions is not None:
            # Use cached suggestions if available
            suggestions = cached_suggestions
        else:
            # Generate suggestions if not cached
            filtered_cities = data[(data['ascii'].str.contains(q, case=False)) & (data['population'] >= 5000)]

            if latitude is not None or longitude is not None:
                # Calculate min and max distances
                min_distance_km = float('inf')
                max_distance_km = 0.0

                for _, city in filtered_cities.iterrows():
                    city_coords = (city['lat'], city['long'])
                    city_point = Point(city_coords)

                    user_coords = (latitude if latitude else city['lat'], longitude if longitude else city['long'])
                    user_point = Point(user_coords)
                    distance_km = geopy_distance(city_point, user_point).km

                    if distance_km < min_distance_km:
                        min_distance_km = distance_km
                    if distance_km > max_distance_km:
                        max_distance_km = distance_km

                # Calculate scores
                for _, city in filtered_cities.iterrows():
                    if not city['lat'] or not city['long']:
                        continue

                    city_coords = (city['lat'], city['long'])
                    city_point = Point(city_coords)

                    user_coords = (latitude if latitude else city['lat'], longitude if longitude else city['long'])
                    user_point = Point(user_coords)
                    distance_km = geopy_distance(city_point, user_point).km

                    if max_distance_km > min_distance_km:
                        score = 1.0 - (distance_km - min_distance_km) / (max_distance_km - min_distance_km)
                    else:
                        score = 1.0

                    # Apply score thresholding
                    if score > 0.9:
                        score = 0.9
                    elif score < 0.1:
                        score = 0.1

                    country = 'Canada' if city['country'] == 'CA' else 'USA'
                    city_province = city['admin1'] if city['country'] == 'US' else ca_codes[city['admin1']]

                    suggestion = {
                        "name": f"{city['name']}, {city_province}, {country}",
                        "latitude": city['lat'],
                        "longitude": city['long'],
                        "score": round(score, 1)
                    }
                    suggestions.append(suggestion)

            else:
                # Handle case where neither latitude nor longitude is provided
                max_population = filtered_cities['population'].max()
                min_population = filtered_cities['population'].min()

                for _, city in filtered_cities.iterrows():
                    if not city['population']:
                        continue

                    if max_population > min_population:
                        score = (city['population'] - min_population) / (max_population - min_population)
                    else:
                        score = 1.0

                    # Apply score thresholding
                    if score > 0.9:
                        score = 0.9
                    elif score < 0.1:
                        score = 0.1

                    country = 'Canada' if city['country'] == 'CA' else 'USA'
                    city_province = city['admin1'] if city['country'] == 'US' else ca_codes[city['admin1']]

                    suggestion = {
                        "name": f"{city['name']}, {city_province}, {country}",
                        "latitude": city['lat'],
                        "longitude": city['long'],
                        "score": round(score, 1)
                    }
                    suggestions.append(suggestion)

            # Store suggestions in Redis cache asynchronously
            await store_suggestions_in_redis(key, suggestions)

        suggestions.sort(key=lambda x: x['score'], reverse=True)

        return {"suggestions": suggestions}

    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid input data. Please check your query parameters.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
