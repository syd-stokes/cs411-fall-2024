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
     
### **Route**: /api/get-movie-from-catalog-by-compound-key
- **Request Type**: `GET`
- **Purpose**: Retrieve a movie by its compound key (director, title, year).
- **Request Body**:
  - **director** (String): The director's name.
  - **title** (String): The movie title.
  - **year** (Integer): The year the movie was released.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    {
	  "status": "success",
	  "movie": {
	    "director": "Example Director",
	    "title": "Example Title",
	    "year": 2023,
	    "genre": "Action",
	    "rating": 8.5
	  }
	}
  - Error Response Example (Missing Query Parameters):
     - Code: 400
      - Content:
      ```json=
     {
       "error": "Missing required query parameters: director, title, year"
     }
  - Error Response Example (Invalid Year):
     - Code: 400
     - Content:
      ```json=
     {
       "error": "Year must be an integer"
     }
 - Example Request:
    ```bash
        curl -X GET "http://localhost:5000/api/get-movie-from-catalog-by-compound-key?director=Example%20Director&title=Example%20Title&year=2023"
    ```
 - Example Response:
    ```json=
    {
	  "status": "success",
	  "movie": {
	    "director": "Example Director",
	    "title": "Example Title",
	    "year": 2023,
	    "genre": "Action",
	    "rating": 8.5
	  }
	}

### **Route**: /api/get-random-movie
- **Request Type**: `GET`
- **Purpose**: Retrieve a random movie from the catalog.
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    {
	  "status": "success",
	  "movie": {
	    "director": "Example Director",
	    "title": "Random Title",
	    "year": 2022,
	    "genre": "Drama",
	    "rating": 7.3
	  }
	}
  - Error Response Example:
     - Code: 500
     - Content:
     ```json=
     {
       "error": "Error retrieving a random movie"
     }
- Example Request:
  ```bash
    curl -X GET http://localhost:5000/api/get-random-movie
  ```
- Example Response:
  ```json=
      {
 	  "status": "success",
 	  "movie": {
 	    "director": "Example Director",
	    "title": "Random Title",
	    "year": 2022,
 	    "genre": "Drama",
	    "rating": 7.3
 	  }
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
     
### Route: `/api/remove-movie-by-movie-id`
- **Request Type**: `POST`
- **Purpose**: Remove a movie from the watchlist by compound key (director, title, year)
- **Request Body**:
  - **director** (String): The name of the movie's director.
  - **title** (String): The title of the movie.
  - **year** (int): The year the movie was released.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    {
        "status": "success", 
        "message": "Movie removed from watchlist"
    }
 - Example Request:
    ```bash
        curl -X POST http://localhost:5000/api/remove-movie-by-movie-id \
        -H "Content-Type: application/json" \
        -d '{"director": "Example Director", "title": "Example Title", "year": 2023}'
    ```
 - Example Response:
     ```json
     {
      "status": "success", 
      "message": "Movie removed from watchlist"
     }

### Route: `/api/remove-movie-by-film-number/<int:film_number>`
- **Request Type**: `DELETE`
- **Purpose**: Remove a movie from the watchlist by film number.
- **Request Body**:
  - **film_number** (int): The unique film number of the movie to remove.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    {
        "status": "success", 
        "message": "Movie at film number {film_number} removed from watchlist"
    }
 - Example Request:
    ```bash
        curl -X POST http://localhost:5000/api/remove-movie-by-film-number-/123 \
        -H "Content-Type: application/json" \
    ```
 - Example Response:
     ```json
     {
      "status": "success", 
      "message": "Movie at film number 123 removed from watchlist"
     }

### Route: `/api/clear-watchlist`
- **Request Type**: `POST`
- **Purpose**: clear all movies from the watchlist.
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    {
        "status": "success", 
        "message": "Watchlist cleared"
    }
 - Example Request:
    ```bash
        curl -X POST http://localhost:5000/api/clear-watchlist \
        -H "Content-Type: application/json" \
    ```
 - Example Response:
     ```json
     {
      "status": "success", 
      "message": "Watchlist cleared"
     }

