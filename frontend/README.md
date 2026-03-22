# Frontend - Inventory Management System

This is the frontend service for the **Cloud-Native Inventory Management System**, built with **Next.js**.

The frontend provides the main user interface for authentication, inventory management, dashboard visualization, and low-stock related interactions.

## Features

The frontend currently supports:

- User login with JWT-based authentication
- Automatic redirect from `/` to `/login` or `/dashboard`
- Protected access to authenticated pages
- Dashboard with dynamic business statistics
- Inventory management page with:
  - item listing
  - pagination
  - filtering and search
  - create item
  - edit item
  - delete button and API integration
- Category and location dropdown selection
- Low-stock filter integration
- Logout flow

## Frontend Pages

### `/`

Root route.

This page automatically checks whether the user is logged in:

- if a valid token exists, the user is redirected to `/dashboard`
- otherwise, the user is redirected to `/login`

### `/login`

Login page for system access.

Users can sign in using a valid account such as the default admin account configured in the backend environment.

Example default credentials:

- **Email:** `admin@test.com`
- **Password:** `123456`

After successful login:

- `access_token` is stored in local storage
- the user is redirected to `/dashboard`

### `/dashboard`

Main frontend overview page.

This page displays dynamic data retrieved from backend APIs, including:

- total number of inventory items
- total categories
- low-stock item count
- current logged-in user information

The dashboard also includes quick navigation actions such as:

- go to inventory
- logout

### `/inventory`

Inventory management page.

This page supports:

- listing inventory items
- displaying item information such as:
  - ID
  - name
  - SKU
  - quantity
  - price
  - category
  - location
- filtering by:
  - search keyword
  - category
  - location
  - min/max quantity
  - below-threshold status
  - sorting order
- pagination
- creating new inventory items
- editing existing inventory items
- deleting items through the API

The page also supports low-stock filtering through query parameters.

Example:

```bash
http://localhost:3000/inventory?lowStock=true
```

This opens the inventory page with low-stock filtering enabled.

## **Tech Stack**

* **Next.js**
* **React**
* **TypeScript**
* **Axios**
* **Tailwind CSS**

## **Project Structure**

A simplified frontend structure:

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── dashboard/
│   │   │   └── page.tsx
│   │   ├── inventory/
│   │   │   └── page.tsx
│   ├── lib/
│   │   └── api.ts
├── package.json
└── README.md
```

## **API Integration**

The frontend communicates with the backend using Axios through:

```
src/lib/api.ts
```

This file is responsible for:

* configuring the backend base URL
* attaching JWT tokens to authenticated requests
* centralizing API communication

The frontend interacts with backend endpoints such as:

* POST /api/v1/auth/login
* GET /api/v1/auth/me
* GET /api/v1/items
* POST /api/v1/items
* PUT /api/v1/items/{item\_id}
* DELETE /api/v1/items/{item\_id}
* GET /api/v1/categories
* GET /api/v1/locations

## **Running the Frontend**

The frontend is usually started through Docker Compose from the project root.

### **Option 1: Run with Docker Compose**

From the project root:

```
docker compose up -d
```

Frontend will be available at:

```
http://localhost:3000
```

### **Option 2: Run frontend locally**

From the **frontend** directory:

```
npm install
npm run dev
```

Then open:

```
http://localhost:3000
```

## **How to Use**

### **1. Open the frontend**

Go to:

```
http://localhost:3000
```

You will be redirected to the login page if not authenticated.

### **2. Log in**

Use a valid account.

Example default admin credentials:

```
Email: admin@test.com
Password: 123456
```

### **3. View dashboard**

After login, the user is redirected to **/dashboard**.

The dashboard shows system business information such as:

* total items
* categories
* low-stock count

### **4. Open inventory**

Click **Go to Inventory** on the dashboard, or open:

```
http://localhost:3000/inventory
```

### **5. Manage items**

On the inventory page, users can:

* create a new item
* edit an existing item
* filter items
* view low-stock items
* delete an item through the API

## **Authentication Behavior**

The frontend uses JWT tokens stored in browser local storage.

### **On successful login:**

* access\_token** is saved**
* subsequent API requests automatically include the token

### **On logout:**

* tokens are removed from local storage
* user is redirected to **/login**

## **Notes**

* The frontend does **not** connect directly to the database.
* All data is retrieved through backend APIs.
* Monitoring dashboards (Prometheus/Grafana) are separate from this frontend and are documented in **monitoring/README.md**.

## **Known Issues**

* The delete API may depend on backend-side handling and constraints.
* Some monitoring and alerting features are handled outside the frontend layer.

## **Future Improvements**

Possible future frontend enhancements include:

* category management page
* location management page
* alerts page
* user management page
* improved error handling and notifications
* better low-stock visualization
* websocket-based real-time updates

## **Related Services**

This project also includes:

* **Backend API** for authentication and inventory operations
* **PostgreSQL** database
* **Redis**
* **Prometheus + Grafana** for monitoring
* **Serverless low-stock alert function**
