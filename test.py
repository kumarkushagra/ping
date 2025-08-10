# server.py
from fastapi import FastAPI, Request
import uvicorn
import csv
import os

app = FastAPI()
stack = []  # in-memory stack
csv_file = "stack.csv"

# Load existing IDs from CSV into memory at startup (if file exists)
if os.path.exists(csv_file):
    with open(csv_file, "r", newline="") as f:
        reader = csv.reader(f)
        stack = [row[0] for row in reader if row]  # first column only
    print(f"Loaded {len(stack)} IDs from CSV.")

@app.post("/queue")
async def enqueue_doc(request: Request):
    data = await request.json()
    doc_id = data.get("id")

    if not doc_id:
        return {"error": "Missing 'id'"}

    stack.append(doc_id)

    # Append to CSV file
    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([doc_id])

    print(f"Queued: {doc_id}")
    return {"status": "queued", "id": doc_id}

@app.get("/stack")
def get_stack():
    return {"stack": stack}



if __name__=="__main__":
    uvicorn.run("test:app", host="0.0.0.0", port = 2000)