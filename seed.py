import os
import model
import server
import crud

os.system("dropdb architexture")
os.system("createdb architexture")

model.connect_to_db(server.app)
model.db.create_all()



for n in range(10):
    email = f"user{n}@test.com"
    password = f"test{n}"

    user = crud.create_user(email, password)

    model.db.session.add(user)
    model.db.session.commit()