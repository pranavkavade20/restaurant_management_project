# Restaurant Management System (RMS)

A robust, scalable web application designed to streamline and manage the core operations of a restaurant, built using **Django** and **Django REST Framework (DRF)**.

## 🌟 Features

This project's structure covers key restaurant operations:

* **User & Authentication (`account`)**: Secure user registration, login, and **Role-Based Access Control** (e.g., Owner, Manager, Staff).
* **Menu & Inventory (`products`)**: **CRUD** (Create, Read, Update, Delete) operations for menu items and basic **inventory tracking** for stock.
* **Order Management (`orders`)**: System for placing, viewing, and updating the status of customer orders (e.g., Pending, Preparing, Ready).
* **Core Logic (`restaurant_management`)**: Central configuration and global business logic (e.g., reporting, shift management).
* **Utilities (`utils`)**: Reusable code, helper functions, and custom mixins shared across the application.

---

## 🛠️ Technology Stack

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend Framework** | **Django** | The primary web framework for secure and rapid development. |
| **API** | **Django REST Framework (DRF)** | Used to build modern, powerful **RESTful API** endpoints. |
| **Database** | **SQLite** | Persistent data storage. |
| **Language** | **Python 3.13** | The core programming language. |

---

## 🚀 Getting Started

### Prerequisites

1.  **Python 3.x** installed.
2.  **`pip`** (Python package installer).

### 1. Setup

```bash
# Clone the repository
git clone https://github.com/pranavkavade20/restaurant_management_project.git
cd restaurant-management-system

# Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # Use .\venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
