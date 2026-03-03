## Smart Restaurant Management System (Smart RMS)

Production-ready **Restaurant Management System** web application built using:

- **Backend**: Python + Django (MVT)
- **Database**: SQL (PostgreSQL recommended; SQLite default for quick start; MySQL supported via `DATABASE_URL`)
- **Frontend**: HTML5 + CSS3 + Bootstrap 5 (responsive, clean UI)
- **Authentication**: Django built-in authentication + custom `User` model with staff roles

### Core Modules Implemented

- **Authentication & Staff Roles**: Admin / Manager / Waiter / Kitchen Staff / Cashier
- **Menu Management**: categories + items, availability toggle, image upload, search & filter
- **Table Management**: tables, capacity, status (Available/Occupied/Reserved)
- **Order Management**: create orders, add/remove items, update quantity, status tracking, totals
- **Kitchen Order Ticket (KOT)**: separate kitchen board with item-only view and ready updates
- **Billing**: invoice generation, configurable GST, discount, payment modes, print-friendly invoice
- **Inventory**: raw materials, suppliers, stock in/out movements, low stock alerts
- **Recipe-based Stock Deduction**: link recipes to menu items; validate stock; auto-deduct on payment
- **Daily Closing Report**: sales summary, payment breakdown, expenses, net profit, PDF export

### Database Design / ERD

See `docs/ERD.md` for entity relationships, 3NF notes, and indexing.

### Sample SQL Queries

See `docs/sample_queries.sql`.

---

## Local Setup (Windows / SQLite quick start)

Open PowerShell in this folder (`smart_rms/`) and run:

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py loaddata fixtures\seed.json
.\.venv\Scripts\python manage.py createsuperuser
.\.venv\Scripts\python manage.py runserver
```

Then open `http://127.0.0.1:8000/`.

---

## PostgreSQL Setup (Recommended)

1. Create a database (example: `smart_rms`)
2. Update `.env`:

```env
DEBUG=True
SECRET_KEY=your-secret
DATABASE_URL=postgres://USER:PASSWORD@127.0.0.1:5432/smart_rms
ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000
```

3. Run:

```powershell
.\.venv\Scripts\python manage.py migrate
.\.venv\Scripts\python manage.py loaddata fixtures\seed.json
.\.venv\Scripts\python manage.py createsuperuser
.\.venv\Scripts\python manage.py runserver
```

---

## Roles & Permissions (Quick Guide)

- **Admin/Manager**: staff management, menu, tables, inventory, recipes, reports
- **Waiter**: create orders, add items, send to kitchen
- **Kitchen**: kitchen board (KOT), mark items ready
- **Cashier**: invoice/payment, daily closing

---

## Step-by-step Implementation (What’s inside)

1. **Project setup**
   - Django project: `config/`
   - Modular apps in `apps/`: `users`, `menu`, `tables`, `orders`, `inventory`, `billing`, `reports`

2. **Settings (deployment-ready)**
   - `config/settings/base.py`, `dev.py`, `prod.py`
   - Environment variables via `.env` (see `.env.example`)
   - Static files via WhiteNoise

3. **Auth + Roles**
   - Custom user model: `apps/users/models.py`
   - Role-based access: `apps/users/permissions.py`

4. **Menu + Tables**
   - CRUD with CBVs + ModelForms
   - Bootstrap templates in `templates/menu/` and `templates/tables/`

5. **Orders + KOT**
   - Create order → add items → send to kitchen → mark items ready
   - Kitchen board auto-refreshes periodically

6. **Inventory + Recipes**
   - Raw materials + stock movements
   - Recipe editor (menu item → raw materials quantities)
   - Stock validation before “Send to kitchen”

7. **Billing**
   - Draft invoice per order
   - Pay invoice (Cash/UPI/Card) with GST + discount
   - **Atomic** payment: validates & deducts stock, then marks order completed
   - Signal safety-net: auto deduct if invoice is marked paid in admin

8. **Reports**
   - Daily closing + expenses + PDF export via ReportLab

---

## Production Deployment Notes (Guide)

### Environment

Set:
- `DJANGO_SETTINGS_MODULE=config.settings.prod`
- `DEBUG=False`
- `SECRET_KEY=...`
- `ALLOWED_HOSTS=your-domain.com`
- `DATABASE_URL=postgres://...`

### Static files

```bash
python manage.py collectstatic
```

### App server (Linux)

- Use Gunicorn behind Nginx (standard Django deployment)
- Or use any WSGI server suitable for your hosting platform

> For college demo on Windows, `runserver` is fine.

---

## Useful URLs

- `/login/` (staff login)
- `/dashboard/`
- `/menu/`
- `/tables/`
- `/orders/`
- `/orders/kitchen/` (KOT)
- `/billing/`
- `/inventory/`
- `/reports/daily-closing/`

