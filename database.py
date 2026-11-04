# This is where all the actual database logic lives: get, create, update,
# delete art records. Routes call these functions instead of talking
# to MySQL directly, so all the query logic stays in one place.
#this import jason is used to handle the JSON data
import json
from config.db import engine
from schemas.art_model import art


# Retrieves all art records from the database.
def get_all():
    with engine.connect() as conn:
        result = conn.execute(art.select()).fetchall()
        # Convert each database row into a dictionary.
        return [dict(row._mapping) for row in result]


# Retrieves one art record by its ID.
def get_by_id(art_id: str):
    with engine.connect() as conn:
        result = conn.execute(
            art.select().where(art.c.id == art_id)
        ).fetchone()
        return dict(result._mapping) if result else None


# Creates a new art record.
def create(art_dict: dict):
    with engine.begin() as conn:
        conn.execute(art.insert().values(**art_dict))
    return art_dict


# Deletes an art record if it exists.
def delete(art_id: str):
    with engine.begin() as conn:
        item = conn.execute(
            art.select().where(art.c.id == art_id)
        ).fetchone()

        if item:
            conn.execute(art.delete().where(art.c.id == art_id))
            return dict(item._mapping)

    return None


# Updates an existing art record and returns the updated version.
def update(art_id: str, updated_data: dict):
    with engine.begin() as conn:
        item = conn.execute(
            art.select().where(art.c.id == art_id)
        ).fetchone()

        if not item:
            return None

        conn.execute(
            art.update()
            .where(art.c.id == art_id)
            .values(**updated_data)
        )

        result = conn.execute(
            art.select().where(art.c.id == art_id)
        ).fetchone()

        return dict(result._mapping) if result else None
def export_to_json(filepath="data.json"):
    # Exports all art records from MySQL into a readable JSON file, for demonstration/backup purposes.
    all_art = get_all()
    with open(filepath, "w") as f:
        json.dump(all_art, f, indent=4, default=str)
    return filepath

def export_chat_to_json(db, filepath="chat_data.json"):
    # Exports all chat messages into a readable JSON file, same idea as export_to_json for art.
    # Only username + text + time are written (no emails or hashes), oldest message first.
    from schemas.art_model import ChatMessage, User
    rows = (
        db.query(ChatMessage, User.username)
        .join(User, User.id == ChatMessage.user_id)
        .order_by(ChatMessage.id.asc())
        .all()
    )
    messages = [
        {"id": m.id, "username": name, "content": m.content, "created_at": m.created_at}
        for m, name in rows
    ]
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=4, default=str, ensure_ascii=False)
    return filepath, len(messages)