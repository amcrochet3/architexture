import os
from flask import (Flask, render_template, request, flash, get_flashed_messages, session, redirect, jsonify)
from model import db, connect_to_db, User, ArchitecturalStructure, Album, Submission
import crud
from jinja2 import StrictUndefined
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]
app.jinja_env.undefined = StrictUndefined

UPLOAD_FOLDER = 'static/img/submissions'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



#helper functions
def get_current_user():
    user_id = session.get("user_id")

    if user_id:
        user = crud.get_user_by_id(user_id)
    else:
        user = None
    
    return user


def geocode_structure(structure):
    if isinstance(structure, Submission) and structure.user_address and structure.user_city and structure.user_country:
        address = f"{structure.user_address}, {structure.user_city}, {structure.user_state}, {structure.user_country}"
        state = structure.user_state
        img_path = structure.user_upload_file_path
    else:
        address = f"{structure.structure_name}, {structure.city}, {structure.country}"
        state = structure.state
        img_path = structure.img_path

    if state:
        address += f", {state}"

    address = address.replace(" ", "%20").replace(",", "")

    print(f"Geocoding address: {address}")

    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key=AIzaSyDSMrST6tA5LevywsZYvPXPsmIqhlbmRg4"
    response = requests.get(url)
    results = response.json()

    if results['status'] == 'OK':
        lat = results['results'][0]['geometry']['location']['lat']
        lng = results['results'][0]['geometry']['location']['lng']
        
        return {
            'structure_name': structure.user_structure_name if isinstance(structure, Submission) else structure.structure_name,
            'lat': lat,
            'lng': lng,
            'img_path': structure.user_upload_file_path if isinstance(structure, Submission) else img_path
        }
    else:
        print(f"Geocoding failed for address: {address}. Status: {results['status']}")
        return None


#index
@app.route('/')
def index():
    if "email" in session and "user_id" in session:
        return redirect(f'/dashboard/{session["user_id"]}')

    return render_template("index.html")


#user registration
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    messages = get_flashed_messages()

    if "email" in session and "user_id" in session:
        return redirect(f'/dashboard/{session["user_id"]}')

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = crud.get_user_by_email(email)

        if user:
            flash("Cannot create an account with that email address. Try again.")
        else:
            crud.create_user(email, password)
            flash("Account successfully created! Redirecting to the log in page...", "success")

        return redirect('/registration')

    return render_template("registration.html", messages=messages)


#user login
@app.route('/login', methods=['GET', 'POST'])
def login():
    messages = get_flashed_messages()

    if "email" in session and "user_id" in session:
        return redirect(f'/dashboard/{session["user_id"]}')

    if request.method == 'POST':
        email = request.form.get("email")
        password = request.form.get("password")

        user = crud.get_user_by_email(email)

        while user:
            if email == user.email and password == user.password:
                session["email"] = user.email
                session["user_id"] = user.user_id
                return redirect(f'/dashboard/{user.user_id}')
            else:
                flash("Invalid email or password. Try again.")
                return redirect('/login')

    return render_template("login.html", messages=messages)


#user logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()

    return redirect('/')


#unique user dashboard
@app.route('/dashboard/<user_id>', methods=['GET'])
def dashboard(user_id):
    user = get_current_user()
    featured_structure = ArchitecturalStructure.query.filter_by(featured=True).first()
    albums = crud.get_albums_by_user(user_id)
    recent_albums = albums[-8:]
    submissions = Submission.query.filter_by(status=True).all()
    recent_submissions = submissions[-8:]

    return render_template("dashboard.html", user=user, featured_structure=featured_structure, albums=recent_albums, submissions=recent_submissions)


#structure library
@app.route('/library', methods=['GET'])
def library():
    user = get_current_user()
    structures = crud.get_all_structures()
    albums = crud.get_albums_by_user(user.user_id)
    
    return render_template("library.html", user=user, structures=structures, albums=albums)


#structure details
@app.route('/structure-details/<structure_id>', methods=['GET'])
def structure_details(structure_id):
    user = get_current_user()
    structure = crud.get_structure_by_id(structure_id)
    albums = crud.get_albums_by_user(user.user_id)

    return render_template("structure-details.html", user=user, structure=structure, albums=albums)


#submitted structures map
@app.route('/map', methods=['GET'])
def map_display():
    user = get_current_user()

    return render_template("map.html", user=user)


@app.route('/map-data', methods=['GET'])
def map_data():
    structures = ArchitecturalStructure.query.all()
    submitted_structures = Submission.query.filter_by(status=True).all()
    locations = []

    for structure in structures + submitted_structures:
        location_data = geocode_structure(structure)
        if location_data:
            locations.append(location_data)

    print(f"Locations list: {locations}")

    return jsonify(locations)


