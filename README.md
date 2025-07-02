Financia
---
A sleek, user-friendly personal finance tracker built with Flask. Add your expenses and income, and visualize your weekly and monthly financial activity with interactive charts — all from one secure dashboard.

Demo Video
---

Features
---
- Expense & Income Tracking: Log entries with amount, date, category, and notes
- Bar Chart Visualizations: Weekly and monthly charts using Chart.js
- Timeline View: Browse recent transactions and totals
- Secure User Auth: Login required for dashboard access
- Admin Panel: Role-based access for managing transactions
- Responsive UI: Clean, mobile-first layout using Bootstrap
- Financial Tips Panel (Post-login): Displays curated money-saving tips and economy updates

- Tech Stack
---

| Layer      | Tools Used                                  |
| ---------- | ------------------------------------------- |
| Frontend   | Bootstrap, Chart.js, JavaScript             |
| Backend    | Flask (Python), SQLite                      |
| Templating | Jinja2                                      |
| API        | Custom Flask routes for chart data          |
| Hosting    | To be deployed (Render/GitHub Pages) |

🔧 Installation & Local Setup
---

'''bash
---
    # 1. Clone the repo
    git clone https://github.com/Kabya002/Financia.git
    cd Financia
    # 2. Create a virtual environment
    python -m venv venv
    source venv/bin/activate  # on Windows: venv\Scripts\activate
    # 3. Install dependencies
    pip install -r requirements.txt
    # 4. Run the app
    flask run
    Access the app at: http://127.0.0.1:5000/

How to Use
---
1. Register and log in to the app
2. Add income or expense entries via the dashboard
3. View weekly and monthly bar charts
4. Explore transaction history and overall balance
5. Navigate through the dashboard tabs for summaries and tips

Folder Structure
---
/Financia
├── app.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   └── login.html
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── models.py
├── forms.py
├── requirements.txt
└── README.md

Auth & Access
---
1. Basic login system with user session tracking
2. Admin access allows editing/deleting entries
3. Flask-WTF used for form validation