## **TMBD Management**
### Route: `/api/movies-by-director`
- **Request Type**: `GET`
- **Purpose**: Retrieve a list of movies directed by a specific director
- **Request Body**:
  - **director** (String): The name of the director whose movies you want to fetch.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    {
       "movies": [
         {
            "overview": "Example Overview",
            "rating": 9.5,
            "release_date": "2021-01-01",
            "title": "Example Movie 1"
         },
         {
            "overview": "Example Overview",
            "rating": 8.7,
            "release_date": "2020-01-01",
            "title": "Example Movie 2"
         }
      ]
    }
 - Example Request:
    ```bash
     curl -X GET"http://localhost:5000/api/movies-by-director?director=Example%20Director" \
    -H "Content-Type: application/json"
    ```
 - Example Response:
    ```json=
    {
       "movies": [
         {
            "overview": "Example Overview",
            "rating": 9.5,
            "release_date": "2021-01-01",
            "title": "Example Movie 1"
         },
         {
            "overview": "Example Overview",
            "rating": 8.7,
            "release_date": "2020-01-01",
            "title": "Example Movie 2"
         }
      ]
    }

### Route: `/api/top-rated-movies`
- **Request Type**: `GET`
- **Purpose**: Retrieve a list of top-rated movies.
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    {
      "movies": [
          {
              "title": "Example Movie 1",
              "rating": 9.5,
              "year": 2021
          },
          {
              "title": "Example Movie 2",
              "rating": 9.3,
              "year": 2020
          }
      ]
    }
 - Example Request:
    ```bash
     curl -X GET http://localhost:5000/api/top-rated-movies \
    -H "Content-Type: application/json"
    ```
 - Example Response:
    ```json=
    {
      "movies": [
          {
              "title": "Example Movie 1",
              "rating": 9.5,
              "year": 2021
          },
          {
              "title": "Example Movie 2",
              "rating": 9.3,
              "year": 2020
          }
      ]
    }

### Route: `/api/search-movies`
- **Request Type**: `GET`
- **Purpose**: Search for movies by title
- **Request Body**:
  - **title** (String): The title of the movie to search for.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    {
       "movies": [
          {
            "overview": "Example Overview",
            "rating": 9.5,
            "release_date": "2021-01-01",
            "title": "Example Movie 1"
          },
          {
            "overview": "Example Overview",
            "rating": 8.7,
            "release_date": "2020-01-01",
            "title": "Example Movie 2"
          }
       ]
    }
 - Example Request:
    ```bash
      curl -X GET  "http://localhost:5000/api/search-movies?title=Example%20Title" \
      -H "Content-Type: application/json"
    ```
 - Example Response:
    ```json=
    {
       "movies": [
          {
            "overview": "Example Overview",
            "rating": 9.5,
            "release_date": "2021-01-01",
            "title": "Example Movie 1"
          },
          {
            "overview": "Example Overview",
            "rating": 8.7,
            "release_date": "2020-01-01",
            "title": "Example Movie 2"
          }
       ]
    }

### Route: `/api/movie-details/<int:movie_id>`
- **Request Type**: `GET`
- **Purpose**: Retrieve details of a specific movie by its ID
- **Request Body**:
  - **movie_id** (int): The unique ID of the movie to fetch details for.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
    {
      "movie": {
          "title": "Example Movie",
          "year": 2021,
          "rating": 8.7,
          "runtime": 120,
          "genres": ["Action", "Adventure"]
      }
    }
 - Example Request:
    ```bash
     curl -X GET http://localhost:5000/api/movie-details/123 \
      -H "Content-Type: application/json"
    ```
 - Example Response:
   ```json=
      {
        "movie": {
            "title": "Example Movie",
            "year": 2021,
            "rating": 8.7,
            "runtime": 120,
            "genres": ["Action", "Adventure"]
        }
    }

## Play Watchlist
### Route: `/api/play-current-movie`
- **Request Type**: `POST`
- **Purpose**: Play the current movie in the watchlist
- **Request Body**:
  - No parameters or body required.
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
            "title": "Example Movie",
            "year": 2021,
            "genre": "Drama",
            "duration": 120,
            "rating": 8.5
        }
    }
 - Example Request:
    ```bash
     curl -X POST http://localhost:5000/api/play-current-movie \
    -H "Content-Type: application/json"
    ```
 - Example Response:
   ```json=
   {
      "status": "success",
      "movie": {
          "id": 123,
          "director": "Example Director",
          "title": "Example Movie",
          "year": 2021,
          "genre": "Drama",
          "duration": 120,
          "rating": 8.5
      }
    }

### Route: `/api/play-entire-watchlist`
- **Request Type**: `POST`
- **Purpose**: Play all movies in the watchlist
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
     {
        "status": "success"
     }
 - Example Request:
    ```bash
      curl -X POST http://localhost:5000/api/play-entire-watchlist \
      -H "Content-Type: application/json"
    ```
 - Example Response:
    ```json=
    {
      "status": "success"
    }

