from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    
    expenses = relationship("Expense", back_populates="user")
    budgets = relationship("Budget", back_populates="user")
    groups = relationship("GroupMember", back_populates="user")

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    expenses = relationship("Expense", back_populates="category")
    budgets = relationship("Budget", back_populates="category")

class Expense(Base):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    description = Column(String)
    date = Column(Date, default=datetime.now().date)
    
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="expenses")
    
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="expenses")
    
    group_expense_id = Column(Integer, ForeignKey('group_expenses.id'), nullable=True)
    group_expense = relationship("GroupExpense", back_populates="expenses")

class Budget(Base):
    __tablename__ = 'budgets'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    alert_threshold = Column(Float, default=90.0)  # Default alert at 90% of budget
    
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="budgets")
    
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship("Category", back_populates="budgets")

class Group(Base):
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    
    members = relationship("GroupMember", back_populates="group")
    expenses = relationship("GroupExpense", back_populates="group")

class GroupMember(Base):
    __tablename__ = 'group_members'
    
    id = Column(Integer, primary_key=True)
    
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="groups")
    
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship("Group", back_populates="members")

class GroupExpense(Base):
    __tablename__ = 'group_expenses'
    
    id = Column(Integer, primary_key=True)
    description = Column(String)
    date = Column(Date, default=datetime.now().date)
    
    group_id = Column(Integer, ForeignKey('groups.id'))
    group = relationship("Group", back_populates="expenses")
    
    expenses = relationship("Expense", back_populates="group_expense")
    shares = relationship("ExpenseShare", back_populates="group_expense")

class ExpenseShare(Base):
    __tablename__ = 'expense_shares'
    
    id = Column(Integer, primary_key=True)
    amount = Column(Float, nullable=False)
    paid = Column(Boolean, default=False)
    
    user_id = Column(Integer, ForeignKey('users.id'))
    
    group_expense_id = Column(Integer, ForeignKey('group_expenses.id'))
    group_expense = relationship("GroupExpense", back_populates="shares")

# Database setup function
def init_db(db_path='sqlite:///expenses.db'):
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()
