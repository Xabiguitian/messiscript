from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel
from pydantic import BaseModel

class Message(BaseModel):
    detail: str

class FriendExpenseLink(SQLModel, table=True):
    friend_id: Optional[int] = Field(default=None, foreign_key="friend.id", primary_key=True)
    expense_id: Optional[int] = Field(default=None, foreign_key="expense.id", primary_key=True)
    amount: float = Field(default=0)

    friend: "Friend" = Relationship(back_populates="expense_links")
    expense: "Expense" = Relationship(back_populates="friend_links")

class Friend(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    expense_links: List["FriendExpenseLink"] = Relationship(back_populates="friend", cascade_delete=True)
    paid_expenses: List["Expense"] = Relationship(back_populates="payer")

class Expense(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    date: str
    amount: float
    payer_id: Optional[int] = Field(default=None, foreign_key="friend.id")
    payer: Optional["Friend"] = Relationship(back_populates="paid_expenses")
    friend_links: List["FriendExpenseLink"] = Relationship(back_populates="expense", cascade_delete=True)


class ExpenseCreate(BaseModel):
    description: str
    date: str
    amount: float
    payer_id: int
    participant_ids: list[int]

class FriendRead(BaseModel):
    id: int
    name: str

class FriendReadWithBalance(FriendRead):
    credit_balance: float = 0
    debit_balance: float = 0

class ExpenseReadWithDetails(BaseModel):
    id: int
    description: str
    date: str
    amount: float
    payer_id: Optional[int] = None
    payer: Optional[FriendRead] = None
    friend_links: List[FriendExpenseLink] = []

class FriendExpense(BaseModel):
    id: int
    description: str
    amount: float
    num_friends: int
    credit_balance: float
    debit_balance: float