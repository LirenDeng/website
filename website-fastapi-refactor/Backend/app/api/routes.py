from fastapi import APIRouter
from app.services.put_call import get_put_call_data

router = APIRouter()

@router.get("/putcall")
def putcall():
    # returns JSON {dte: [...], ratio: [...]}
    return get_put_call_data()
