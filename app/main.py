from fastapi import FastAPI

from app.database import engine, Base
from app.api.account_api import router as account_router

from app.domain.account_balance import AccountBalance
from app.domain.customer import Customer
from app.domain.account import Account

app = FastAPI(title="AI Powered Banking service")

app.include_router(account_router)
Base.metadata.create_all(engine)

@app.get("/")
def health_check():
    return {"status": "Banking AI service is running"}
