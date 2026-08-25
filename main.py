from fastapi import FastAPI
from fastapi.responses import JSONResponse
import re
import json
import google_crc32c

app = FastAPI()
URI_RE = re.compile(r"^gs://[^/]+/.+$")
GEN_RE = re.compile(r"^[0-9]+$")
CRC_RE = re.compile(r"^[0-9a-f]{8}$")

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/build-corpus")
async def build_corpus(payload: dict):

    if (
        not isinstance(payload, dict)
        or "policy" not in payload
        or "objects" not in payload
        or not isinstance(payload["objects"], list)
    ):
        return JSONResponse(
            status_code=400,
            content={"error": "INVALID_INPUT"}
        )

    rejected_objects = []
    lineage = []

    return {
        "splits": {
            "train": [],
            "validation": [],
            "test": []
        },
        "rejectedObjects": [],
        "rejectedRows": [],
        "digests": {
            "train": "",
            "validation": "",
            "test": ""
        },
        "lineage": []
        
    }
