from sqlalchemy.sql import func
from .models import Group, GroupMember, GroupExpense, ExpenseShare, Expense, User

class GroupManager:
    def __init__(self, db_session, user):
        self.db_session = db_session
        self.user = user
    
    def create_group(self, group_name):
       """Create a new expense sharing group"""
       group = Group(name=group_name)
       self.db_session.add(group)
    
       # Add creator as a member
       member = GroupMember(user=self.user, group=group)
       self.db_session.add(member)
    
       self.db_session.commit()
       return group

def add_member(self, group_id, username):
    """Add a member to the group"""
    group = self.db_session.query(Group).get(group_id)
    if not group:
        raise ValueError("Group not found")
        
    # Check if user is already a member
    user = self.db_session.query(User).filter(User.username == username).first()
    if not user:
        raise ValueError(f"User {username} not found")
        
    existing_member = self.db_session.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == user.id
    ).first()
    
    if existing_member:
        raise ValueError(f"User {username} is already a member of this group")
        
    # Add new member
    member = GroupMember(user=user, group=group)
    self.db_session.add(member)
    self.db_session.commit()
    
    return member

def add_group_expense(self, group_id, amount, category_name, description, paid_by_username, shares=None):
    """
    Add a shared expense to the group
    shares: dict mapping usernames to share amounts or percentages
    """
    group = self.db_session.query(Group).get(group_id)
    if not group:
        raise ValueError("Group not found")
        
    # Get the user who paid
    paid_by_user = self.db_session.query(User).filter(User.username == paid_by_username).first()
    if not paid_by_user:
        raise ValueError(f"User {paid_by_username} not found")
        
    # Create the group expense
    group_expense = GroupExpense(
        description=description,
        group=group
    )
    self.db_session.add(group_expense)
    
    # Create the main expense for the paying user
    from .expense_manager import ExpenseManager
    expense_manager = ExpenseManager(self.db_session, paid_by_user)
    expense = expense_manager.add_expense(amount, category_name, description)
    expense.group_expense = group_expense
    
    # If no specific shares provided, split equally among all members
    if not shares:
        members = self.db_session.query(GroupMember).filter(
            GroupMember.group_id == group_id
        ).all()
        
        share_amount = amount / len(members)
        shares = {member.user.username: share_amount for member in members}
        
    # Create expense shares
    for username, share_amount in shares.items():
        if username == paid_by_username:
            continue  # Skip the payer
            
        user = self.db_session.query(User).filter(User.username == username).first()
        if not user:
            continue
            
        share = ExpenseShare(
            amount=share_amount,
            user_id=user.id,
            group_expense=group_expense,
            paid=False
        )
        self.db_session.add(share)
        
    self.db_session.commit()
    return group_expense

def get_user_groups(self):
    """Get all groups the user is a member of"""
    groups = self.db_session.query(Group)\
        .join(GroupMember, GroupMember.group_id == Group.id)\
        .filter(GroupMember.user_id == self.user.id)\
        .all()
        
    return groups

def get_group_balances(self, group_id):
    """Get all balances within a group"""
    # Check if group exists and user is a member
    group = self.db_session.query(Group).get(group_id)
    if not group:
        raise ValueError("Group not found")
        
    is_member = self.db_session.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == self.user.id
    ).first()
    
    if not is_member:
        raise ValueError("You are not a member of this group")
    
    # Get all members in the group
    members = self.db_session.query(User.id, User.username)\
        .join(GroupMember, GroupMember.user_id == User.id)\
        .filter(GroupMember.group_id == group_id)\
        .all()
        
    member_dict = {id: username for id, username in members}
    
    # Calculate what each person has paid
    paid_amounts = {}
    for user_id, username in members:
        paid = self.db_session.query(func.sum(Expense.amount))\
            .join(GroupExpense, GroupExpense.id == Expense.group_expense_id)\
            .filter(
                GroupExpense.group_id == group_id,
                Expense.user_id == user_id
            ).scalar() or 0
            
        paid_amounts[username] = paid
        
    # Calculate what each person owes
    owed_amounts = {}
    for user_id, username in members:
        owed = self.db_session.query(func.sum(ExpenseShare.amount))\
            .filter(
                ExpenseShare.user_id == user_id,
                ExpenseShare.paid == False
            ).scalar() or 0
            
        owed_amounts[username] = owed
        
    # Calculate net balances
    balances = {}
    for username in member_dict.values():
        balances[username] = paid_amounts.get(username, 0) - owed_amounts.get(username, 0)
        
    return balances

def mark_expense_as_paid(self, share_id):
    """Mark an expense share as paid"""
    share = self.db_session.query(ExpenseShare).get(share_id)
    if not share:
        raise ValueError("Expense share not found")
        
    # Check if the current user is involved in this expense
    group_expense = share.group_expense
    group = group_expense.group
    
    is_member = self.db_session.query(GroupMember).filter(
        GroupMember.group_id == group.id,
        GroupMember.user_id == self.user.id
    ).first()
    
    if not is_member:
        raise ValueError("You are not authorized to modify this expense")
        
    share.paid = True
    self.db_session.commit()
    return share

def get_group_expenses(self, group_id):
    """Get all expenses for a specific group"""
    # Check if group exists and user is a member
    is_member = self.db_session.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == self.user.id
    ).first()
    
    if not is_member:
        raise ValueError("You are not a member of this group")
        
    expenses = self.db_session.query(
        GroupExpense.id,
        GroupExpense.description,
        GroupExpense.date,
        User.username.label('paid_by'),
        Expense.amount,
        func.count(ExpenseShare.id).label('num_shares')
    ).join(Expense, Expense.group_expense_id == GroupExpense.id)\
     .join(User, User.id == Expense.user_id)\
     .outerjoin(ExpenseShare, ExpenseShare.group_expense_id == GroupExpense.id)\
     .filter(GroupExpense.group_id == group_id)\
     .group_by(GroupExpense.id, User.username, Expense.amount)\
     .order_by(GroupExpense.date.desc())\
     .all()
     
    return expenses

def get_group_members(self, group_id):
    """Get all members of a specific group"""
    members = self.db_session.query(User.username)\
        .join(GroupMember, GroupMember.user_id == User.id)\
        .filter(GroupMember.group_id == group_id)\
        .all()
        
    return [member for member in members]

def delete_group(self, group_id):
    """Delete a group if the current user is a member"""
    group = self.db_session.query(Group).get(group_id)
    if not group:
        raise ValueError("Group not found")
        
    # Check if user is a member
    is_member = self.db_session.query(GroupMember).filter(
        GroupMember.group_id == group_id,
        GroupMember.user_id == self.user.id
    ).first()
    
    if not is_member:
        raise ValueError("You are not a member of this group")
        
    # Delete all related records
    self.db_session.query(ExpenseShare)\
        .filter(ExpenseShare.group_expense_id.in_(
            self.db_session.query(GroupExpense.id).filter(GroupExpense.group_id == group_id)
        ))\
        .delete(synchronize_session=False)
        
    self.db_session.query(Expense)\
        .filter(Expense.group_expense_id.in_(
            self.db_session.query(GroupExpense.id).filter(GroupExpense.group_id == group_id)
        ))\
        .delete(synchronize_session=False)
        
    self.db_session.query(GroupExpense)\
        .filter(GroupExpense.group_id == group_id)\
        .delete(synchronize_session=False)
        
    self.db_session.query(GroupMember)\
        .filter(GroupMember.group_id == group_id)\
        .delete(synchronize_session=False)
        
    self.db_session.delete(group)
    self.db_session.commit()
    
    return True
