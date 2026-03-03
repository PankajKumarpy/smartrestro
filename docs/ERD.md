## ER Diagram (Text Explanation)

This project follows a normalized relational design (3NF) using Django ORM models.

### Entities and relationships

- **User (`users_user`)**
  - Stores staff accounts using Django authentication.
  - Key attribute: `role` (Admin/Manager/Waiter/Kitchen/Cashier).

- **Category (`menu_category`)**
  - `Category (1) -> (M) MenuItem`

- **MenuItem (`menu_menuitem`)**
  - Belongs to a `Category`.
  - Can have **one** `Recipe`.

- **RestaurantTable (`tables_restauranttable`)**
  - `RestaurantTable (1) -> (M) Order`

- **Order (`orders_order`)**
  - Belongs to one table.
  - Created by one user (waiter/manager/admin).
  - `Order (1) -> (M) OrderItem`
  - `Order (1) -> (1) Invoice` (billing)

- **OrderItem (`orders_orderitem`)**
  - Line items for an order.
  - References `MenuItem`.
  - Has kitchen item status for KOT workflow.

- **Supplier (`inventory_supplier`)**
  - `Supplier (1) -> (M) RawMaterial`

- **RawMaterial (`inventory_rawmaterial`)**
  - Current stock and minimum stock level.
  - `RawMaterial (1) -> (M) StockMovement`
  - Used in `RecipeItem`.

- **StockMovement (`inventory_stockmovement`)**
  - Tracks stock in/out history for auditability.
  - Created by a staff user.

- **Recipe (`inventory_recipe`)**
  - `MenuItem (1) -> (1) Recipe`
  - `Recipe (1) -> (M) RecipeItem`

- **RecipeItem (`inventory_recipeitem`)**
  - Links recipe to raw materials and required quantity.
  - Composite uniqueness: (`recipe`, `material`)

- **TaxConfig (`billing_taxconfig`)**
  - GST rate configuration (typically one active row).

- **Invoice (`billing_invoice`)**
  - One invoice per order.
  - Stores financial snapshot: subtotal/discount/gst/total.
  - `Invoice (1) -> (M) Payment`

- **Payment (`billing_payment`)**
  - Stores payment transactions (mode/amount/reference).

- **Expense (`reports_expense`)**
  - Daily expenses for closing report.

### 3NF Notes (Normalization)

- **No repeating groups**: multi-line items are stored in `OrderItem` and `RecipeItem`.
- **No partial dependencies**: line tables use full keys and reference parent records via foreign keys.
- **No transitive dependencies**: descriptive data (category, supplier) is stored in dedicated tables; operational records reference them by IDs.

### Indexing (Performance)

Key indexes are used for frequent filters:

- `users_user(role, is_active)` for role dashboards/access.
- `orders_order(status, created_at)` for active kitchen/order lists.
- `menu_menuitem(is_available, name)` for searching and availability filtering.
- `inventory_rawmaterial(is_active, name)` and low-stock checks.
- `billing_invoice(status, paid_at)` for reports and daily closing.

