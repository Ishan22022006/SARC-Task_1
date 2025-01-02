from fastapi import FastAPI, HTTPException
from typing import List, Optional
from pydantic import BaseModel

app = FastAPI()

# Model to record Budget based requests: 
class Budget(BaseModel):
    user: str
    amount: float

# Model to record Transactions based requests:
class Transaction(BaseModel):
    user: str
    description: Optional[str] = None
    amount: float
    credit: Optional[bool] = False
    debit: Optional[bool] = False

# Temporary in memory data-base: 
budgets = {}
transactions = []


# CRUD operations are as follows: 

# C: Create - This request creats a new user in data-base
@app.post("/budget/", response_model=Budget)
def create_budget(budget: Budget):
    if budget.user in budgets:
        raise HTTPException(status_code=400, detail="Budget for this user already exists.")
    budgets[budget.user] = budget.amount
    return budget

# R: Read - This request allows to fetch data of particular user
@app.get("/budget/{user}", response_model=Budget)
def get_budget(user: str):
    if user not in budgets:
        raise HTTPException(status_code=404, detail="Budget not found.")
    return {"user": user, "amount": budgets[user]}

# U: Update - This request allows us to update the amount of particular user
@app.put("/budget/{user}", response_model=Budget)
def update_budget(user: str, budget: Budget):
    if user not in budgets:
        raise HTTPException(status_code=404, detail="Budget not found.")
    budgets[user] = budget.amount
    return budget

# D: Delete - This request allows us to dalete details of particular user
@app.delete("/budget/{user}")
def delete_budget(user: str):
    if user not in budgets:
        raise HTTPException(status_code=404, detail="Budget not found.")
    del budgets[user]
    return {"detail": "Budget deleted successfully."}

# This request allows us to debit money from our account
@app.post("/transactions/debit/", response_model=Transaction)
def credit_amount(transaction: Transaction):
    if transaction.user not in budgets:
        raise HTTPException(status_code=404, detail="Budget for this user does not exist.")

    if transaction.amount > budgets[transaction.user]:
        raise HTTPException(status_code=400, detail="Transaction amount exceeds the budget.")

    budgets[transaction.user] -= transaction.amount
    transaction.debit = True
    transactions.append(transaction)
    return transaction

# This request allows us to credit money in our account
@app.post("/transactions/credit/", response_model=Transaction)
def debit_amount(transaction: Transaction):
    if transaction.user not in budgets:
        raise HTTPException(status_code=404, detail="Budget for this user does not exist.")
    
    budgets[transaction.user] += transaction.amount
    transaction.credit = True
    transactions.append(transaction)
    return transaction

# R: Read - This request allows us to get details of our transaction history
@app.get("/transactions/{user}", response_model=List[Transaction])
def get_transactions(user: str):
    user_transactions = [t for t in transactions if t.user == user]
    if not user_transactions:
        raise HTTPException(status_code=404, detail="No transactions found for this user.")
    return user_transactions

# To use this, type the following command on terminal:
# uvicorn main:app --reload