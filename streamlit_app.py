import streamlit as st
from datetime import datetime
from app.models import init_db, User
from app.expense_manager import ExpenseManager
from app.budget_manager import BudgetManager
from app.group_manager import GroupManager
from sqlalchemy.exc import IntegrityError
import pandas as pd
import matplotlib.pyplot as plt

# Initialize DB
db = init_db()

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

# --- Registration Form ---
def registration_form():
    st.subheader("📝 Register")
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if username and email and password:
            try:
                user = User(username=username, email=email, password=password)
                db.add(user)
                db.commit()
                st.success("✅ User registered! You can now log in.")
            except IntegrityError:
                db.rollback()
                st.error("Username or Email already exists.")
        else:
            st.warning("Please fill in all fields.")

# --- Login Form ---
def login_form():
    st.subheader("🔐 Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", key="login_pass", type="password")

    if st.button("Login"):
        user = db.query(User).filter_by(username=username, password=password).first()
        if user:
            st.session_state.logged_in = True
            st.session_state.user = user
            st.success(f"Welcome, {user.username}!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")

# --- Auth UI ---
if not st.session_state.logged_in:
    option = st.sidebar.radio("Account", ["Login", "Register"])
    if option == "Login":
        login_form()
    else:
        registration_form()
    st.stop()

# --- Logout ---
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# --- Logged-in user context ---
user = st.session_state.user
expense_manager = ExpenseManager(db, user)
budget_manager = BudgetManager(db, user)
group_manager = GroupManager(db, user)

# --- Sidebar Navigation ---
st.sidebar.title("Navigation")
menu = st.sidebar.radio("Go to", ["💸 Add Expense", "📊 Reports", "📅 Set Budget", "👥 Group Expenses"])

# 💸 Add Expense
if menu == "💸 Add Expense":
    st.title("Add New Expense")
    amount = st.number_input("Amount", min_value=0.0, step=1.0)
    category = st.text_input("Category")
    description = st.text_area("Description")
    date = st.date_input("Date", datetime.today())

    if st.button("Add Expense"):
        expense_manager.add_expense(amount, category, description, date)
        st.success("Expense added successfully!")

# 📊 Reports
elif menu == "📊 Reports":
    st.title("Monthly Report")
    year = st.number_input("Year", value=datetime.today().year)
    month = st.number_input("Month", min_value=1, max_value=12, value=datetime.today().month)

    st.subheader(f"Total Spending - {month}/{year}")
    total = expense_manager.get_monthly_spending(year, month)
    st.metric(label="Total Spent", value=f"₹{total:.2f}")

    st.subheader("Spending by Category")
    data = expense_manager.get_category_spending(year, month)
    if data:
        for d in data:
            st.write(f"**{d.name}**: ₹{d.total:.2f} / ₹{d.budget if d.budget else 'No Budget Set'}")
    else:
        st.info("No expenses found for this month.")

# 📅 Set Budget
elif menu == "📅 Set Budget":
    st.title("Set Monthly Budget")
    category = st.text_input("Category")
    amount = st.number_input("Budget Amount", min_value=0.0, step=1.0)
    year = st.number_input("Year", value=datetime.today().year)
    month = st.number_input("Month", min_value=1, max_value=12, value=datetime.today().month)
    threshold = st.slider("Alert Threshold (%)", 10, 100, 90)

    if st.button("Set Budget"):
        budget_manager.set_budget(category, amount, year, month, alert_threshold=threshold)
        st.success("Budget saved!")

    st.subheader("Your Budgets")
    for b in budget_manager.get_budgets(year, month):
        st.write(f"**{b.category}**: ₹{b.amount:.2f}, Alert at {b.alert_threshold}%")

elif menu == "👥 Group Expenses":
    st.title("👥 Group Expenses")

    # --- Create Group ---
    with st.expander("➕ Create New Group"):
        new_group_name = st.text_input("Group Name")
        if st.button("Create Group"):
            try:
                group_manager.create_group(new_group_name)
                st.success(f"Group '{new_group_name}' created successfully!")
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error creating group: {e}")

    groups = group_manager.get_user_groups()
    if not groups:
        st.warning("You are not part of any groups.")
        st.stop()

    group_names = [g.name for g in groups]
    selected_group_name = st.selectbox("Select Group", group_names)
    group = next(g for g in groups if g.name == selected_group_name)

    # --- Add Member ---
    with st.expander("➕ Add Member to Group"):
        new_member_username = st.text_input("Enter username to add")
        if st.button("Add Member"):
            try:
                group_manager.add_member(group.id, new_member_username)
                st.success(f"User '{new_member_username}' added to group!")
                st.experimental_rerun()
            except Exception as e:
                st.error(str(e))

    # --- Group Balances ---
    st.subheader(f"💰 Balances in '{group.name}'")
    balances = group_manager.get_group_balances(group.id)
    for user, balance in balances.items():
        status = "🟢 Gets" if balance > 0 else "🔴 Owes"
        st.write(f"{user}: {status} ₹{abs(balance):.2f}")

    # --- Pie Chart for Balances ---
    st.subheader("📊 Expense Share Chart")
    # Filter out 0 values (optional)
    non_zero_balances = {user: amount for user, amount in balances.items() if amount != 0}

    if not non_zero_balances:
        st.info("No balance data to display in chart.")
    else:
        df = pd.DataFrame({
            'User': list(non_zero_balances.keys()),
            'Balance': list(non_zero_balances.values())
        })
        fig, ax = plt.subplots()
        ax.pie(df['Balance'], labels=df['User'], autopct='%1.1f%%', startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

    # --- Group Expense History ---
    st.subheader("🧾 Expense History")
    expenses = group_manager.get_group_expenses(group.id)
    if not expenses:
        st.info("No expenses recorded yet.")
    else:
        for e in expenses:
            st.write(f"📌 {e.description} | ₹{e.amount:.2f} | Paid by: {e.paid_by} | Shares: {e.num_shares}")

    # --- Add Group Expense Form ---
    st.subheader("➕ Add Shared Expense")
    amount = st.number_input("Amount", min_value=0.0)
    category = st.text_input("Category")
    description = st.text_input("Description")
    members = group_manager.get_group_members(group.id)
    paid_by = st.selectbox("Who paid?", members)
    split_evenly = st.checkbox("Split equally?", value=True)

    if not split_evenly:
        st.warning("Custom shares UI not yet supported — splitting equally.")

    if st.button("Add Group Expense"):
        try:
            group_manager.add_group_expense(
                group_id=group.id,
                amount=amount,
                category_name=category,
                description=description,
                paid_by_username=paid_by,
                shares=None
            )
            st.success("Group expense added!")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Error: {e}")
