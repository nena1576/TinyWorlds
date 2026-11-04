# This defines all our actual API endpoints (the URLs people/browser hit).
# Each function here handles one request type (GET/POST/PUT/DELETE)
# and calls into database.py to do the real work.
from fastapi import APIRouter, HTTPException, Depends
from schemas.schemas import Art, ArtCreate, ArtUpdate
import database
from security import require_admin

router = APIRouter(prefix="/art", tags=["art"])

@router.get("")
def get_all_art():
    return {"art": database.get_all()}

@router.get("/export", dependencies=[Depends(require_admin)])
def export_art():
    filepath = database.export_to_json()
    return {"message": f"Exported to {filepath}"}

@router.get("/{art_id}")
def get_art(art_id: str):
    item = database.get_by_id(art_id)
    if not item:
        raise HTTPException(status_code=404, detail="Art not found")
    return item

@router.post("", dependencies=[Depends(require_admin)])
def save_art(art_data: ArtCreate):
    new_art = Art(**art_data.model_dump())
    return "artwork created successfully", database.create(new_art.model_dump())

@router.delete("/{art_id}", dependencies=[Depends(require_admin)])
def delete_art(art_id: str):
    deleted = database.delete(art_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Art not found")
    return {"message": "Art deleted successfully", "deleted_art": deleted}

@router.put("/{art_id}", dependencies=[Depends(require_admin)])
def update_art(art_id: str, updated_art: ArtUpdate):
    updated = database.update(art_id, updated_art.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail="Art not found")
    return {"message": "Art updated successfully", "updated_art": updated}

