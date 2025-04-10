from datetime import datetime
from sqlalchemy.sql import func
from app.models import Budget, Category

class BudgetManager:
    def __init__(self, db_session, user):
        self.db_session = db_session
        self.user = user
        
    def set_budget(self, category_name, amount, year=None, month=None, alert_threshold=90):
        """Set a budget for a specific category and month"""
        # Default to current month if not specified
        if year is None or month is None:
            today = datetime.now().date()
            year = year or today.year
            month = month or today.month
            
        category = self._get_or_create_category(category_name)
        
        # Check if budget already exists
        budget = self.db_session.query(Budget).filter(
            Budget.user_id == self.user.id,
            Budget.category_id == category.id,
            Budget.month == month,
            Budget.year == year
        ).first()
        
        if budget:
            # Update existing budget
            budget.amount = amount
            budget.alert_threshold = alert_threshold
        else:
            # Create new budget
            budget = Budget(
                amount=amount,
                year=year,
                month=month,
                alert_threshold=alert_threshold,
                user=self.user,
                category=category
            )
            self.db_session.add(budget)
            
        self.db_session.commit()
        return budget
    
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
    
    def get_budgets(self, year=None, month=None):
        """Get all budgets for a specific month"""
        # Default to current month if not specified
        if year is None or month is None:
            today = datetime.now().date()
            year = year or today.year
            month = month or today.month
            
        budgets = self.db_session.query(
            Category.name.label('category'),
            Budget.amount,
            Budget.alert_threshold
        ).join(Budget, Budget.category_id == Category.id)\
         .filter(
            Budget.user_id == self.user.id,
            Budget.month == month,
            Budget.year == year
         ).all()
            
        return budgets
        
    def delete_budget(self, category_name, year, month):
        """Delete a budget for a specific category and month"""
        category = self.db_session.query(Category).filter(
            func.lower(Category.name) == category_name.lower()
        ).first()
        
        if not category:
            return False
            
        budget = self.db_session.query(Budget).filter(
            Budget.user_id == self.user.id,
            Budget.category_id == category.id,
            Budget.month == month,
            Budget.year == year
        ).first()
        
        if budget:
            self.db_session.delete(budget)
            self.db_session.commit()
            return True
        return False
