from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



class ArchitecturalStructure(db.Model):

    __tablename__ = "architectural_structures"

    structure_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    structure_name = db.Column(db.String(255), nullable=True)
    structure_type = db.Column(db.String(50))
    arch_style = db.Column(db.String(100), nullable=True)
    year_built = db.Column(db.Integer, nullable=True)
    arch_firm = db.Column(db.String(255), nullable=True)
    architect_name = db.Column(db.String(255), nullable=True)
    street = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(255))
    state = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(100))
    img_path = db.Column(db.String(255))
    img_path2 = db.Column(db.String(255))
    header = db.Column(db.String(255))
    summary = db.Column(db.String(1000))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    featured = db.Column(db.Boolean)
    times_featured = db.Column(db.Integer)

    #ArchitecturalStructure foreign key
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    #ArchitecturalStructure ORM relationships
    user = db.relationship("User", back_populates="structures")
    albums = db.relationship("Album", secondary="album_structures", back_populates="structures")


class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    admin_status = db.Column(db.Boolean)

    #User ORM relationships
    structures = db.relationship("ArchitecturalStructure", back_populates="user")
    admin = db.relationship("Admin", back_populates="user")
    submissions = db.relationship("Submission", back_populates="user")
    albums = db.relationship("Album", back_populates="user")


class Admin(db.Model):

    __tablename__ = "admins"

    admin_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)

    #Admin ORM relationship
    user = db.relationship("User", back_populates="admin")


class Submission(db.Model):

    __tablename__ = "submissions"

    submission_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    user_structure_name = db.Column(db.String(255), nullable=True)
    user_typology = db.Column(db.String(100), nullable=True)
    user_address = db.Column(db.String(255), nullable=True)
    user_city = db.Column(db.String(255), nullable=True)
    user_state = db.Column(db.String(50), nullable=True)
    user_country = db.Column(db.String(100), nullable=True)
    user_upload_file_path = db.Column(db.String(255), nullable=True)
    user_lat = db.Column(db.Float, nullable=True)
    user_lng = db.Column(db.Float, nullable=True)
    status = db.Column(db.Boolean)

    #Submission foreign key
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    #Submission ORM relationship
    user = db.relationship("User", back_populates="submissions")


class AlbumStructure(db.Model):

    __tablename__ = "album_structures"

    album_structures_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)

    #AlbumStructure foregin keys
    structure_id = db.Column(db.Integer, db.ForeignKey("architectural_structures.structure_id"))
    album_id = db.Column(db.Integer, db.ForeignKey("albums.album_id"))


class Album(db.Model):

    __tablename__ = "albums"

    album_id = db.Column(db.Integer, primary_key=True, autoincrement=True, unique=True)
    thumbnail_path = db.Column(db.String(255))
    album_name = db.Column(db.String(255))
    description = db.Column(db.String(500))

    #Album foreign key
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    #Album ORM relationships
    structures = db.relationship("ArchitecturalStructure", secondary="album_structures", back_populates="albums")
    user = db.relationship("User", back_populates="albums")
    


def connect_to_db(flask_app, db_uri="postgresql:///architexture", echo=True):

    flask_app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    flask_app.config["SQLALCHEMY_ECHO"] = echo
    flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

    db.app = flask_app
    db.init_app(flask_app)

    print("Connected to the db!")



if __name__ == "__main__":
    from server import app
    connect_to_db(app)