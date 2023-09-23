from fastapi import FastAPI
from redis import Redis
from rq import Queue
from pydantic import BaseModel
from job import print_num


app = FastAPI()
redis_queue = Redis(host="192.168.0.18", port=6379)
task_queue = Queue("task_queue", connection=redis_queue)

class JobData(BaseModel):
    lowest : int
    highest : int

@app.get('/')
def index():
    return {
        "success": True,
        "message": "pong"
    }

@app.post('/job')
def post_job(job: JobData):
    lowest = job.lowest
    highest = job.highest
    job_instance = task_queue.enqueue(print_num, lowest, highest)
    return{
        "success": True,
        "job_id": job_instance.id
    }


