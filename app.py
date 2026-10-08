"""
Webapp zur Verwaltung von Lieblingsfilmen.
"""
import os
from flask import Flask, redirect, request, render_template, url_for, flash
import requests
from dotenv import load_dotenv
from models import Movie, db
from data_manager import DataManager

app = Flask(__name__)
app.secret_key = "super_secret_key_für_flash_messages"
# .env-Datei laden
load_dotenv()

app = Flask(__name__)


API_KEY = os.getenv("OMDB_API_KEY")

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{
    os.path.join(
        basedir, 'data/movies.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
data_manager = DataManager()


@app.route('/')
def index():
    """
    Die Startseite deiner Anwendung.
    Zeigt eine Liste aller registrierten Nutzer und ein Formular zum Hinzufügen neuer Nutzer.
    (Diese Route verwendet standardmäßig GET).
    """
    users = data_manager.get_users()
    return render_template('index.html', users=users)


@app.route('/users', methods=['POST'])
def create_user():
    """
    Wenn der Nutzer das „Nutzer hinzufügen“-Formular abschickt, wird eine POST-Anfrage ausgelöst.
    Der Server erhält die neuen Nutzerdaten, fügt sie der Datenbank hinzu und leitet dann zurück zu.
    """
    name = request.form.get('name')
    if not name or not name.strip():
        flash("Bitte gib einen gültigen Namen ein.", "error")
        return redirect(url_for('index'))

    new_user = data_manager.create_user(name.strip())
    if new_user:
        flash(f"Nutzer '{new_user.name}' erfolgreich angelegt!", "success")
    else:
        flash("Fehler beim Erstellen des Nutzers in der Datenbank.", "error")

    return redirect(url_for('index'))


@app.route('/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id: int):
    """
    Wenn du auf einen Nutzernamen klickst, ruft die App die Liste der Lieblingsfilme
    dieses Nutzers ab und zeigt sie an.
    """
    user = data_manager.get_user(user_id)
    if not user:
        flash("Nutzer wurde nicht gefunden.", "error")
        return redirect(url_for('index'))

    movies = data_manager.get_movies(user_id)
    return render_template('movies.html', user=user, movies=movies)


@app.route('/users/<int:user_id>/movies', methods=['POST'])
def add_user_movie(user_id: int):
    """
    Fügt einen neuen Film zur Favoritenliste eines Nutzers hinzu.
    """
    title = request.form.get('title')

    if not title or not title.strip():
        flash("Bitte gib einen Filmtitel ein.", "error")
        return redirect(url_for('get_user_movies', user_id=user_id))

    # --- OMDb API ---
    try:
        url = f"http://www.omdbapi.com/?apikey={API_KEY}&t={title.strip()}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data.get('Response') == 'True':
            raw_year = data.get('Year', '0')
            try:
                year = int(raw_year[:4])
            except ValueError:
                year = 0

            new_movie = Movie(
                title=data.get('Title'),
                director=data.get('Director', 'N/A'),
                year=year,
                poster_url=data.get('Poster', '')
            )
            saved_movie = data_manager.add_movie(user_id, new_movie)
            if saved_movie:
                flash(
                    f"Film '{
                        new_movie.title}' wurde hinzugefügt!",
                    "success")
            else:
                flash(
                    "Fehler beim Speichern des Films in der Datenbank.",
                    "error")
        else:
            flash(
                f"Film nicht gefunden: {
                    data.get(
                        'Error',
                        'Unbekannter Fehler')}",
                "error")

    except requests.exceptions.Timeout:
        flash(
            "Zeitüberschreitung bei der Anfrage an OMDb. Bitte erneut versuchen.",
            "error")

    except requests.exceptions.HTTPError as e:
        # Internes logging für Entwickler -> logfile
        print(f"[API ERROR] HTTP Status: {e.response.status_code}")

        # ensure not to poplute own key
        if e.response.status_code == 401:
            flash(
                "Verbindungsfehler zur Film-Datenbank (Authentifizierung fehlgeschlagen).",
                "error")
        else:
            flash("Fehler beim Abrufen der Filmdaten von OMDb.", "error")

    except requests.exceptions.RequestException as e:
        # logging for logfile
        print(f"[NETWORK ERROR] {e}")

        # general user error
        flash(
            "Es konnte keine Verbindung zum Film-Service hergestellt werden.",
            "error")

    return redirect(url_for('get_user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/update',
           methods=['POST'])
def update_user_movie(user_id: int, movie_id: int):
    """
    Erstellt eine Kopie des Films mit dem neuen Titel speziell für diesen Nutzer,
    damit die Änderung andere Nutzer mit demselben Film nicht betrifft.
    """
    new_title = request.form.get('new_title')
    if new_title and new_title.strip():
        success = data_manager.update_user_movie_title(
            user_id, movie_id, new_title.strip())
        if success:
            flash("Filmtitel erfolgreich aktualisiert!", "success")
        else:
            flash("Fehler beim Aktualisieren des Titels.", "error")
    else:
        flash("Ungültiger Titel.", "error")

    return redirect(url_for('get_user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/movies/<int:movie_id>/delete',
           methods=['POST'])
def delete_user_movie(user_id: int, movie_id: int):
    """
    Entfernt einen bestimmten Film aus der Liste der Lieblingsfilme eines Nutzers.
    """
    success = data_manager.delete_movie(user_id, movie_id)
    if success:
        flash("Film aus Favoriten entfernt.", "success")
    else:
        flash("Fehler beim Entfernen des Films.", "error")

    return redirect(url_for('get_user_movies', user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
    """
    404 error handler
    """
    print(e)
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """
     500 error handler
     """
    print(e)
    return render_template('500.html'), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
