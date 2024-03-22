@echo off
REM Erstellt eine virtuelle Umgebung
py -m venv myenv

REM Aktiviert die virtuelle Umgebung
call myenv\Scripts\activate

REM Setzt die Flask-App Variable
set FLASK_APP=Wagner.py

REM Installiert erforderliche Pakete
: pip install flask
: pip install flask-wtf
: pip install flask-sqlalchemy
: pip install flask-migrate
: pip install flask-login
: pip install flask-mail
: pip install flask-restful
: pip install flask-httpauth
: pip install flask-cors

REM Initialisiert die Datenbank und führt Migrationen durch
: flask db init
: flask db migrate
: flask db upgrade

REM Startet die Flask-Anwendung
flask run --host=0.0.0.0 --port=5000

echo Fertig!
