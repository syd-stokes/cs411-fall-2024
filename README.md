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
This project is a web application designed for managing a movie catalog and watchlist. It features a robust backend using Flask, SQLite, and SQLAlchemy and integrates with the TMDB API for enriched movie data. The app provides functionalities for user management, movie management, and dynamic interactions with APIs.

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
  ```json
  {
    "username": "example_user",
    "password": "secure_password"
  }
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
  ```json
  {
    "username": "example_user",
    "password": "secure_password"
  }
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
  ```json
  {
    "username": "example_user",
    "password": "new_secure_password"
  }
- **Response**:
  ```json=
  {
    "status": "password updated",
    "username": "example_user"
  }
    
## **Movie Management**
### Route: `/api/create-movie`
- **Request Type**: `POST`
- **Purpose**: Add a new movie to the catalog.
- **Request Body**:
  ```json
  {
    "director": "Example Director",
    "title": "Example Title",
    "year": 2023,
    "genre": "Action",
    "duration": 120,
    "rating": 8.5
  }
- **Response**:
  ```json=
  {
    "status": "success",
    "movie": "Example Title"
  }
  
### Route: `/api/get-all-movies-from-catalog`
- **Request Type**: `GET`
- **Purpose**: Retrieve all movies in the catalog.
- **Query Parameters**:
  - sort_by_rating: Optional, true to sort by rating.
  - sort_by_watch_count: Optional, true to sort by watch count.
- **Response**:
  ```json=
  {
    "status": "success",
    "movies": [ ... ] // List of movie objects
  }
  
## **Watchlist Management**
### Route: `/api/add-movie-to-watchlist`
- **Request Type**: `POST`
- **Purpose**: Add a movie to the watchlist using compound key.
- **Request Body**:
  ```json
  {
    "director": "Example Director",
    "title": "Example Title",
    "year": 2023
  }
  ```
- **Response**:
  ```json=
  {
    "status": "success",
    "message": "Movie added to watchlist"
  }
  ```

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
