from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app import models
from scripts import seed_db


def test_parse_float_extracts_numeric_values():
    assert seed_db.parse_float("12.5 g") == 12.5
    assert seed_db.parse_float("0") == 0.0
    assert seed_db.parse_float("") == 0.0


def test_seed_imports_iron_from_csv_header(tmp_path, monkeypatch):
    csv_path = tmp_path / "nutrition.csv"
    csv_path.write_text(
        "name,serving_size,calories,protein,carbohydrate,fat,fiber,sugars,sodium,calcium,potassium,vitamin_c,vitamin_a,iron,caffeine,water,cholesterol,alcohol\n"
        "Spinach,100 g,23,2.9,3.6,0.4,2.2,0.4,79,99,558,28.1,469,2.71,0,91.4,0,0\n",
        encoding="utf-8",
    )

    test_db_path = tmp_path / "seed_test.db"
    engine = create_engine(
        f"sqlite:///{test_db_path}",
        connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(seed_db, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(seed_db, "engine", engine)
    monkeypatch.setattr(seed_db, "Base", Base)
    monkeypatch.setattr(
        seed_db.os.path,
        "join",
        lambda *args: str(csv_path) if "nutrition.csv" in args[-1] else str(Path(*args))
    )

    seed_db.seed()

    db = TestingSessionLocal()
    try:
        ingredient = db.query(models.Ingredient).filter(models.Ingredient.name == "Spinach").first()
        assert ingredient is not None
        assert ingredient.iron == 2.71
    finally:
        db.close()
