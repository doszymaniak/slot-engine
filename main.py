from app.database import Session, Base, engine
from app.cli import main as cli_main


def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
    cli_main()