#personalized album creation
@app.route('/albums/<user_id>', methods=['GET'])
def albums_display(user_id):
    user = get_current_user()
    albums = crud.get_albums_by_user(user_id)

    return render_template("albums.html", user=user, albums=albums)


@app.route('/albums/<user_id>', methods=['POST'])
def create_album(user_id):
    user = get_current_user()
    album_name = request.form.get('album-name')
    description = request.form.get('album-description')
    
    if album_name:
        album = crud.create_album(user_id=user.user_id, album_name=album_name, description=description)

        return jsonify({
            'album_id': album.album_id, 
            'album_name': album.album_name, 
            'description': album.description
        })
    else:
        return jsonify({'error': 'Album name is required'}), 400
    

@app.route('/add_to_album/<structure_id>', methods=['POST'])
def add_to_album(structure_id):
    user_id = session.get("user_id")
    album_id = request.form.get("album-id")
    
    album = crud.get_album_by_id(album_id)
    structure = crud.get_structure_by_id(structure_id)

    if structure in album.structures:
        return jsonify({'message': 'This structure is already in the album', 'added': False})
    else:
        crud.add_structure_to_album(album_id, structure_id)
        return jsonify({'message': 'Structure added to album successfully', 'added': True})


@app.route('/album-details/<album_id>', methods=['GET'])
def album_details(album_id):
    user = get_current_user()
    album = crud.get_album_by_id(album_id)
    structures = album.structures

    return render_template("album-details.html", user=user, album=album, structures=structures)


@app.route('/edit-album/<album_id>', methods=['POST'])
def edit_album(album_id):
    album_name = request.form['album-name']
    album_description = request.form['album-description']
    
    updated_album = crud.update_album(album_id, album_name, album_description)
    if updated_album:
        return jsonify({'success': 'Album updated successfully'})
    

@app.route('/delete-album/<album_id>', methods=['DELETE'])
def delete_album_route(album_id):
    success = crud.delete_album(album_id)
    if success:
        return jsonify({'success': 'Album deleted successfully'})
    

#user submissions
@app.route('/submit/<user_id>', methods=['GET'])
def submission_form_display(user_id):
    user = get_current_user()

    return render_template("submit.html", user=user)


@app.route('/submit/<user_id>', methods=['POST'])
def user_submission(user_id):
    file = request.files['file']
    file_path = None

    if 'file' in request.files:
        file = request.files['file']
        
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

    user_structure_name = request.form.get('user-structure-name')
    user_typology = request.form.get('user-typology')
    user_address = request.form.get('user-address')
    user_city = request.form.get('user-city')
    user_state = request.form.get('user-state')
    user_country = request.form.get('user-country')
    user_lat = request.form.get('user-lat')
    user_lng = request.form.get('user-lng')

    user_lat = float(user_lat) if user_lat else None
    user_lng = float(user_lng) if user_lng else None

    print("Received lat:", user_lat)  # Debugging
    print("Received lng:", user_lng)  # Debugging

    submission = crud.create_submission(
        user_id=user_id,
        user_structure_name=user_structure_name,
        user_typology=user_typology,
        user_address=user_address, 
        user_city=user_city, 
        user_state=user_state, 
        user_country=user_country, 
        user_upload_file_path=file_path,
        user_lat=user_lat, 
        user_lng=user_lng,
        status=False
    )

    return jsonify({'success': True, 'submission_id': submission.submission_id})


#admin dashboard and controls
@app.route('/admin', methods=['GET'])
def admin_dashboard_display():
    submissions = Submission.query.all()
    structures = ArchitecturalStructure.query.all()

    return render_template("admin.html", submissions=submissions, structures=structures)


@app.route('/admin/approve/<submission_id>', methods=['POST'])
def approve_submission(submission_id):
    crud.update_submission_status(submission_id)

    return jsonify({'success': True})


@app.route('/admin/deny/<submission_id>', methods=['POST'])
def deny_submission(submission_id):
    crud.delete_submission(submission_id=submission_id)

    return jsonify({'success': True})


@app.route('/admin/feature/<structure_id>', methods=['POST'])
def feature_structure(structure_id):
    structure = ArchitecturalStructure.query.get(structure_id)

    if structure:
        ArchitecturalStructure.query.update({ArchitecturalStructure.featured: False})
        structure.featured = True

        db.session.commit()

        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Structure not found'}), 404



if __name__ == "__main__":
    connect_to_db(app)
    app.run(host="0.0.0.0", debug=True)