### Route: `/api/play-rest-of-watchlist`
- **Request Type**: `POST`
- **Purpose**: Play the rest of the watchlist starting from the current track
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
     {
        "status": "success"
     }
 - Example Request:
    ```bash
      curl -X POST http://localhost:5000/api/play-rest-of-watchlist \
      -H "Content-Type: application/json"
     ```
 - Example Response:
    ```json=
   {
      "status": "success"
    }

### Route: `/api/rewind-watchlist`
- **Request Type**: `POST`
- **Purpose**: Rewinds the watchlist to the first movie
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
     {
        "status": "success"
    }
 - Example Request:
    ```bash
      curl -X POST http://localhost:5000/api/rewind-watchlist \
      -H "Content-Type: application/json"
    ```
 - Example Response:
    ```json=
   {
      "status": "success"
    }
    
### Route: /api/get-all-movies-from-watchlist
- **Request Type**: `GET`
- **Purpose**: Retrieves all movies from the watchlist.
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
      { “message”: “All movies retrieved successfully.”,
				“Movies” = [{
          "status": "success",
          "movie": {
            "id": 2,
            "title": "The Matrix",
            "director": "The Wachowskis",
            "year": 1999,
            "genre": "Sci-Fi",
            "duration": 136,
            "rating": 8.7
          }
        ]
    }
- Example Request:
	```bash
  	curl -X GET http://localhost:5000/api/get-all-movies-from-watchlist 
- Example Response:
    ```json=
    {
      “message”: “All movies retrieved successfully.”,
      “Movies”: [
        "status": "success",
        "movie": {
          "id": 2,
          "title": "The Matrix",
          "director": "The Wachowskis",
          "year": 1999,
          "genre": "Sci-Fi",
          "duration": 136,
          "rating": 8.7
        }
      ]
    }

### Route: /api/get-movie-from-watchlist-by-film-number/<film_number>
- **Request Type**: `GET`
- **Purpose**: Retrieves a specific movie from the watchlist by its film number.
- **Request Body**:
  - **film_number** (int): The number of the movie to fetch details for.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
      {
        “message” : “Movie retrieved successfully by film number.”,
        "status": "success",
        "movie": {
          "id": 2,
          "title": "The Matrix",
          "director": "The Wachowskis",
          "year": 1999,
          "genre": "Sci-Fi",
          "duration": 136,
          "rating": 8.7
        }
      }
- Example Request:
  ```bash
	  curl -X GET http://localhost:5000/api/get-movie-from-watchlist-by-film-number/2
- Example Response:
  ```json=
  {
  “message” : “Movie retrieved successfully by film number.”,
    "status": "success",
    "movie": {
      "id": 2,
      "title": "The Matrix",
      "director": "The Wachowskis",
      "year": 1999,
      "genre": "Sci-Fi",
      "duration": 136,
      "rating": 8.7
    }
  }

### Route: /api/get-current-movie
- **Request Type**: `GET`
- **Purpose**: Retrieves the current movie being played in the watchlist.
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
      ```json=
      {
        “message”: “ Current movie retrieved successfully.”,
          "status": "success",
          "current_movie": {
            "id": 3,
            "title": "Inception",
            "director": "Christopher Nolan",
            "year": 2010,
            "genre": "Sci-Fi",
            "duration": 148,
            "rating": 8.8
          }
      }
- Example Request:
  ```bash
      curl -X GET http://localhost:5000/api/get-current-movie
- Example Response:
  ```json=
 		{
      “message”: “ Current movie retrieved successfully.”,
        "status": "success",
        "current_movie": {
          "id": 3,
          "title": "Inception",
          "director": "Christopher Nolan",
          "year": 2010,
          "genre": "Sci-Fi",
          "duration": 148,
          "rating": 8.8
        }
    }

### Route: /api/get-watchlist-length-duration
- **Request Type**: `GET`
- **Purpose**: Retrieves the total number of movies and the total duration of the watchlist.
- **Request Body**:
  - No parameters or body required.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
      ```json=
      {
        “message”: "Watchlist length and duration retrieved successfully.",
        "status": "success",
        "watchlist_length": 5,
        "watchlist_duration": 600
      }
- Example Request:
  ```bash
    curl -X GET http://localhost:5000/api/get-watchlist-length-duration
- Example Response:
  ```json=
  {
    “message”: "Watchlist length and duration retrieved successfully.",
    "status": "success",
    "watchlist_length": 5,
    "watchlist_duration": 600
  }

### Route: /api/go-to-film-number/<film_number>
- **Request Type**: `POST`
- **Purpose**: Sets the watchlist to start playing from a specific film number.
- **Request Body**:
  - **film_number** (int): The film number to set as the current movie.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
      ```json=
      {
      “message”: “Moved to film number successfully ”
        "status": "success",
        "film_number": 3
      }
- Example Request:
	```bash
	curl -X POST http://localhost:5000/api/go-to-film-number/3
- Example Response:
	```json=
   {
    “message”: “Moved to film number successfully ”
    "status": "success",
    "film_number": 3
  }

### Route: /api/move-movie-to-beginning
- **Request Type**: `POST`
- **Purpose**: Moves a specified movie to the beginning of the watchlist.
- **Request Body**:
	- **director** (String): The director of the movie.
  - **title** (String): The title of the movie.
  - **year** (int): The year the movie was released.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
      ```json=
      {
        “message” : “Movie moved to the beginning successfully.”,
        "status": "success",
        "movie": "Director Name - Movie Title"
      }
- Example Request:
  ```bash
    {
      "director": "Director Name",
      "title": "Movie Title",
      "year": 2023
    }
- Example Response:
  ```json=
  {
    “message” : “Movie moved to the beginning successfully.”,
    "status": "success",
    "movie": "Director Name - Movie Title"
  }

### Route: /api/move-movie-to-end
- **Request Type**: `POST`
- **Purpose**: Moves a specified movie to the end of the watchlist.
- **Request Body**:
  - **director** (String): The director of the movie.
  - **title** (String): The title of the movie.
  - **year** (int): The year the movie was released.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
      ```json=
      {
        “message” : "Movie moved to the end successfully."
        "status": "success",
        "movie": "Director Name - Movie Title"
      }
- Example Request:
  ```bash
  {
      "director": "Director Name",
      "title": "Movie Title",
      "year": 2023
  }
- Example Response:
  ```json=
  {
    “message” : "Movie moved to the end successfully."
    "status": "success",
    "movie": "Director Name - Movie Title"
  }

### Route: /api/move-movie-to-film-number
- **Request Type**: `POST`
- **Purpose**: Moves a specified movie to a specific position (film number) in the watchlist.
- **Request Body**:
  - **director** (String): The director of the movie.
  - **title** (String): The title of the movie.
  - **year** (int): The year the movie was released.
  - **film_number** (int): The new position in the watchlist to move the movie to
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
      ```json=
      {
      	“message” : Movie moved to film number successfully
      	"status": "success",
      	"movie": "Director Name - Movie Title",
      	"film_number": 3
      }
- Example Request:
  ```bash
    {
     	"director": "Director Name",
        "title": "Movie Title",
        "year": 2023,
        "film_number": 3
    }
- Example Response:
  ```json=
  {
    “message” : Movie moved to film number successfully
    "status": "success",
    "movie": "Director Name - Movie Title",
    "film_number": 3
  }

### Route: /api/swap-movies-in-watchlist
- **Request Type**: `POST`
- **Purpose**: Swaps the positions of two movies in the watchlist by their film numbers.
- **Request Body**:
  - **film_number_1** (int): The film number of the first movie.
  - **film_number_2** (int): The film number of the second movie.
- **Response Format**: JSON
  - Success Response Example:
    - Code: 200
    - Content:
    ```json=
	{
	      "status": "success",
	      "swapped_movies": {
	        "film_1": {
	          "id": 1,
	          "director": "Director 1",
	          "title": "Movie 1"
	        },
	        "film_2": {
	          "id": 2,
	          "director": "Director 2",
	          "title": "Movie 2"
	        }
	      }
	    }
- Example Request:
  ```bash
	{
      "film_number_1": 1,
      "film_number_2": 2
    }
- Example Response:
  ```json=
	{
    "status": "success",
    "swapped_movies": {
      "film_1": {
        "id": 1,
        "director": "Director 1",
        "title": "Movie 1"
      },
      "film_2": {
        "id": 2,
        "director": "Director 2",
        "title": "Movie 2"
      }
    }
  }

### Route: /api/movie-leaderboard
- **Request Type**: `GET`
- **Purpose**: Retrieves a leaderboard of movies sorted by rating or watch count.
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
        “message” : “Retrieved leaderboard successfully”,
          "status": "success",
          "leaderboard": [
            {
              "id": 1,
              "title": "Movie 1",
              "rating": 9.8,
              "watch_count": 120
            },
            {
              "id": 2,
              "title": "Movie 2",
              "rating": 9.5,
              "watch_count": 100
            }
          ]
      }
- Example Request:
  ```bash
  curl -X GET "http://localhost:5000/api/movie-leaderboard?sort_by_rating=true&sort_by_watch_count=false"
- Example Response:
  ```json=
  {
    “message” : “Retrieved leaderboard successfully”,
      "status": "success",
      "leaderboard": [
        {
          "id": 1,
          "title": "Movie 1",
          "rating": 9.8,
          "watch_count": 120
        },
        {
          "id": 2,
          "title": "Movie 2",
          "rating": 9.5,
          "watch_count": 100
        }
      ]
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
