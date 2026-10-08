"""
Datahandler for user and movie table
"""
from sqlalchemy.exc import SQLAlchemyError
from models import db, User, Movie


class DataManager:
    """
    Datahandler for user and movie table
    """

    def create_user(self, name: str) -> User | None:
        """
        creates a new user
        """
        try:
            new_user = User(name=name)
            db.session.add(new_user)
            db.session.commit()
            return new_user
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Fehler beim Erstellen des Nutzers: {e}")
            return None

    def get_users(self) -> list[User]:
        """
        returns all users
        """
        try:
            return db.session.query(User).all()
        except SQLAlchemyError as e:
            print(f"Fehler beim Abrufen der Nutzer: {e}")
            return []

    def get_user(self, user_id: int) -> User | None:
        """
        returns user
        """
        try:
            return db.session.get(User, user_id)
        except SQLAlchemyError as e:
            print(f"Fehler beim Abrufen des Nutzers {user_id}: {e}")
            return None

    def get_movies(self, user_id: int) -> list[Movie]:
        """
        get movies for particular user
        """
        user = self.get_user(user_id)
        if user:
            return user.favorites
        return []

    def add_movie(self, user_id: int, movie: Movie) -> Movie | None:
        """
        adds a new movie for particular user
        """
        try:
            user = self.get_user(user_id)
            if not user:
                return None

            existing_movie = db.session.query(Movie).filter_by(
                title=movie.title,
                year=movie.year,
                director=movie.director
            ).first()

            if existing_movie:
                movie_to_add = existing_movie
            else:
                db.session.add(movie)
                movie_to_add = movie

            if movie_to_add not in user.favorites:
                user.favorites.append(movie_to_add)

            db.session.commit()
            return movie_to_add
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Fehler beim Hinzufügen des Films: {e}")
            return None

    def update_user_movie_title(
            self, user_id: int, movie_id: int, new_title: str) -> bool:
        """
        updates user movie
        """
        try:
            user = self.get_user(user_id)
            old_movie = db.session.get(Movie, movie_id)

            if user and old_movie and old_movie in user.favorites:
                user.favorites.remove(old_movie)

                new_movie = Movie(
                    title=new_title,
                    director=old_movie.director,
                    year=old_movie.year,
                    poster_url=old_movie.poster_url
                )
                db.session.add(new_movie)
                user.favorites.append(new_movie)
                db.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Fehler beim Aktualisieren des Titels: {e}")
            return False

    def delete_movie(self, user_id: int, movie_id: int) -> bool:
        """
        deletes movie for particular user
        """
        try:
            user = self.get_user(user_id)
            movie = db.session.get(Movie, movie_id)

            if user is not None and movie is not None:
                if movie in user.favorites:
                    user.favorites.remove(movie)
                    db.session.commit()
                    return True
            return False
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Fehler beim Löschen des Films: {e}")
            return False
