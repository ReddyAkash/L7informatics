# 💸 Personal & Group Expense Tracker

A full-stack Expense Tracker web application built with **Streamlit**, **SQLAlchemy**, and **Docker**.

This app allows users to:
- 🔐 Register & login
- 💰 Log and categorize daily expenses
- 📅 Set monthly budgets with alert thresholds
- 📧 Receive email alerts when budget exceeds
- 👥 Create groups and split expenses (like Splitwise)
- 📊 View reports with charts and category-wise breakdowns
- 🐳 Run the entire project using Docker

---

## 📸 Screenshots

### 🔐 Main Features

| Registration Page | Login Page | Adding Expense 1 | Adding Expense 2 | Monthly Report |
|-------------------|------------|------------------|------------------|----------------|
| ![Register](screenshots/register.png) | ![Login](screenshots/login.png) | ![AddExpenses1](screenshots/addexpense1.png) | ![AddExpenses2](screenshots/addexpense2.png) | ![MonthlyReport](screenshots/monthlyreport.png) |

---

### 👥 Group Expenses Features

| Group Page 1 | Group Page 2 | Group Page 3 | Group Page 4 | Group Page 5 |
|--------------|--------------|--------------|--------------|--------------|
| ![Group1](screenshots/group1.png) | ![Group2](screenshots/group2.png) | ![Group3](screenshots/group3.png) | ![Group4](screenshots/group4.png) | ![Group5](screenshots/group5.png) |

 ### 📧 Alert mail for completion of 90% alloted budget
 ![Alert](screenshots/alertmail.png)

---

## 📦 Technologies Used

- [Streamlit](https://streamlit.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [SQLite](https://www.sqlite.org/)
- [Docker](https://www.docker.com/)
- [Matplotlib](https://matplotlib.org/)
- [Python 3.10](https://www.python.org/)

---


### 1️⃣ Clone the repository

```bash
git clone https://github.com/ReddyAkash/L7informatics.git
cd L7informatics

```

### 2️⃣ Create virtual environment and activate it

```bash
python -m venv venv

# For Windows:
venv\Scripts\activate

# For macOS/Linux:
source venv/bin/activate

```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the app locally if required.

```bash
streamlit run streamlit_app.py
🖥️ App will be live at: http://localhost:8501

```

### 🐳 Docker Setup to run application in container
   
   ### 1️⃣ Build the Docker image
```bash
docker build -t expense-tracker-app .
```
![Docker](screenshots/docker-image.png)
 ### 2️⃣ Run the Docker container
```bash
docker run -p 8501:8501 expense-tracker-app.
```
![Docker](screenshots/docker-container.png)

### Persist SQLite DB
```bash
docker run -p 8501:8501 -v ${PWD}/data:/app/data expense-tracker-app
```
Make sure your models.py contains:
```bash
sqlite:///data/expenses.db
🖥️ App will be live at: http://localhost:8501
```

When the app runs inside Docker, it saves data (like user info, expenses, budgets) to expenses.db.

By default, this would be lost once the container stops.

This command binds that database location (/app/data) to the local folder (./data/), so the file is saved on the actual machine.


### 🧠 Core Project File Overview
| File | Description |
|------|-------------|
| `streamlit_app.py` | Main Streamlit UI for user interaction |
| `app/models.py` | SQLAlchemy ORM models |
| `app/expense_manager.py` | Manages personal expenses |
| `app/budget_manager.py` | Handles budgets & alerts |
| `app/group_manager.py` | Group creation, expense sharing |
| `app/notifier.py` | Email alert notifications |
| `Dockerfile` | Docker build instructions |
| `requirements.txt` | Project dependencies |
| `screenshots/` | Images for README and app preview |

### 📬 Email Alert Setup
```bash
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-app-password
```
Make sure to switch on the 2 step verification and create an app password which will be used as a sender password.
![AppPassword](screenshots/appPassword.png)
📌 Use Gmail App Passwords if 2FA is already  enabled.

### ✅ Completed Features
```bash
 User Registration & Login

 Daily Expense Logging

 Monthly Budgets with Alerts

 Email Notifications

 Group Expense Management

 Visual Reports

 Docker Support

 Persistent Database

```

### 🙌 Author
Akash Reddy
🔗 GitHub: @ReddyAkash

### ⭐ Like this Project?
If you found this project helpful, give it a ⭐ and share it!

Made using Python, Streamlit & Docker.