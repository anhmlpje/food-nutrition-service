"""
Seed script: imports nutrition.csv into the SQLite database.
Run once with: python scripts/seed_db.py
"""
import sys
import os
import re
import csv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app import models
from app.utils.nutrition_calc import infer_allergens

Base.metadata.create_all(bind=engine)


def parse_float(value: str) -> float:
    """Extract numeric value from strings like '2.5 g' or '100 mg'."""
    if not value or value.strip() in ("", "0"):
        return 0.0
    match = re.search(r"[\d.]+", str(value))
    return float(match.group()) if match else 0.0


def seed():
    db = SessionLocal()
    csv_path = os.path.join(os.path.dirname(__file__), "../data/nutrition.csv")

    if not os.path.exists(csv_path):
        print(f"ERROR: CSV file not found at {csv_path}")
        sys.exit(1)

    print("Seeding database from nutrition.csv ...")

    count = 0
    skipped = 0

    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "").strip()
            if not name:
                skipped += 1
                continue

            # Skip duplicates
            existing = db.query(models.Ingredient).filter(
                models.Ingredient.name == name
            ).first()
            if existing:
                skipped += 1
                continue

            allergens = infer_allergens(name)

            ingredient = models.Ingredient(
                name=name,
                serving_size=row.get("serving_size", "100 g"),
                calories=parse_float(row.get("calories", "0")),
                protein=parse_float(row.get("protein", "0")),
                carbohydrate=parse_float(row.get("carbohydrate", "0")),
                fat=parse_float(row.get("fat", "0")),
                fiber=parse_float(row.get("fiber", "0")),
                sugars=parse_float(row.get("sugars", "0")),
                sodium=parse_float(row.get("sodium", "0")),
                calcium=parse_float(row.get("calcium", "0")),
                potassium=parse_float(row.get("potassium", "0")),
                vitamin_c=parse_float(row.get("vitamin_c", "0")),
                vitamin_a=parse_float(row.get("vitamin_a", "0")),
                iron=parse_float(row.get("iron", row.get("irom", "0"))),
                caffeine=parse_float(row.get("caffeine", "0")),
                water=parse_float(row.get("water", "0")),
                cholesterol=parse_float(row.get("cholesterol", "0")),
                alcohol=parse_float(row.get("alcohol", "0")),
                allergens=",".join(allergens),
            )

            db.add(ingredient)
            count += 1

            # Commit in batches of 500 for performance
            if count % 500 == 0:
                db.commit()
                print(f"  Inserted {count} ingredients...")

    db.commit()
    db.close()
    print(f"\nDone! Inserted {count} ingredients, skipped {skipped}.")


if __name__ == "__main__":
    seed()
