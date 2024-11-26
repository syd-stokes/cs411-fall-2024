import logging
from typing import List
from playlist.movie_collection.models.movie_model import Movie, update_watch_count
from movie_collection.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class WatchlistModel:
    """
    A class to manage a watchist of movies.

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

        self.playlist.append(movie)

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
        logger.info("Removing movie at film number %d from playlist", film_number)
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

    def get_current_song(self) -> Song:
        """
        Returns the current song being played.
        """
        self.check_if_empty()
        return self.get_song_by_track_number(self.current_track_number)

    def get_playlist_length(self) -> int:
        """
        Returns the number of songs in the playlist.
        """
        return len(self.playlist)

    def get_playlist_duration(self) -> int:
        """
        Returns the total duration of the playlist in seconds.
        """
        return sum(song.duration for song in self.playlist)

    ##################################################
    # Playlist Movement Functions
    ##################################################

    def go_to_track_number(self, track_number: int) -> None:
        """
        Sets the current track number to the specified track number.

        Args:
            track_number (int): The track number to set as the current track.
        """
        self.check_if_empty()
        track_number = self.validate_track_number(track_number)
        logger.info("Setting current track number to %d", track_number)
        self.current_track_number = track_number

    def move_song_to_beginning(self, song_id: int) -> None:
        """
        Moves a song to the beginning of the playlist.

        Args:
            song_id (int): The ID of the song to move to the beginning.
        """
        logger.info("Moving song with ID %d to the beginning of the playlist", song_id)
        self.check_if_empty()
        song_id = self.validate_song_id(song_id)
        song = self.get_song_by_song_id(song_id)
        self.playlist.remove(song)
        self.playlist.insert(0, song)
        logger.info("Song with ID %d has been moved to the beginning", song_id)

    def move_song_to_end(self, song_id: int) -> None:
        """
        Moves a song to the end of the playlist.

        Args:
            song_id (int): The ID of the song to move to the end.
        """
        logger.info("Moving song with ID %d to the end of the playlist", song_id)
        self.check_if_empty()
        song_id = self.validate_song_id(song_id)
        song = self.get_song_by_song_id(song_id)
        self.playlist.remove(song)
        self.playlist.append(song)
        logger.info("Song with ID %d has been moved to the end", song_id)

    def move_song_to_track_number(self, song_id: int, track_number: int) -> None:
        """
        Moves a song to a specific track number in the playlist.

        Args:
            song_id (int): The ID of the song to move.
            track_number (int): The track number to move the song to (1-indexed).
        """
        logger.info("Moving song with ID %d to track number %d", song_id, track_number)
        self.check_if_empty()
        song_id = self.validate_song_id(song_id)
        track_number = self.validate_track_number(track_number)
        playlist_index = track_number - 1
        song = self.get_song_by_song_id(song_id)
        self.playlist.remove(song)
        self.playlist.insert(playlist_index, song)
        logger.info("Song with ID %d has been moved to track number %d", song_id, track_number)

    def swap_songs_in_playlist(self, song1_id: int, song2_id: int) -> None:
        """
        Swaps the positions of two songs in the playlist.

        Args:
            song1_id (int): The ID of the first song to swap.
            song2_id (int): The ID of the second song to swap.

        Raises:
            ValueError: If you attempt to swap a song with itself.
        """
        logger.info("Swapping songs with IDs %d and %d", song1_id, song2_id)
        self.check_if_empty()
        song1_id = self.validate_song_id(song1_id)
        song2_id = self.validate_song_id(song2_id)

        if song1_id == song2_id:
            logger.error("Cannot swap a song with itself, both song IDs are the same: %d", song1_id)
            raise ValueError(f"Cannot swap a song with itself, both song IDs are the same: {song1_id}")

        song1 = self.get_song_by_song_id(song1_id)
        song2 = self.get_song_by_song_id(song2_id)
        index1 = self.playlist.index(song1)
        index2 = self.playlist.index(song2)
        self.playlist[index1], self.playlist[index2] = self.playlist[index2], self.playlist[index1]
        logger.info("Swapped songs with IDs %d and %d", song1_id, song2_id)

    ##################################################
    # Playlist Playback Functions
    ##################################################

    def play_current_song(self) -> None:
        """
        Plays the current song.

        Side-effects:
            Updates the current track number.
            Updates the play count for the song.
        """
        self.check_if_empty()
        current_song = self.get_song_by_track_number(self.current_track_number)
        logger.info("Playing song: %s (ID: %d) at track number: %d", current_song.title, current_song.id, self.current_track_number)
        update_play_count(current_song.id)
        logger.info("Updated play count for song: %s (ID: %d)", current_song.title, current_song.id)
        previous_track_number = self.current_track_number
        self.current_track_number = (self.current_track_number % self.get_playlist_length()) + 1
        logger.info("Track number updated from %d to %d", previous_track_number, self.current_track_number)

    def play_entire_playlist(self) -> None:
        """
        Plays the entire playlist.

        Side-effects:
            Resets the current track number to 1.
            Updates the play count for each song.
        """
        self.check_if_empty()
        logger.info("Starting to play the entire playlist.")
        self.current_track_number = 1
        logger.info("Reset current track number to 1.")
        for _ in range(self.get_playlist_length()):
            logger.info("Playing track number: %d", self.current_track_number)
            self.play_current_song()
        logger.info("Finished playing the entire playlist. Current track number reset to 1.")

    def play_rest_of_playlist(self) -> None:
        """
        Plays the rest of the playlist from the current track.

        Side-effects:
            Updates the current track number back to 1.
            Updates the play count for each song in the rest of the playlist.
        """
        self.check_if_empty()
        logger.info("Starting to play the rest of the playlist from track number: %d", self.current_track_number)
        for _ in range(self.get_playlist_length() - self.current_track_number + 1):
            logger.info("Playing track number: %d", self.current_track_number)
            self.play_current_song()
        logger.info("Finished playing the rest of the playlist. Current track number reset to 1.")

    def rewind_playlist(self) -> None:
        """
        Rewinds the playlist to the beginning.
        """
        self.check_if_empty()
        logger.info("Rewinding playlist to the beginning.")
        self.current_track_number = 1

    ##################################################
    # Utility Functions
    ##################################################

    def validate_song_id(self, song_id: int, check_in_playlist: bool = True) -> int:
        """
        Validates the given song ID, ensuring it is a non-negative integer.

        Args:
            song_id (int): The song ID to validate.
            check_in_playlist (bool, optional): If True, checks if the song ID exists in the playlist.
                                                If False, skips the check. Defaults to True.

        Raises:
            ValueError: If the song ID is not a valid non-negative integer.
        """
        try:
            song_id = int(song_id)
            if song_id < 0:
                logger.error("Invalid song id %d", song_id)
                raise ValueError(f"Invalid song id: {song_id}")
        except ValueError:
            logger.error("Invalid song id %s", song_id)
            raise ValueError(f"Invalid song id: {song_id}")

        if check_in_playlist:
            if song_id not in [song_in_playlist.id for song_in_playlist in self.playlist]:
                logger.error("Song with id %d not found in playlist", song_id)
                raise ValueError(f"Song with id {song_id} not found in playlist")

        return song_id

    def validate_track_number(self, track_number: int) -> int:
        """
        Validates the given track number, ensuring it is a non-negative integer within the playlist's range.

        Args:
            track_number (int): The track number to validate.

        Raises:
            ValueError: If the track number is not a valid non-negative integer or is out of range.
        """
        try:
            track_number = int(track_number)
            if track_number < 1 or track_number > self.get_playlist_length():
                logger.error("Invalid track number %d", track_number)
                raise ValueError(f"Invalid track number: {track_number}")
        except ValueError:
            logger.error("Invalid track number %s", track_number)
            raise ValueError(f"Invalid track number: {track_number}")

        return track_number

    def check_if_empty(self) -> None:
        """
        Checks if the playlist is empty, logs an error, and raises a ValueError if it is.

        Raises:
            ValueError: If the playlist is empty.
        """
        if not self.playlist:
            logger.error("Playlist is empty")
            raise ValueError("Playlist is empty")