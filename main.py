from fastapi import FastAPI
from routers import main_routes
from middleware.timer_middleware import TimerMiddleware


app = FastAPI()

# log와 monitoring을 위한 middleware 추가
app.add_middleware(TimerMiddleware)

app.include_router(main_routes.router, prefix='/main', tags=['main'])
