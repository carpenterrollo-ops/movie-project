## 🔑 OMDb API-Key einrichten

Diese Anwendung nutzt die [OMDb API](http://www.omdbapi.com/), um Filminformationen und Poster abzurufen.

### 1. Key kostenlos anfordern
1. Gehe auf [omdbapi.com/apikey.aspx](http://www.omdbapi.com/apikey.aspx).
2. Wähle die **FREE**-Option (1.000 Anfragen pro Tag).
3. Gib deine E-Mail-Adresse und deinen Namen ein und klicke auf **Submit**.
4. Prüfe dein E-Mail-Postfach und klicke auf den **Aktivierungslink** in der Bestätigungs-E-Mail (wichtig, da der Key erst danach funktioniert!).

### 2. Key im Projekt hinterlegen
1. Erstelle im Hauptverzeichnis des Projekts eine Datei namens `.env` (falls nicht vorhanden).
2. Trage deinen zugewiesenen Schlüssel dort ein:

```env
OMDB_API_KEY=dein_generierter_key