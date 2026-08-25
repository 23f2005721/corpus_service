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

    for obj in payload["objects"]:

        reasons = []

        uri = obj.get("uri")
        generation = obj.get("generation")
        fetched = obj.get("fetchedGeneration")
        crc = obj.get("crc32c")
        schema = obj.get("schemaId")
        content = obj.get("content")

        if not isinstance(uri, str) or not URI_RE.fullmatch(uri):
            reasons.append("URI_INVALID")

        gen_valid = (
            isinstance(generation, str)
            and GEN_RE.fullmatch(generation)
        )

    fetched_valid = (
        isinstance(fetched, str)
        and GEN_RE.fullmatch(fetched)
        )

        if not gen_valid or not fetched_valid:
            reasons.append("GENERATION_INVALID")

        elif generation != fetched:
            reasons.append("GENERATION_MISMATCH")

        crc_valid = (
            isinstance(crc, str)
            and CRC_RE.fullmatch(crc)
        )

        if not crc_valid:
            reasons.append("CRC32C_INVALID")

        elif isinstance(content, str):

            actual_crc = f"{google_crc32c.value(content.encode('utf-8')):08x}"

            if actual_crc != crc:
                reasons.append("CRC32C_MISMATCH")

        if schema != "training-v1":
            reasons.append("SCHEMA_INVALID")

        if not isinstance(content, str):
            reasons.append("SCHEMA_INVALID")

        if isinstance(content, str):

            lines = [x for x in content.splitlines() if x.strip()]

        if len(lines) == 0:
            reasons.append("SCHEMA_INVALID")

        else:

            for line in lines:

                try:
                    row = json.loads(line)

                    if (
                        not isinstance(row, dict)
                        or set(row.keys())
                        != {
                            "id",
                            "entity",
                            "eventTime",
                            "revision",
                            "text",
                            }
                        ):
                        reasons.append("SCHEMA_INVALID")
                        break

                except Exception:
                    reasons.append("JSONL_INVALID")
                    break
        reasons = sorted(set(reasons))

        if reasons:

            rejected_objects.append(
            {
                "uri": uri if isinstance(uri, str) else None,
                "reasonCodes": reasons,
                }
            )

        else:

            lineage.append(
            {
                "uri": uri,
                "generation": generation,
                "crc32c": crc,
                "schemaId": schema,
                }
            )
        rejected_objects.sort(key=lambda x: str(x["uri"]))
        lineage.sort(key=lambda x: x["uri"])

        return {
            "splits": {
                "train": [],
                "validation": [],
                "test": []
            },
            "rejectedObjects": rejected_objects,
            "rejectedRows": [],
            "digests": {
                "train": "",
                "validation": "",
                "test": ""
            },
            "lineage": lineage
        }
        
    }
