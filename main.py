from app.database import Session, Base, engine


Base.metadata.create_all(engine)
print("Database created")