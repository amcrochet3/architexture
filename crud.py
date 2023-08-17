from model import db, User



#CRUD operations for User
def create_user(email, password):
    new_user = User(email=email, password=password)

    db.session.add(new_user)
    db.session.commit()

    return new_user


def get_user_by_id(user_id):

    return User.query.get(user_id)


def get_user_by_email(email):

    return User.query.filter_by(email=email).first()


def get_all_users():

    return User.query.all()



if __name__ == "__main__":
    from server import app
    connect_to_db(app)