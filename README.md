# **CS411 Final Project**

## **Table of Contents**
1. [Overview](#overview)
2. [Features](#features)
3. [Routes Documentation](#routes-documentation)
4. [Setup Instructions](#setup-instructions)
5. [Testing](#testing)
7. [License](#license)

---

## **Overview**
This project is a web application designed for managing a movie catalog and a personalized watchlist of favorite movies. It enables users to organize, explore, and interact with detailed movie data through an intuitive interface that integrates with the TMDB API. Our application features:
  - A robust backend built using Flask, SQLite, and SQLAlchemy for efficient data storage and retrieval.
  - Integration with the TMDB API to provide detailed and up-to-date movie metadata, such as ratings, genres, descriptions, and more.
  - User management functionalities, including account creation, login, and secure password updates.
  - Comprehensive movie catalog management tools, allowing users to add, delete, and retrieve movies with various filtering and sorting options.
  - A highly interactive watchlist management system for adding, removing, reordering, and playing movies.
  - Dynamic API interactions to fetch movie details, generate leaderboards based on ratings or watch counts, and retrieve personalized recommendations.

Overall, this application serves as a centralized hub for users to maintain and explore their movie collections while offering seamless interaction with external movie databases for highly detailed data.

---

## **Features**
- **User Management**: 
  - Create accounts, login, and securely store passwords using hashing and salting.
  - Update user passwords.
- **Movie Management**: 
  - Add, delete, and view movies in a catalog.
  - Retrieve movies by ID, compound keys, or random selection.
  - Generate leaderboards for movies based on ratings or watch counts.
- **Watchlist Management**: 
  - Add, remove, and clear movies from the watchlist.
  - Reorganize watchlist by moving, swapping, or rewinding movies.
  - Play the current movie, the entire watchlist, or the remainder of the watchlist.
- **API Integration**: 
  - Interacts with the TMDB API for fetching movie data and details.
- **Health Checks**: 
  - Verify application and database connectivity.

---

## **Routes Documentation**

### **Health Checks**
#### Route: `/api/health`
- **Request Type**: `GET`
- **Purpose**: Checks if the application is running.
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json
    {
      "status": "healthy"
    }
 - Example Request:
    ```bash
        curl -X GET http://localhost:5000/api/health
    ```
 - Example Response:
     ```json
     {
          "status": "healthy"
     }

### **Database Check**
#### Route: `/api/db-check`
- **Request Type**: `GET`
- **Purpose**: Verifies database connection and table existence.
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json
    {
      "database_status": "healthy"
    }
  - Error Response Example:
    - Code: 404
    - Content:
    ```json
    {
      "error": "Database not reachable or movies table not found"
    }
 - Example Request:
    ```bash
        curl -X GET http://localhost:5000/api/db-check
    ```
 - Example Response:
     ```json
     {
          "database_status": "healthy"
     }

## **User Management**
### Route: `/api/create-account`
- **Request Type**: `POST`
- **Purpose**: Create a new user account.
- **Request Body**:
  - **username** (String): The username of the user account to create.
  - **password** (String): The password of the user account to create.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 201
    - Content:
    ```json
    {
      "status": "user added",
      "username": "example_user"
    }
 - Example Request:
    ```bash
        curl -X POST http://localhost:5000/api/create-account \
        -H "Content-Type: application/json" \
        -d '{"username": "example_user", "password": "secure_password"}'
    ```
 - Example Response:
     ```json
     {
       "status": "user added", 
       "username": "example_user"
     }

### Route: `/api/login`
- **Request Type**: `POST`
- **Purpose**: Authenticate a user.
- **Request Body**:
  - **username** (String): The username of the user account to create.
  - **password** (String): The password of the user account to create.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json
    {
     "message": "User example_user logged in successfully."
    }
 - Example Request:
    ```bash
        curl -X POST http://localhost:5000/api/login \ 
        -H "Content-Type: application/json" \ 
        -d '{"username": "example_user", "password": "secure_password"}'
    ```
 - Example Response:
     ```json
     {
      "message": "User example_user logged in successfully."
     }

### Route: `/api/update-password`
- **Request Type**: `PUT`
- **Purpose**: Update the password of an existing user.
- **Request Body**:
  - **username** (String): The username of the user account to create.
  - **password** (String): The password of the user account to create.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json
    {
     "status": "password updated", 
     "username": "example_user"
    }
 - Example Request:
    ```bash
        curl -X PUT http://localhost:5000/api/update-password \
        -H "Content-Type: application/json" \
        -d '{"username": "example_user", "password": "new_secure_password"}'
    ```
 - Example Response:
     ```json
     {
      "status": "password updated", 
      "username": "example_user"
     }
    
## **Movie Management**
### Route: `/api/create-movie`
- **Request Type**: `POST`
- **Purpose**: Add a new movie to the catalog.
- **Request Body**:
  - **director** (String): The name of the movie's director.
  - **title** (String): The title of the movie.
  - **year** (int): The year the movie was released.
  - **genre** (String): The genre of the movie (e.g., Action, Drama, Comedy).
  - **duration** (int): The duration of the movie in minutes.
  - **rating** (float): The rating of the movie (e.g., IMDb rating).
- **Response Format**: JSON
  - Success Response Example:
    - Code: 201
    - Content:
    ```json=
    {
      "status": "success",
      "movie": "Example Title"
    }
 - Example Request:
    ```bash
        curl -X POST http://localhost:5000/api/create-movie \
        -H "Content-Type: application/json" \
        -d '{"director": "Example Director", "title": "Example Title", "year": 2023, "genre": "Action", "duration": 120, "rating": 8.5}'
    ```
 - Example Response:
     ```json
     {
      "status": "success", 
      "movie": "Example Title"
     }
  
### Route: `/api/clear-catalog`
- **Request Type**: `DELETE`
- **Purpose**: Clear all movies in the catalog.
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    {
      "status": "success", 
      "message": "Catalog cleared successfully"
    }
 - Example Request:
    ```bash
        curl -X DELETE http://localhost:5000/api/clear-catalog
    ```
 - Example Response:
     ```json
     {
      "status": "success", 
      "message": "Catalog cleared successfully"
     }

### Route: `/api/delete-movie/<int:movie_id>`
- **Request Type**: `DELETE`
- **Purpose**: Delete a movie by its ID.
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    {
      "status": "success", 
      "message": "Movie deleted successfully"
    }
 - Example Request:
    ```bash
        curl -X DELETE http://localhost:5000/api/delete-movie/123
    ```
 - Example Response:
     ```json
     {
      "status": "success", 
      "message": "Movie deleted successfully"
     }

### Route: `/api/get-movie-from-catalog-by-id/<int:movie_id>`
- **Request Type**: `GET`
- **Purpose**: Retrieve a movie by its ID.
- **Request Body**:
  - **movie_id** (int): The ID of the movie to retrieve.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    { 
      "status": "success", 
      "movie": { 
        "id": 123, 
        "director": "Example Director", 
        "title": "Example Title", 
        "year": 2023, 
        "genre": "Action", 
        "duration": 120, 
        "rating": 8.5 
      } 
    }
 - Example Request:
    ```bash
        curl -X GET http://localhost:5000/api/get-movie-from-catalog-by-id/123
    ```
 - Example Response:
     ```json
    { 
      "status": "success", 
      "movie": { 
        "id": 123, 
        "director": "Example Director", 
        "title": "Example Title", 
        "year": 2023, 
        "genre": "Action", 
        "duration": 120, 
        "rating": 8.5 
      } 
    }

### Route: `/api/get-all-movies-from-catalog`
- **Request Type**: `GET`
- **Purpose**: Retrieve all movies in the catalog.
- **Request Body**:
  - **Query Parameters (Optional)**:
      - **sort_by_rating** (bool): If true, sorts movies by rating in descending order.
      - **sort_by_watch_count** (bool): If true, sorts movies by watch count in descending order.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    {
        "status": "success", 
        "movies": [ 
          { 
            "id": 123, 
            "director": "Example Director", 
            "title": "Example Title", 
            "year": 2023, 
            "genre": "Action", 
            "duration": 120, 
            "rating": 8.5 
          }, 
          ... 
        ]
    }
 - Example Request:
    ```bash
        curl -X GET "http://localhost:5000/api/get-all-movies-from-catalog?sort_by_rating=true"
    ```
 - Example Response:
     ```json
    {
        "status": "success", 
        "movies": [ 
          { 
            "id": 123, 
            "director": "Example Director", 
            "title": "Example Title", 
            "year": 2023, 
            "genre": "Action", 
            "duration": 120, 
            "rating": 8.5 
          }, 
          ... 
        ]
    }

## **Watchlist Management**
### Route: `/api/add-movie-to-watchlist`
- **Request Type**: `POST`
- **Purpose**: Add a movie to the watchlist using compound key.
- **Request Body**:
  - **director** (String): The name of the movie's director.
  - **title** (String): The title of the movie.
  - **year** (int): The year the movie was released.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 201
    - Content:
    ```json=
    {
        "status": "success", 
        "message": "Movie added to watchlist"
    }
 - Example Request:
    ```bash
        curl -X POST http://localhost:5000/api/add-movie-to-watchlist \
        -H "Content-Type: application/json" \
        -d '{"director": "Example Director", "title": "Example Title", "year": 2023}'
    ```
 - Example Response:
     ```json
     {
      "status": "success", 
      "message": "Movie added to watchlist"
     }

---

## **Setup Instructions**

### Clone the Repository:
```bash
git clone <repo_url>
cd <repo_name>
```

### Install Dependencies:
```bash
pip install -r requirements.txt
```

### Setup Environment Variables:

Create a .env file using the .env.example template:
```bash
TMDB_API_KEY=your_api_key_here
DB_PATH=./db/movie_catalog.db
SQL_CREATE_TABLE_PATH=./sql/create_movie_table.sql
CREATE_DB=true
```

---

## **Testing**
### Unit Tests: 
Run Virtual Environment:
```bash
source movie_venv/bin/activate
```

Run PyTest:
```bash
pytest
```

### Smoke Tests: 
```bash
./run_docker.sh 
./smoketest.sh
```

---

## **License**
This project is for educational purposes under the Boston University CS411 curriculum.
