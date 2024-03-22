from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, current_user, UserMixin
from flask import Flask, request
from flask_restful import Resource, Api
from flask_cors import CORS
from flask_httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

app = Flask(__name__)
CORS(app)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydb.db'
app.secret_key = 'your_secret_key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    notes = db.relationship('Note', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
class NoteAPI(Resource):
    method_decorators = [login_required]

    def get(self):
        # Alle Notizen oder eine spezifische Notiz zurückgeben
        pass

    def post(self):
        # Neue Notiz hinzufügen
        pass

    def delete(self, note_id):
        # Eine spezifische Notiz löschen
        pass

class CustomUser(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

api.add_resource(NoteAPI, '/api/notes', '/api/notes/<int:note_id>')


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.String(200), nullable=False)
    #Enthält eine Verknüpfung zum Benutzer (über user_id) und den Inhalt der Notiz
    def __init__(self, user_id, content):
        self.user_id = user_id
        self.content = content

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            # Bei bereits existierendem Benutzernamen eine ensprechende Nachricht anzeigen
            return render_template('register.html', error="Benutzername bereits vergeben - Bitte wählen Sie einen anderen")
        
        # Passwort wird gehashed bevor es in die Datenbank geschrieben wird
        password_hash = generate_password_hash(password)
        
        # Neuen Benutzer wird in die Datenbank eingetragen
        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for('login'))  # Leitet Benutzer nach der Anmeldung zur Startseite

    return render_template('register.html')


@auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    return user


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            # Wenn Benutzer vorhanden und Passwort korrekt ist, wird der Benutzername in der Session gespeichert
            login_user(user)
            return redirect(url_for('login_success'))  # Weiterleitung bei erfolgreicher Anmeldung
        else:
            return redirect(url_for('login_error'))  # Weiterleitung bei Fehler bei der Anmeldung

    return render_template('login.html')

@app.route('/login_success')
@login_required  # Stellt sicher, dass der Benutzer angemeldet sein muss, um auf diese Seite zuzugreifen
def login_success():
    # Verwendet current_user.username, um den Benutzernamen des angemeldeten Benutzers zu erhalten
    if current_user.is_authenticated:
        return render_template('welcome.html', username=current_user.username)
    else:
        return 'Sie sind nicht angemeldet.'

@app.route('/api/impressum')
def impressum_api():
    return render_template('impressum.html')



@app.route('/login_error')
def login_error():
    return render_template('login_error.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)  # Löscht die Benutzername-Sitzungsvariable
    return redirect(url_for('index'))  # Weiterleitung zur Startseite


@app.route('/notes')
@login_required
def notes():
    all_notes = Note.query.all()  # Zeigt alle Notizen der Datenbank an
    return render_template('notes.html', notes=all_notes)


@app.route('/add_note', methods=['POST'])
@login_required
def add_note():
    if request.method == 'POST':
        user_id = current_user.id  # Holt sich die ID des angemeldeten Benutzers
        content = request.form['content']  # Zeigt die eingegebene Notiz

        # Erstellt ein neues Notizobjekt und fügt es in die Datenbank ein
        new_note = Note(user_id=user_id, content=content)
        db.session.add(new_note)
        db.session.commit()

    return redirect(url_for('view_notes'))  # Leitet den Benutzer zur Seite für die Anzeige der Notizen weiter


@app.route('/view_notes')
@login_required  #Erfordert, dass der Benutzer angemeldet ist
def view_notes():
    # Abrufen aller Notizen aus der Datenbank, ohne nach user_id zu filtern
    notes = Note.query.all()
    return render_template('notes.html', notes=notes)  # Übergabe aller Notizen an die HTML-Seite


@app.route('/delete_note/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note_to_delete = Note.query.get_or_404(note_id)
    if note_to_delete.user_id != current_user.id:
        return 'Sie sind nicht berechtigt, diese Notiz zu löschen.', 403
    db.session.delete(note_to_delete)
    db.session.commit()
    return redirect(url_for('view_notes'))





@app.route('/add_note_page')
def add_note_page():
    return render_template('add_note.html')


@app.route('/impressum')
def impressum():
    return render_template('impressum.html')

if __name__ == '__main__':
    app.run()
