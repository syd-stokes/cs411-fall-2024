#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  response=$(curl -s -X GET "$BASE_URL/health")
  echo "Response: $response"
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "BASE_URL is: $BASE_URL"
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  response=$(curl -s -X GET "$BASE_URL/db-check")
  echo "Response: $response"
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "BASE_URL is: $BASE_URL"
    echo "Database check failed."
    exit 1
  fi
}


##############################################
#
# User management
#
##############################################

# Function to create a user
create_account() {
  echo "Creating a new user..."
  curl -s -X POST "$BASE_URL/create-account" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}' | grep -q '"status": "user added"'
  if [ $? -eq 0 ]; then
    echo "User created successfully."
  else
    echo "Failed to create user."
    exit 1
  fi
}

# Function to log in a user
login_user() {
  echo "Logging in user..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}')
  if echo "$response" | grep -q '"message": "User testuser logged in successfully."'; then
    echo "User logged in successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Login Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log in user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

# Function to log out a user
update_user_password() {
  echo "Logging out user..."
  response=$(curl -s -X POST "$BASE_URL/update-password" -H "Content-Type: application/json" \
    -d '{"username":"testuser"}')
  if echo "$response" | grep -q '"message": "User testuser logged out successfully."'; then
    echo "User logged out successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Logout Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log out user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}


##########################################################
#
# Movie Management
#
##########################################################

clear_catalog() {
  echo "Clearing the watchlist..."
  curl -s -X DELETE "$BASE_URL/clear-catalog" | grep -q '"status": "success"'
}

create_movie() {
  director=$1
  title=$2
  year=$3
  genre=$4
  duration=$5
  rating=$6

  echo "Creating movie ($director - $title, $year)..."
    response=$(curl -s -X POST "$BASE_URL/create-movie" \
        -H "Content-Type: application/json" \
        -d "{\"director\":\"$director\", \"title\":\"$title\", \"year\":$year, \"genre\":\"$genre\", \"duration\":$duration, \"rating\":$rating}")
    echo "Response: $response"
  if [ $? -eq 0 ]; then
    echo "Movie created successfully."
  else
    echo "BASE_URL is: $BASE_URL"
    echo "Failed to add movie."
    exit 1
  fi
}

delete_movie_by_id() {
  movie_id=$1

  echo "Deleting movie by ID ($movie_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-movie/$movie_id")
  echo "Response: $response"
  if echo "$response" | grep -q '"status": "movie deleted"'; then
    echo "Movie deleted successfully by ID ($movie_id)."
  else
    echo "BASE_URL is: $BASE_URL"
    echo "Failed to delete movie by ID ($movie_id)."
    exit 1
  fi
}

# get_all_movies() {
#   echo "Getting all movies in the watchlist..."
#   response=$(curl -s -X GET "$BASE_URL/get-all-movies-from-catalog")
#   echo "Response: $response"
#   if echo "$response" | grep -q '"status": "success"'; then
#     echo "All movies retrieved successfully."
#     if [ "$ECHO_JSON" = true ]; then
#       echo "Movies JSON:"
#       echo "$response" | jq .
#     fi
#   else
#     echo "BASE_URL is: $BASE_URL"
#     echo "Failed to get movies."
#     exit 1
#   fi
# }
get_all_movies() {
  sort_by_rating=$1
  sort_by_watch_count=$2

  echo "Getting all movies in the watchlist..."
  response=$(curl -s -X GET "$BASE_URL/get-all-movies-from-catalog?sort_by_rating=$sort_by_rating&sort_by_watch_count=$sort_by_watch_count")
  echo "Response: $response"
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movies retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movies JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get movies."
    exit 1
  fi
}

get_movie_by_id() {
  movie_id=$1
  
  echo "Getting movie by ID ($movie_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-movie-from-catalog-by-id/$movie_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie retrieved successfully by ID ($movie_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movie JSON (ID $movie_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get movie by ID ($movie_id)."
    exit 1
  fi
}

get_movie_by_compound_key() {
  director=$1
  title=$2
  year=$3

  echo "Getting movie by compound key (Director: '$director', Title: '$title', Year: $year)..."
  response=$(curl -s -X GET "$BASE_URL/get-movie-from-catalog-by-compound-key?director=$(echo $director | sed 's/ /%20/g')&title=$(echo $title | sed 's/ /%20/g')&year=$year")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie retrieved successfully by compound key."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movie JSON (by compound key):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get movie by compound key."
    exit 1
  fi
}

get_random_movie() {
  echo "Getting a random movie from the catalog..."
  response=$(curl -s -X GET "$BASE_URL/get-random-movie")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Random movie retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Random Movie JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get a random movie."
    exit 1
  fi
}


############################################################
#
# Watchlist Management
#
############################################################

add_movie_to_watchlist() {
  director=$1
  title=$2
  year=$3

  echo "Adding movie: $director - $title ($year) to watchlist..."
  response=$(curl -s -X POST "$BASE_URL/add-movie-to-watchlist" \
    -H "Content-Type: application/json" \
    -d "{\"director\":\"$director\", \"title\":\"$title\", \"year\":$year}")
  echo "Response: $response"

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie added to watchlist successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movie JSON:"
      echo "$response" | jq .
    fi
  else
    echo "BASE_URL is: $BASE_URL"
    echo "Failed to add movie to watchlist."
    exit 1
  fi
}

remove_movie_from_watchlist() {
  director=$1
  title=$2
  year=$3

  echo "Removing movie from watchlist: $director - $title ($year)..."
  response=$(curl -s -X DELETE "$BASE_URL/remove-movie-from-watchlist" \
    -H "Content-Type: application/json" \
    -d "{\"director\":\"$director\", \"title\":\"$title\", \"year\":$year}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie removed from watchlist successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movie JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to remove movie from watchlist."
    exit 1
  fi
}

remove_movie_by_film_number() {
  film_number=$1

  echo "Removing movie by film number: $film_number..."
  response=$(curl -s -X DELETE "$BASE_URL/remove-movie-from-watchlist-by-film-number/$film_number")

  if echo "$response" | grep -q '"status":'; then
    echo "Movie removed from watchlist by film number ($film_number) successfully."
  else
    echo "Failed to remove movie from watchlist by film number."
    exit 1
  fi
}

clear_watchlist() {
  echo "Clearing watchlist..."
  response=$(curl -s -X POST "$BASE_URL/clear-watchlist")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Watchlist cleared successfully."
  else
    echo "Failed to clear watchlist."
    exit 1
  fi
}


############################################################
#
# Play Watchlist
#
############################################################

play_current_movie() {
  echo "Playing current movie..."
  response=$(curl -s -X POST "$BASE_URL/play-current-movie")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Current movie is now playing."
  else
    echo "Failed to play current movie."
    exit 1
  fi
}

rewind_watchlist() {
  echo "Rewinding watchlist..."
  response=$(curl -s -X POST "$BASE_URL/rewind-watchlist")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Watchlist rewound successfully."
  else
    echo "Failed to rewind watchlist."
    exit 1
  fi
}

get_all_movies_from_watchlist() {
  echo "Retrieving all movies from watchlist..."
  response=$(curl -s -X GET "$BASE_URL/get-all-movies-from-watchlist")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "All movies retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movies JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve all movies from watchlist."
    exit 1
  fi
}

get_movie_from_watchlist_by_film_number() {
  film_number=$1
  echo "Retrieving movie by film number ($film_number)..."
  response=$(curl -s -X GET "$BASE_URL/get-movie-from-watchlist-by-film-number/$film_number")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie retrieved successfully by film number."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movie JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve movie by film number."
    exit 1
  fi
}

get_current_movie() {
  echo "Retrieving current movie..."
  response=$(curl -s -X GET "$BASE_URL/get-current-movie")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Current movie retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Current Movie JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve current movie."
    exit 1
  fi
}

get_watchlist_length_duration() {
  echo "Retrieving watchlist length and duration..."
  response=$(curl -s -X GET "$BASE_URL/get-watchlist-length-duration")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Watchlist length and duration retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Watchlist Info JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve watchlist length and duration."
    exit 1
  fi
}

go_to_film_number() {
  film_number=$1
  echo "Going to film number ($film_number)..."
  response=$(curl -s -X POST "$BASE_URL/go-to-film-number/$film_number")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Moved to film number ($film_number) successfully."
  else
    echo "Failed to move to film number ($film_number)."
    exit 1
  fi
}

play_entire_watchlist() {
  echo "Playing entire watchlist..."
  curl -s -X POST "$BASE_URL/play-entire-watchlist" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Entire watchlist played successfully."
  else
    echo "Failed to play entire watchlist."
    exit 1
  fi
}

# Function to play the rest of the watchlist
play_rest_of_watchlist() {
  echo "Playing rest of the watchlist..."
  curl -s -X POST "$BASE_URL/play-rest-of-watchlist" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Rest of watchlist played successfully."
  else
    echo "Failed to play rest of watchlist."
    exit 1
  fi
}

############################################################
#
# Arrange Watchlist
#
############################################################

move_movie_to_beginning() {
  director=$1
  title=$2
  year=$3

  echo "Moving movie ($director - $title, $year) to the beginning of the watchlist..."
  response=$(curl -s -X POST "$BASE_URL/move-movie-to-beginning" \
    -H "Content-Type: application/json" \
    -d "{\"director\": \"$director\", \"title\": \"$title\", \"year\": $year}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie moved to the beginning successfully."
  else
    echo "Failed to move movie to the beginning."
    exit 1
  fi
}

move_movie_to_end() {
  director=$1
  title=$2
  year=$3

  echo "Moving movie ($director - $title, $year) to the end of the watchlist..."
  response=$(curl -s -X POST "$BASE_URL/move-movie-to-end" \
    -H "Content-Type: application/json" \
    -d "{\"director\": \"$director\", \"title\": \"$title\", \"year\": $year}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie moved to the end successfully."
  else
    echo "Failed to move movie to the end."
    exit 1
  fi
}

move_movie_to_film_number() {
  director=$1
  title=$2
  year=$3
  film_number=$4

  echo "Moving movie ($director - $title, $year) to film number ($film_number)..."
  response=$(curl -s -X POST "$BASE_URL/move-movie-to-film-number" \
  -H "Content-Type: application/json" \
  -d "{\"director\": \"$director\", \"title\": \"$title\", \"year\": $year, \"film_number\": $film_number}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie moved to film number ($film_number) successfully."
  else
    echo "Failed to move movie to film number ($film_number)."
    exit 1
  fi
}

swap_movies_in_watchlist() {
  film_number1=$1
  film_number2=$2

  echo "Swapping movies at film numbers ($film_number1) and ($film_number2)..."
  response=$(curl -s -X POST "$BASE_URL/swap-movies-in-watchlist" \
    -H "Content-Type: application/json" \
    -d "{\"film_number_1\": $film_number1, \"film_number_2\": $film_number2}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movies swapped successfully between film numbers ($film_number1) and ($film_number2)."
  else
    echo "Failed to swap movies."
    exit 1
  fi
}



######################################################
#
# Leaderboard
#
######################################################

# # Function to get the movie leaderboard sorted by watch count
# get_movie_leaderboard() {
#   echo "Getting movie leaderboard sorted by watch count..."
#   response=$(curl -s -X GET "$BASE_URL/movie-leaderboard?sort=watch_count")
#   if echo "$response" | grep -q '"status": "success"'; then
#     echo "Movie leaderboard retrieved successfully."
#     if [ "$ECHO_JSON" = true ]; then
#       echo "Leaderboard JSON (sorted by watch count):"
#       echo "$response" | jq .
#     fi
#   else
#     echo "Failed to get movie leaderboard."
#     exit 1
#   fi
# }

# Function to get the movie leaderboard sorted by rating or watch count
get_movie_leaderboard() {
  echo "Getting movie leaderboard with various sorting options..."

  # Test: Sort by watch count
  response=$(curl -s -X GET "$BASE_URL/movie-leaderboard?sort_by_watch_count=true")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie leaderboard retrieved successfully (sorted by watch count)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by watch count):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get movie leaderboard sorted by watch count."
    exit 1
  fi

  # Test: Sort by rating
  response=$(curl -s -X GET "$BASE_URL/movie-leaderboard?sort_by_rating=true")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie leaderboard retrieved successfully (sorted by rating)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by rating):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get movie leaderboard sorted by rating."
    exit 1
  fi

  # Test: Sort by both watch count and rating
  response=$(curl -s -X GET "$BASE_URL/movie-leaderboard?sort_by_watch_count=true&sort_by_rating=true")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie leaderboard retrieved successfully (sorted by watch count and rating)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by watch count and rating):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get movie leaderboard sorted by watch count and rating."
    exit 1
  fi

  # Test: Default behavior (no sorting)
  response=$(curl -s -X GET "$BASE_URL/movie-leaderboard")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie leaderboard retrieved successfully (default sorting)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (default sorting):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get movie leaderboard with default sorting."
    exit 1
  fi
}


# Health checks
check_health
check_db

create_account
login_user
update_user_password

# Clear the catalog
clear_catalog
clear_watchlist

# Create movies
create_movie "Jon M. Chu" "Wicked" 2024 "Musical" 160 8.2
create_movie "Robert Zemeckis" "Forrest Gump" 1994 "Comedy" 144 8.8
create_movie "Quentin Tarantino" "Pulp Fiction" 1994 "Action" 154 8.9
create_movie "Nick Cassavetes" "The Notebook" 2004 "Romance" 123 7.8
create_movie "Samuel Armstrong" "Dumbo" 1941 "Animation" 64 7.2

add_movie_to_watchlist "Quentin Tarantino" "Pulp Fiction" 1994
add_movie_to_watchlist "Robert Zemeckis" "Forrest Gump" 1994
add_movie_to_watchlist "Nick Cassavetes" "The Notebook" 2004 "Romance" 123 7.8
add_movie_to_watchlist "Samuel Armstrong" "Dumbo" 1941 "Animation" 64 7.2

delete_movie_by_id 1
get_all_movies "true" "false"  # Sort by rating
get_all_movies "false" "true" # Sort by watch count
get_all_movies "false" "false" # Default sorting

get_movie_by_id 2
get_movie_by_compound_key "Quentin Tarantino" "Pulp Fiction" 1994
get_random_movie

clear_watchlist

add_movie_to_watchlist "Quentin Tarantino" "Pulp Fiction" 1994
add_movie_to_watchlist "Robert Zemeckis" "Forrest Gump" 1994
add_movie_to_watchlist "Nick Cassavetes" "The Notebook" 2004 "Romance" 123 7.8
add_movie_to_watchlist "Samuel Armstrong" "Dumbo" 1941 "Animation" 64 7.2

remove_movie_from_watchlist "Quentin Tarantino" "Pulp Fiction" 1994
remove_movie_by_film_number 2

get_all_movies_from_watchlist

# add_movie_to_watchlist "Robert Zemeckis" "Forrest Gump" 1994
add_movie_to_watchlist "Quentin Tarantino" "Pulp Fiction" 1994

move_movie_to_beginning "Quentin Tarantino" "Pulp Fiction" 1994
move_movie_to_end "Robert Zemeckis" "Forrest Gump" 1994
add_movie_to_watchlist "Nick Cassavetes" "The Notebook" 2004 "Romance" 123 7.8
move_movie_to_film_number "Nick Cassavetes" "The Notebook" 2004 1
swap_movies_in_watchlist 1 2

get_all_movies_from_watchlist
get_movie_from_watchlist_by_film_number 1

get_watchlist_length_duration

rewind_watchlist

play_entire_watchlist
play_current_movie
play_rest_of_watchlist

get_movie_leaderboard

echo "All tests passed successfully!"