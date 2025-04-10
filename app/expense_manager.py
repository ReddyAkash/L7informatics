from datetime import datetime
from sqlalchemy.sql import func
from app.models import Expense, Category, Budget
from app.notifier import Notifier

class ExpenseManager:
    def __init__(self, db_session, user):
        self.db_session = db_session
        self.user = user
        self.notifier = Notifier()
        
    def add_expense(self, amount, category_name, description="", date=None):
        """Add a new expense and check budget limits"""
        category = self._get_or_create_category(category_name)
        
        if date is None:
            date = datetime.now().date()
        
        # Create and save the expense
        expense = Expense(
            amount=amount,
            description=description,
            user_id=self.user.id,
            category_id=category.id,
            date=date
        )
        self.db_session.add(expense)
        self.db_session.commit()
        
        # Check budget after adding expense
        self._check_budget_limits(category, date.year, date.month)
        
        return expense
    
    def _get_or_create_category(self, category_name):
        """Get existing category or create a new one"""
        category = self.db_session.query(Category).filter(
            func.lower(Category.name) == category_name.lower()
        ).first()
        
        if not category:
            category = Category(name=category_name)
            self.db_session.add(category)
            self.db_session.commit()
            
        return category
    
    def _check_budget_limits(self, category, year, month):
        """Check if user has exceeded budget limits and send alerts"""
        # Get current budget for this category and month
        budget = self.db_session.query(Budget).filter(
            Budget.user_id == self.user.id,
            Budget.category_id == category.id,
            Budget.month == month,
            Budget.year == year
        ).first()
        
        if not budget:
            return  # No budget set for this category
        
        # Calculate total spending for this category in current month
        total_spent = self.db_session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == self.user.id,
            Expense.category_id == category.id,
            func.extract('month', Expense.date) == month,
            func.extract('year', Expense.date) == year
        ).scalar() or 0
        
        # Check if exceeded budget
        if total_spent > budget.amount:
            self.notifier.send_alert(
                self.user,
                f"Budget Exceeded for {category.name}",
                f"You've spent ${total_spent:.2f} out of ${budget.amount:.2f} budget for {category.name}."
            )
        # Check if approaching budget threshold
        elif total_spent >= (budget.amount * budget.alert_threshold / 100):
            remaining = budget.amount - total_spent
            percentage_used = (total_spent / budget.amount) * 100
            self.notifier.send_alert(
                self.user,
                f"Budget Alert for {category.name}",
                f"You've used {percentage_used:.1f}% of your budget for {category.name}. "
                f"${remaining:.2f} remaining."
            )
    
    def get_monthly_spending(self, year, month):
        """Get total spending for a specific month"""
        total = self.db_session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == self.user.id,
            func.extract('year', Expense.date) == year,
            func.extract('month', Expense.date) == month
        ).scalar() or 0
        
        return total
    
    def get_category_spending(self, year, month, category_name=None):
        """Get spending by category for a specific month"""
        query = self.db_session.query(
            Category.name,
            func.sum(Expense.amount).label('total'),
            Budget.amount.label('budget')
        ).join(Expense, Expense.category_id == Category.id)\
         .outerjoin(Budget, (Budget.category_id == Category.id) & 
                           (Budget.user_id == self.user.id) &
                           (Budget.month == month) &
                           (Budget.year == year))\
         .filter(
            Expense.user_id == self.user.id,
            func.extract('year', Expense.date) == year,
            func.extract('month', Expense.date) == month
         ).group_by(Category.name, Budget.amount)
        
        if category_name:
            query = query.filter(func.lower(Category.name) == category_name.lower())
            
        return query.all()
        
    def get_all_expenses(self, year=None, month=None, category_name=None):
        """Get all expenses with optional filtering"""
        query = self.db_session.query(
            Expense.id,
            Expense.amount,
            Expense.description,
            Expense.date,
            Category.name.label('category')
        ).join(Category, Expense.category_id == Category.id)\
         .filter(Expense.user_id == self.user.id)
        
        if year:
            query = query.filter(func.extract('year', Expense.date) == year)
        
        if month:
            query = query.filter(func.extract('month', Expense.date) == month)
            
        if category_name:
            query = query.filter(func.lower(Category.name) == category_name.lower())
            
        return query.order_by(Expense.date.desc()).all()
        
    def delete_expense(self, expense_id):
        """Delete an expense by ID"""
        expense = self.db_session.query(Expense).filter(
            Expense.id == expense_id,
            Expense.user_id == self.user.id
        ).first()
        
        if expense:
            self.db_session.delete(expense)
            self.db_session.commit()
            return True
        return False
