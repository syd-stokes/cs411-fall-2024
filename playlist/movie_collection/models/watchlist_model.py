import logging
from typing import List
from playlist.movie_collection.models.movie_model import Movie, update_watch_count
from movie_collection.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class WatchlistModel:
    """
    A class to manage a watchlist of movies.

    Attributes:
        current_film_number (int): The current film number being watched.
        watchlist (List[Movie]): The list of movies in the watchlist.

    """

    def __init__(self):
        """
        Initializes the WatchlistModel with an empty watchlist and the current film set to 1.
        """
        self.current_film_number = 1
        self.watchlist: List[Movie] = []
        
    ##################################################
    # Movie Management Functions
    ##################################################

    def add_movie_to_watchlist(self, movie: Movie) -> None:
        """
        Adds a movie to the watchlist.

        Args:
            movie (Movie): the movie to add to the watchlist.

        Raises:
            TypeError: If the movie is not a valid Movie instance.
            ValueError: If a movie with the same 'id' already exists.
        """
        logger.info("Adding new movie to watchlist")
        if not isinstance(movie, Movie):
            logger.error("Movie is not a valid movie")
            raise TypeError("Movie is not a valid movie")

        movie_id = self.validate_movie_id(movie.id, check_in_watchlist=False)
        if movie_id in [movie_in_watchlist.id for movie_in_watchlist in self.watchlist]:
            logger.error("Movie with ID %d already exists in the watchlist", movie.id)
            raise ValueError(f"Movie with ID {movie.id} already exists in the watchlist")

        self.watchlist.append(movie)

    def remove_movie_by_movie_id(self, movie_id: int) -> None:
        """
        Removes a movie from the watchlist by its movie ID.

        Args:
            movie_id (int): The ID of the movie to remove from the watchlist.

        Raises:
            ValueError: If the watchlist is empty or the movie ID is invalid.
        """
        logger.info("Removing movie with id %d from watchlist", movie_id)
        self.check_if_empty()
        movie_id = self.validate_movie_id(movie_id)
        self.watchlist = [movie_in_watchlist for movie_in_watchlist in self.watchlist if movie_in_watchlist.id != movie_id]
        logger.info("Movie with id %d has been removed", movie_id)

    def remove_movie_by_film_number(self, film_number: int) -> None:
        """
        Removes a movie from the watchlist by its film number (1-indexed).

        Args:
            film_number (int): The film number of the movie to remove.

        Raises:
            ValueError: If the watchlist is empty or the film number is invalid.
        """
        logger.info("Removing movie at film number %d from watchlist", film_number)
        self.check_if_empty()
        film_number = self.validate_film_number(film_number)
        watchlist_index = film_number - 1
        logger.info("Removing movie: %s", self.watchlist[watchlist_index].title)
        del self.watchlist[watchlist_index]

    def clear_watchlist(self) -> None:
        """
        Clears all movies from the watchlist. If the watchlist is already empty, logs a warning.
        """
        logger.info("Clearing watchlist")
        if self.get_watchlist_length() == 0:
            logger.warning("Clearing an empty watchlist")
        self.watchlist.clear()

    ##################################################
    # Watchlist Retrieval Functions
    ##################################################

    def get_all_movies(self) -> List[Movie]:
        """
        Returns a list of all movies in the watchlist.
        """
        self.check_if_empty()
        logger.info("Getting all movies in the watchlist")
        return self.watchlist

    def get_movie_by_movie_id(self, movie_id: int) -> Movie:
        """
        Retrieves a movie from the watchlist by its movie ID.

        Args:
            movie_id (int): The ID of the movie to retrieve.

        Raises:
            ValueError: If the watchlist is empty or the movie is not found.
        """
        self.check_if_empty()
        movie_id = self.validate_movie_id(movie_id)
        logger.info("Getting movie with id %d from watchlist", movie_id)
        return next((movie for movie in self.watchlist if movie.id == movie_id), None)

    def get_movie_by_film_number(self, film_number: int) -> Movie:
        """
        Retrieves a movie from the watchlist by its film number (1-indexed).

        Args:
            film_number (int): The film number of the movie to retrieve.

        Raises:
            ValueError: If the watchlist is empty or the film number is invalid.
        """
        self.check_if_empty()
        film_number = self.validate_film_number(film_number)
        watchlist_index = film_number - 1
        logger.info("Getting movie at film number %d from watchlist", film_number)
        return self.watchlist[watchlist_index]

    def get_current_movie(self) -> Movie:
        """
        Returns the current movie being watched.
        """
        self.check_if_empty()
        return self.get_movie_by_film_number(self.current_film_number)

    def get_watchlist_length(self) -> int:
        """
        Returns the number of movies in the watchlist.
        """
        return len(self.watchlist)

    def get_watchlist_duration(self) -> int:
        """
        Returns the total duration of the watchlist in minutes.
        """
        return sum(movie.duration for movie in self.watchlist)

    ##################################################
    # Watchlist Movement Functions
    ##################################################

    def go_to_film_number(self, film_number: int) -> None:
        """
        Sets the current film number to the specified film number.

        Args:
            film_number (int): The film number to set as the current film.
        """
        self.check_if_empty()
        film_number = self.validate_film_number(film_number)
        logger.info("Setting current film number to %d", film_number)
        self.current_film_number = film_number

    def move_movie_to_beginning(self, movie_id: int) -> None:
        """
        Moves a movie to the beginning of the watchlist.

        Args:
            movie_id (int): The ID of the movie to move to the beginning.
        """
        logger.info("Moving movie with ID %d to the beginning of the watchlist", movie_id)
        self.check_if_empty()
        movie_id = self.validate_movie_id(movie_id)
        movie = self.get_movie_by_movie_id(movie_id)
        self.watchlist.remove(movie)
        self.watchlist.insert(0, movie)
        logger.info("Movie with ID %d has been moved to the beginning", movie_id)

    def move_movie_to_end(self, movie_id: int) -> None:
        """
        Moves a movie to the end of the watchlist.

        Args:
            movie_id (int): The ID of the movie to move to the end.
        """
        logger.info("Moving movie with ID %d to the end of the watchlist", movie_id)
        self.check_if_empty()
        movie_id = self.validate_movie_id(movie_id)
        movie = self.get_movie_by_movie_id(movie_id)
        self.watchlist.remove(movie)
        self.watchlist.append(movie)
        logger.info("Movie with ID %d has been moved to the end", movie_id)

    def move_movie_to_film_number(self, movie_id: int, film_number: int) -> None:
        """
        Moves a movie to a specific film number in the watchlist.

        Args:
            movie_id (int): The ID of the movie to move.
            film_number (int): The film number to move the movie to (1-indexed).
        """
        logger.info("Moving movie with ID %d to film number %d", movie_id, film_number)
        self.check_if_empty()
        movie_id = self.validate_movie_id(movie_id)
        film_number = self.validate_film_number(film_number)
        watchlist_index = film_number - 1
        movie = self.get_movie_by_movie_id(movie_id)
        self.watchlist.remove(movie)
        self.watchlist.insert(watchlist_index, movie)
        logger.info("Movie with ID %d has been moved to film number %d", movie_id, film_number)

    def swap_movies_in_watchlist(self, movie1_id: int, movie2_id: int) -> None:
        """
        Swaps the positions of two movies in the watchlist.

        Args:
            movie1_id (int): The ID of the first movie to swap.
            movie2_id (int): The ID of the second movie to swap.

        Raises:
            ValueError: If you attempt to swap a movie with itself.
        """
        logger.info("Swapping movies with IDs %d and %d", movie1_id, movie2_id)
        self.check_if_empty()
        movie1_id = self.validate_movie_id(movie1_id)
        movie2_id = self.validate_movie_id(movie2_id)

        if movie1_id == movie2_id:
            logger.error("Cannot swap a movie with itself, both movie IDs are the same: %d", movie1_id)
            raise ValueError(f"Cannot swap a movie with itself, both movie IDs are the same: {movie1_id}")

        movie1 = self.get_movie_by_movie_id(movie1_id)
        movie2 = self.get_movie_by_movie_id(movie2_id)
        index1 = self.watchlist.index(movie1)
        index2 = self.watchlist.index(movie2)
        self.watchlist[index1], self.watchlist[index2] = self.watchlist[index2], self.watchlist[index1]
        logger.info("Swapped movies with IDs %d and %d", movie1_id, movie2_id)

    ##################################################
    # Watchlist Playback Functions
    ##################################################

    def play_current_movie(self) -> None:
        """
        Plays the current movie.

        Side-effects:
            Updates the current film number.
            Updates the watch count for the movie.
        """
        self.check_if_empty()
        current_movie = self.get_movie_by_film_number(self.current_film_number)
        logger.info("Playing movie: %s (ID: %d) at film number: %d", current_movie.title, current_movie.id, self.current_film_number)
        update_watch_count(current_movie.id)
        logger.info("Updated watch count for movie: %s (ID: %d)", current_movie.title, current_movie.id)
        previous_film_number = self.current_film_number
        self.current_film_number = (self.current_film_number % self.get_watchlist_length()) + 1
        logger.info("Film number updated from %d to %d", previous_film_number, self.current_film_number)

    def play_entire_watchlist(self) -> None:
        """
        Plays the entire watchlist.

        Side-effects:
            Resets the current film number to 1.
            Updates the watch count for each movie.
        """
        self.check_if_empty()
        logger.info("Starting to play the entire watchlist.")
        self.current_film_number = 1
        logger.info("Reset current film number to 1.")
        for _ in range(self.get_watchlist_length()):
            logger.info("Playing film number: %d", self.current_film_number)
            self.play_current_movie()
        logger.info("Finished playing the entire watchlist. Current film number reset to 1.")

    def play_rest_of_watchlist(self) -> None:
        """
        Plays the rest of the watchlist from the current film.

        Side-effects:
            Updates the current film number back to 1.
            Updates the watch count for each movie in the rest of the watchlist.
        """
        self.check_if_empty()
        logger.info("Starting to play the rest of the watchlist from film number: %d", self.current_film_number)
        for _ in range(self.get_watchlist_length() - self.current_film_number + 1):
            logger.info("Playing film number: %d", self.current_film_number)
            self.play_current_movie()
        logger.info("Finished playing the rest of the watchlist. Current film number reset to 1.")

    def rewind_watchlist(self) -> None:
        """
        Rewinds the watchlist to the beginning.
        """
        self.check_if_empty()
        logger.info("Rewinding watchlist to the beginning.")
        self.current_film_number = 1

    ##################################################
    # Utility Functions
    ##################################################

    def validate_movie_id(self, movie_id: int, check_in_watchlist: bool = True) -> int:
        """
        Validates the given movie ID, ensuring it is a non-negative integer.

        Args:
            movie_id (int): The movie ID to validate.
            check_in_watchlist (bool, optional): If True, checks if the movie ID exists in the watchlist.
                                                If False, skips the check. Defaults to True.

        Raises:
            ValueError: If the movie ID is not a valid non-negative integer.
        """
        try:
            movie_id = int(movie_id)
            if movie_id < 0:
                logger.error("Invalid movie id %d", movie_id)
                raise ValueError(f"Invalid movie id: {movie_id}")
        except ValueError:
            logger.error("Invalid movie id %s", movie_id)
            raise ValueError(f"Invalid movie id: {movie_id}")

        if check_in_watchlist:
            if movie_id not in [movie_in_watchlist.id for movie_in_watchlist in self.watchlist]:
                logger.error("Movie with id %d not found in watchlist", movie_id)
                raise ValueError(f"Movie with id {movie_id} not found in watchlist")

        return movie_id

    def validate_film_number(self, film_number: int) -> int:
        """
        Validates the given film number, ensuring it is a non-negative integer within the watchlist's range.

        Args:
            film_number (int): The film number to validate.

        Raises:
            ValueError: If the film number is not a valid non-negative integer or is out of range.
        """
        try:
            film_number = int(film_number)
            if film_number < 1 or film_number > self.get_watchlist_length():
                logger.error("Invalid film number %d", film_number)
                raise ValueError(f"Invalid film number: {film_number}")
        except ValueError:
            logger.error("Invalid film number %s", film_number)
            raise ValueError(f"Invalid film number: {film_number}")

        return film_number

    def check_if_empty(self) -> None:
        """
        Checks if the watchlist is empty, logs an error, and raises a ValueError if it is.

        Raises:
            ValueError: If the watchlist is empty.
        """
        if not self.watchlist:
            logger.error("Watchlist is empty")
            raise ValueError("Watchlist is empty")