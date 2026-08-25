from fastapi import FastAPI, HTTPException

app = FastAPI()

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
        raise HTTPException(
            status_code=400,
            detail={"error": "INVALID_INPUT"}
        )

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
