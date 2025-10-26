from fastapi import APIRouter, Depends, HTTPException
from persistence.database import get_session
from persistence.models import Message, Friend, FriendExpenseLink, FriendExpense, FriendReadWithBalance
from sqlmodel import Session, select, func
from typing import List

router = APIRouter(
    prefix = "/friends",
    tags=["friends"]
)

@router.post("/",
          status_code=201,
          response_model=Friend,
          responses={201: {"model": Friend}, 409: {"model": Message}})
def add_friend(friend: Friend, session: Session = Depends(get_session)) -> Friend:
    existing_friend = session.exec(select(Friend).where(Friend.name == friend.name)).first()
    if existing_friend is None:
        session.add(friend)
        session.commit()
        session.refresh(friend)
        return friend
    else:
        raise HTTPException(status_code=409, detail="Friend with that name already exists")


def get_credit_balance(friend_id: int, session: Session) -> float:
    credit_balance = session.exec(select(func.sum(FriendExpenseLink.amount)).where(FriendExpenseLink.friend_id == friend_id)).first()
    return credit_balance if credit_balance is not None else 0

def get_debit_balance(friend_id: int, session: Session) -> float:
    expense_links = session.exec(select(FriendExpenseLink).where(FriendExpenseLink.friend_id == friend_id)).all()
    debit_balance = 0
    for expense_link in expense_links:
        expense = expense_link.expense
        if not expense: continue
        num_friends = len(expense.friend_links)
        if num_friends > 0:
            debit_balance += expense.amount / num_friends
    return debit_balance

@router.get("/{friend_id}",
         response_model=FriendReadWithBalance,
         responses={200: {"model": FriendReadWithBalance}, 404: {"model": Message}})
def get_friend(friend_id: int, session: Session = Depends(get_session)) -> FriendReadWithBalance:
    friend = session.get(Friend, friend_id)
    if friend is not None:
        credit = get_credit_balance(friend_id, session)
        debit = get_debit_balance(friend_id, session)
        return FriendReadWithBalance(id=friend.id, name=friend.name, credit_balance=credit, debit_balance=debit)
    else:
        raise HTTPException(status_code=404, detail=f"Friend '{friend_id}' not found")


@router.get("/{friend_id}/expenses", summary="Get Expenses by Friend",
         response_model=List[FriendExpense],
         responses={200: {"model": List[FriendExpense]}, 404: {"model": Message}})
def get_expenses_by_friend(friend_id: int, session: Session = Depends(get_session)) -> List[FriendExpense]:
    friend = session.get(Friend, friend_id)
    if friend is not None:
        friend_expenses = []
        for friend_expense_link in friend.expense_links:
            expense = friend_expense_link.expense
            if not expense: continue
            num_friends = len(expense.friend_links)
            if num_friends > 0:
                debit = expense.amount / num_friends
            else:
                debit = 0
            
            friend_expenses.append(FriendExpense(
                id=expense.id,
                description=expense.description,
                amount=expense.amount,
                num_friends=num_friends,
                credit_balance=friend_expense_link.amount,
                debit_balance=debit
            ))
        return friend_expenses
    else:
        raise HTTPException(status_code=404, detail=f"Friend '{friend_id}' not found")


@router.get("/",
         response_model=List[FriendReadWithBalance],
         responses={200: {"model": List[FriendReadWithBalance]}})
def get_friends(session: Session = Depends(get_session)) -> List[FriendReadWithBalance]:
    friends = session.exec(select(Friend)).all()
    friends_with_balance = []
    for friend in friends:
        credit = get_credit_balance(friend.id, session)
        debit = get_debit_balance(friend.id, session)
        friends_with_balance.append(FriendReadWithBalance(
            id=friend.id, name=friend.name, credit_balance=credit, debit_balance=debit
        ))
    return friends_with_balance

@router.put("/{friend_id}",
         status_code=204,
         responses={404: {"model": Message}})
def update_friend(friend_id: int, friend: Friend, session: Session = Depends(get_session)):
    stored_friend = session.get(Friend, friend_id)
    if stored_friend is not None:
        stored_friend.name = friend.name
        session.commit()
        session.refresh(stored_friend)
    else:
        raise HTTPException(status_code=404, detail=f"Friend '{friend_id}' not found")

@router.delete("/{friend_id}",
         status_code=204,
         responses={404: {"model": Message},
                    409: {"model": Message}})
def delete_friend(friend_id: int, session: Session = Depends(get_session)):
    stored_friend = session.get(Friend, friend_id)
    if stored_friend is not None:
        credit_balance = get_credit_balance(friend_id, session)
        if credit_balance == 0:
            session.delete(stored_friend)
            session.commit()
        else:
            raise HTTPException(status_code=409, detail=f"Credit balance of friend '{friend_id}' is not zero. Cannot delete.")
    else:
        raise HTTPException(status_code=404, detail=f"Friend '{friend_id}' not found")