# Autocomplete Service

This service provides autocomplete suggestions for large cities in the USA and Canada based on given search parameters. It utilizes FastAPI for the API endpoints and integrates with Redis for caching.

## Table of Contents

- [Overview](#overview)
- [How it Works](#how-it-works)
  - [Calculation Process](#calculation-process)
  - [Scoring Thresholding](#scoring-thresholding)
  - [Implementation Details](#implementation-details)
- [Installation](#installation)
- [Usage](#usage)
  - [Running Locally](#running-locally)
  - [Prerequisites](#prerequisites)
  - [Installing Redis Server](#installing-redis-server-for-running-without-docker-or-kubernetes)
  - [Docker](#docker)
  - [Kubernetes (Minikube)](#kubernetes-minikube)
- [API Endpoint](#api-endpoint)
- [Deployment](#deployment)
- [Swagger Docs](#swagger-openapi-documentation)
- [Testing](#testing)
- [Dataset](#dataset)
- [Evaluation](#evaluation)
- [Contributing](#contributing)
- [License](#license)

## Overview

The Autocomplete Service provides suggestions for cities based on a search term (`q`). Optional parameters (`latitude` and `longitude`) can be provided to refine results based on the caller's location. Suggestions are sorted by score, which indicates the confidence level of the match.

## How it Works
### Calculation Process
The autocomplete service utilizes a dataset containing cities in the USA and Canada to provide suggestions based on user queries. The service accepts a search term (q) and optionally, the caller's location (latitude and longitude) to refine suggestions. The core functionalities include:

- <b>Query Handling</b>: The service parses the query string to retrieve search parameters.
- <b>Location Awareness</b>: If provided, the caller's location helps prioritize suggestions based on proximity using geographic coordinates.
- <b>Scoring</b>: Suggestions are scored based on relevance and confidence, represented as a floating-point value between 0 and 1. A score of 1 indicates high confidence in the suggestion's relevance.
- <b>Population-Based Scoring</b>: When latitude and longitude are not provided, suggestions are ordered by population descending to provide relevant options based on city size.

### Scoring Thresholding
To ensure relevant and accurate suggestions, the scoring mechanism includes:

- <b>Proximity Scoring</b>: Uses the Haversine formula to calculate distances between the caller's location and each city's coordinates, influencing the suggestion's score.
- <b>Population Thresholding</b>: Sets a baseline score based on city population when geographic coordinates are unavailable. Cities with higher populations receive higher scores, ensuring more populous areas are prioritized in suggestions.

### Implementation Details
The service is implemented in Python using FastAPI for handling HTTP requests and responses. It integrates with Redis for caching and Kubernetes for scalable deployment. Tests are implemented using pytest to validate functionality and edge cases.

## Installation

1. Clone the repository:
    
    SSH
    ```bash
    git clone git@github.com:barrylee111/buzzsolutions.git
    cd autocomplete_service
    ```
    HTTPS
    ```bash
    git clone https://github.com:barrylee111/buzzsolutions.git
    cd autocomplete_service
    ```

2. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

3. Create an `.env` with the following vars:
    ```
    PYTHONPATH=$PWD
    FASTAPI_URL=http://localhost:2345/suggestions
    ```
    This is only used for running the tests locally without Docker or Kubernetes.

## Usage
### Running Locally
1. Start the FastAPI application:

    ```bash
    uvicorn autocomplete_service.server:app --host 0.0.0.0 --port 2345
    ```

2. Access the API at:

    ```bash
    http://localhost:2345/suggestions?q=London&latitude=43.70011&longitude=-79.4163
    ```

### Prerequisites:
- Python 3.12.4 or higher installed
- Redis Server installed and running
- k8s installed (for Kubernetes deployment)

### Installing Redis Server (for running without Docker or kubernetes):
#### For Debian-based systems:
```bash
sudo apt-get update
sudo apt-get install redis-server
```

#### For macOS (using Homebrew)
```bash
brew install redis
```

### Starting Redis Server
Start Redis Server:
```bash
redis-server
```

### Setting PYTHONPATH on Ubuntu:
If you're running on Ubuntu, set the PYTHONPATH to the current directory:

```bash
export PYTHONPATH=$PWD
```
This ensures that Python can find the necessary modules when running the FastAPI application.

### Docker
#### Build the Docker image and run the container:

```bash
docker build -t autocomplete-service .
docker run -d -p 2345:2345 autocomplete-service
```

#### Access the API at:

```bash
http://localhost:2345/suggestions?q=London&latitude=43.70011&longitude=-79.4163
```

### Kubernetes (Minikube)
If you have not installed `kubectl` or `minikube`, you will need to do so to run the cluster. [Kubernetes Documentation](https://kubernetes.io/docs/tasks/tools/)

#### Deploy to Minikube:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

#### Get the service URL:

```bash
minikube service autocomplete-service
```

#### Access the Kubernetes cluster at:

```bash
<minikube_service_URL>:2345/suggestions?q=London&latitude=43.70011&longitude=-79.4163
```

**Note:** If you encounter issues pulling the Docker image for the Kubernetes build which calls an image from Dockerhub, ensure you are logged in to Docker Hub. You can log in using `docker login` command and entering your credentials. If you do not have a Docker Hub account, you can create one for free at [Docker Hub](https://hub.docker.com/).

## API Endpoint
<b>Endpoint</b>: /suggestions
#### Parameters:
- <b>q</b>: Search term (required)
- <b>latitude, longitude</b>: Optional parameters to refine results based on caller's location
- <b>Response</b>: JSON array of scored city suggestions, sorted by score descending

### Sample Responses
#### Near match
GET /suggestions?q=London&latitude=43.70011&longitude=-79.4163

```json
{
  "suggestions": [
    {
      "name": "London, ON, Canada",
      "latitude": "42.98339",
      "longitude": "-81.23304",
      "score": 0.9
    },
    {
      "name": "London, OH, USA",
      "latitude": "39.88645",
      "longitude": "-83.44825",
      "score": 0.5
    },
    {
      "name": "London, KY, USA",
      "latitude": "37.12898",
      "longitude": "-84.08326",
      "score": 0.5
    },
    {
      "name": "Londontowne, MD, USA",
      "latitude": "38.93345",
      "longitude": "-76.54941",
      "score": 0.3
    }
  ]
}
```

#### No match
GET /suggestions?q=SomeRandomCityInTheMiddleOfNowhere

```json
{
  "suggestions": []
}
```

## Deployment
For production deployment, deploy the application using Docker or Kubernetes and expose the service endpoint.

## Swagger (OpenAPI) Documentation
#### You will find the API documentation running at:
```
http://localhost:2345/docs
```

## Testing
#### Run tests using pytest:

```bash
pytest tests/test.py
```

Ensure Redis is running before running tests.

## Dataset
The dataset cities_canada-usa.tsv provides city information used for autocomplete suggestions.

## Evaluation
This solution meets the challenge requirements, focusing on:

- Capacity to follow instructions
- Developer experience (ease of setup and usage)
- Solution correctness and performance
- Test quality and coverage
- Code style and cleanliness
- Attention to detail and sensible assumptions

## Contributing
Contributions are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
MIT License