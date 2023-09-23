import uvicorn
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)
