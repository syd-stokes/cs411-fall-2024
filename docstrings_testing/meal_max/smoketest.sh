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
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Meal Management
#
##########################################################

clear_meals() {
  echo "Clearing the meals..."
  curl -s -X DELETE "$BASE_URL/clear-meals" | grep -q '"status": "success"'
}

create_meal() {
  meal=$1
  cuisine=$2
  price=$3
  difficulty=$4

  echo "Adding meal ($meal - $cuisine, $price) to the table..."
  response=$(curl -s -X POST "$BASE_URL/create-meal" -H "Content-Type: application/json" \
    -d "{\"meal\":\"$meal\", \"cuisine\":\"$cuisine\", \"price\":$price, \"difficulty\":\"$difficulty\"}")
  if echo "$response" | grep -q '"status": "combatant added"'; then
    echo "Meal added successfully."
  else
    echo "Failed to add meal."
    exit 1
  fi
}


delete_meal_by_id() {
  meal_id=$1
  echo "Deleting meal by ID ($meal_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-meal/$meal_id")
  if echo "$response" | grep -q '"status": "meal deleted"'; then 
    echo "Meal deleted successfully by ID ($meal_id)."
  else
    echo "Failed to delete meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_id() {
  meal_id=$1

  echo "Getting meal by ID ($meal_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-id/$meal_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by ID ($meal_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (ID $meal_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by ID ($meal_id)."
    exit 1
  fi
}

get_meal_by_name() {
  meal_name=$1

  echo "Getting meal by name ($meal_name)..."
  response=$(curl -s -X GET "$BASE_URL/get-meal-by-name/$meal_name")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal retrieved successfully by name ($meal_name)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Meal JSON (Name $meal_name):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal by name ($meal_name)."
    exit 1
  fi
}

# update_meal_stats() {
#   meal_id=$1
#   result=$2

#   echo "Updating meal stats for meal ID $meal_id with result $result..."

#   # Test the API endpoint to update meal stats
#   response=$(curl -s -X POST "$BASE_URL/update-meal-stats" -H "Content-Type: application/json" \
#     -d "{\"meal_id\": $meal_id, \"result\": \"$result\"}")

#   # Check if the response indicates success
#   if echo "$response" | grep -q '"status": "success"'; then
#     echo "Meal stats updated successfully for meal ID $meal_id with result $result."
#   else
#     echo "Failed to update meal stats for meal ID $meal_id with result $result."
#     exit 1
#   fi
# }


############################################################
#
# Combatant & Battle Management
#
############################################################

clear_combatants() {
  echo "Clearing combatants..."
  response=$(curl -s -X POST "$BASE_URL/clear-combatants")

  if echo "$response" | grep -q '"status": "combatants cleared"'; then
    echo "Combatants cleared successfully."
  else
    echo "Failed to clear combatants."
    exit 1
  fi
}

get_combatants() {
  echo "Getting all combatants..."
  response=$(curl -s -X GET "$BASE_URL/get-combatants")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All combatants retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Combatants JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get combatants."
    exit 1
  fi
}

prep_combatant() {
  meal_name=$1 
  echo "Adding meal with name '$meal_name' as combatant"
  response=$(curl -s -X POST "$BASE_URL/prep-combatant" -H "Content-Type: application/json" \
    -d "{\"meal\": \"$meal_name\"}")
  if echo "$response" | grep -q '"status": "combatant prepared"'; then
    echo "Meal with name '$meal_name' added as combatant."
  else
    echo "Failed to add meal with name '$meal_name' as combatant."
    exit 1
  fi
}

battle() {
  echo "Initiating a battle between two combatants..."
  response=$(curl -s -X GET "$BASE_URL/battle")
  if echo "$response" | grep -q '"status": "battle complete"'; then
    winner=$(echo "$response" | jq -r '.winner')
    echo "Battle completed. Winner: $winner"
  else
    echo "Battle failed."
    exit 1
  fi
}


######################################################
#
# Leaderboard
#
######################################################

# Function to get the meal leaderboard sorted by wins or win percentage
get_leaderboard() {
  sort_by=$1  # Specify "wins" or "win_pct"
  echo "Getting meal leaderboard sorted by $sort_by..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=$sort_by")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Meal leaderboard retrieved successfully (sorted by $sort_by)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by $sort_by):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get meal leaderboard."
    exit 1
  fi
}


# Health checks
check_health
check_db

# Clear the meals table & combatants
clear_meals
clear_combatants

# Create meals
create_meal "Pasta" "Italian" 25.99 "MED"
create_meal "Tacos" "Mexican" 15.99 "LOW"
create_meal "Dango" "Japanese" 5.99 "HIGH"
create_meal "White Rice" "Chinese" 20.00 "LOW"
create_meal "Curry" "Indian" 44.00 "MED"

delete_meal_by_id 4

get_meal_by_id 2
get_meal_by_name "Dango"
# get_meal_by_name "Hamburger"

#battle
prep_combatant "Curry"
#battle
prep_combatant "Tacos"
get_combatants
battle

get_leaderboard "wins"
get_leaderboard "win_pct"

# update_meal_stats 1 "win"
# update_meal_stats 2 "loss"

get_meal_by_id 1
get_meal_by_id 2

# Clear data again
clear_meals
clear_combatants

get_combatants
get_meal_by_id 1

echo "All tests passed successfully!"