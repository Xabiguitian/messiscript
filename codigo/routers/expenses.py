from fastapi import APIRouter, Depends, HTTPException
from persistence.database import get_session
from persistence.models import Message, Friend, Expense, FriendExpenseLink, ExpenseCreate, ExpenseReadWithDetails
from sqlmodel import Session, select, func
from datetime import datetime
from typing import List

router = APIRouter(
    prefix = "/expenses",
    tags=["expenses"]
)

def is_valid_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

@router.post("/",
          status_code=201,
          response_model=Expense,
          responses={
              201: {"model": Expense},
              409: {"model": Message},
              404: {"model": Message},
              422: {"model": Message}
          })
def add_expense(expense_data: ExpenseCreate, session: Session = Depends(get_session)) -> Expense:
    if not is_valid_date(expense_data.date):
        raise HTTPException(status_code=422, detail=f"Malformed date '{expense_data.date}' (required format: YYYY-MM-DD)")

    payer = session.get(Friend, expense_data.payer_id)
    if not payer:
        raise HTTPException(status_code=404, detail=f"Payer friend with id '{expense_data.payer_id}' not found")

    if not expense_data.participant_ids:
         raise HTTPException(status_code=422, detail="Participant list cannot be empty")

    for p_id in expense_data.participant_ids:
        if not session.get(Friend, p_id):
             raise HTTPException(status_code=404, detail=f"Participant friend with id '{p_id}' not found")

    if expense_data.payer_id not in expense_data.participant_ids:
         raise HTTPException(status_code=422, detail="Payer must be included in the participant list")

    new_expense = Expense(
        description=expense_data.description,
        date=expense_data.date,
        amount=expense_data.amount,
        payer_id=expense_data.payer_id
    )
    session.add(new_expense)
    session.commit()
    session.refresh(new_expense)

    amount_paid_by_payer = expense_data.amount
    for p_id in expense_data.participant_ids:
        credit_amount = amount_paid_by_payer if p_id == expense_data.payer_id else 0
        link = FriendExpenseLink(
            expense_id=new_expense.id,
            friend_id=p_id,
            amount=credit_amount
        )
        session.add(link)

    session.commit()
    session.refresh(new_expense)
    return new_expense

@router.get("/{expense_id}",
         response_model=ExpenseReadWithDetails,
         responses={200: {"model": ExpenseReadWithDetails}, 404: {"model": Message}})
def get_expense(expense_id: int, session: Session = Depends(get_session)) -> Expense:
    expense = session.get(Expense, expense_id)
    if expense is not None:
        return expense
    else:
        raise HTTPException(status_code=404, detail=f"Expense '{expense_id}' not found")


@router.get("/",
         response_model=List[ExpenseReadWithDetails],
         responses={200: {"model": List[ExpenseReadWithDetails]}})
def get_expenses(session: Session = Depends(get_session)) -> List[Expense]:
    expenses = session.exec(select(Expense)).all()
    return expenses

@router.put("/{expense_id}",
         status_code=204,
         responses={404: {"model": Message}, 422: {"model": Message}})
def update_expense(expense_id: int, expense_update: ExpenseCreate, session: Session = Depends(get_session)):
    if not is_valid_date(expense_update.date):
        raise HTTPException(status_code=422, detail=f"Malformed date '{expense_update.date}' (required format: YYYY-MM-DD)")

    stored_expense = session.get(Expense, expense_id)
    if stored_expense is None:
        raise HTTPException(status_code=404, detail=f"Expense {expense_id} not found")

    if not session.get(Friend, expense_update.payer_id):
        raise HTTPException(status_code=404, detail=f"Payer friend with id '{expense_update.payer_id}' not found")

    if not expense_update.participant_ids:
         raise HTTPException(status_code=422, detail="Participant list cannot be empty")

    new_participant_ids = set(expense_update.participant_ids)
    for p_id in new_participant_ids:
        if not session.get(Friend, p_id):
             raise HTTPException(status_code=404, detail=f"Participant friend with id '{p_id}' not found")

    if expense_update.payer_id not in new_participant_ids:
         raise HTTPException(status_code=422, detail="Payer must be included in the participant list")

    stored_expense.description = expense_update.description
    stored_expense.date = expense_update.date
    stored_expense.amount = expense_update.amount
    
    current_participant_links = session.exec(select(FriendExpenseLink).where(FriendExpenseLink.expense_id == expense_id)).all()
    current_participant_ids = {link.friend_id for link in current_participant_links}

    ids_to_add = new_participant_ids - current_participant_ids
    links_to_remove = [link for link in current_participant_links if link.friend_id not in new_participant_ids]

    for link in links_to_remove:
         if link.amount != 0 and link.friend_id != stored_expense.payer_id:
              raise HTTPException(status_code=409, detail=f"Cannot remove participant {link.friend_id} with non-zero credit ({link.amount})")
         session.delete(link)

    for p_id in ids_to_add:
         link = FriendExpenseLink(expense_id=expense_id, friend_id=p_id, amount=0)
         session.add(link)
    
    session.flush()

    for link in session.exec(select(FriendExpenseLink).where(FriendExpenseLink.expense_id == expense_id)).all():
        if link.friend_id == expense_update.payer_id:
            link.amount = expense_update.amount
        else:
            link.amount = 0
            
    stored_expense.payer_id = expense_update.payer_id
    session.commit()

@router.delete("/{expense_id}",
         status_code=204,
         responses={404: {"model": Message}})
def delete_expense(expense_id: int, session: Session = Depends(get_session)):
    stored_expense = session.get(Expense, expense_id)
    if stored_expense is not None:
        session.delete(stored_expense)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail=f"Expense '{expense_id}' not found")