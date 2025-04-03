
# [SBD1]P1_202100106

Este proyecto implementa una **API RESTful** en **Python (Flask)** conectada a **Oracle Database**, para gestionar un sistema completo de compras: **usuarios**, **productos**, **órdenes**, **pagos**, **envíos**, y más.  

---

## Tabla de Contenidos

- [\[SBD1\]P1\_202100106](#sbd1p1_202100106)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [Funcionalidades Principales](#funcionalidades-principales)
  - [Estructura del Proyecto](#estructura-del-proyecto)
  - [Tecnologías](#tecnologías)
  - [Documentación](#documentación)
  - [Cómo Ejecutar el Proyecto](#cómo-ejecutar-el-proyecto)
  - [Diagrama (Generado por GitDiagram)](#diagrama-generado-por-gitdiagram)

---

## Funcionalidades Principales

- Gestión de **Usuarios** (Registro, Login, CRUD, Dirección).
- Gestión de **Productos** (Alta, Baja, Stock, Categorías).
- Gestión de **Órdenes de Compra** (Creación, Listado, Detalle).
- Gestión de **Pagos** (Asociación de métodos de pago, registro de pagos).
- Gestión de **Envíos** (Integración de empresas de transporte y estados de envío).

---

## Estructura del Proyecto

```plaintext
/client
└── /app
    ├── /users
    │   ├── __init__.py         # Inicialización del módulo users
    │   └── routes.py           # Endpoints HTTP para usuarios
    │
    ├── /products
    │   ├── __init__.py         # Inicialización del módulo products
    │   └── routes.py           # Endpoints HTTP para productos
    │
    ├── /orders
    │   ├── __init__.py         # Inicialización del módulo orders
    │   ├── routes.py           # Endpoints HTTP para órdenes
    │   ├── services.py         # Lógica de negocio y validaciones para órdenes
    │   └── db_operations.py    # Consultas SQL y manipulación de la base de datos de órdenes
    │
    ├── /payments
    │   ├── __init__.py         # Inicialización del módulo payments
    │   └── routes.py           # Endpoints HTTP para pagos
    │
    └── __init__.py             # Función create_app() y registro de blueprints de los módulos
  
│
├── utils/                # Funciones auxiliares
│   └── db.py             # Conexión a la base de datos Oracle
  └── .env              
│
├── run.py                # Punto de entrada principal para ejecutar la app
└── .venv/                # Entorno virtual 


```

---

## Tecnologías

- **Python 3.12**
- **Flask 3.1.0**
- **Oracle Database 21c**
- **cx_Oracle / oracledb**
- **bcrypt** para hashing de contraseñas
- **Docker** (opcional para levantar Oracle)

---

## Documentación

Accede a los diferentes manuales del proyecto:

- [Análisis de Datos](https://www.notion.so/An-lisis-Previo-19bfad1ba0758091b7b4d2c78529e5a0?pvs=4)
- [Manual Técnico](https://www.notion.so/Manual-T-cnico-1b4fad1ba075804aa987cb79fea0e1cc?pvs=4)
- [Manual de Usuario](https://www.notion.so/Manual-de-Usuario-1b5fad1ba07580a78603cc5652476437?pvs=21)

---

## Cómo Ejecutar el Proyecto

1. Clona el repositorio:

    ```bash
    git clone https://github.com/tuusuario/tu-repositorio.git
    ```

2. Activa el entorno virtual:

    ```bash
    source .venv/bin/activate
    ```

3. Instala las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

4. Configura el archivo `.env` en `/utils`:

    ```plaintext
    DB_USER=system
    DB_PASSWORD=tuPassword
    DB_DSN=localhost:1521/XEPDB1
    
    ```

5. Corre el servidor Flask:

    ```bash
    python run.py
    ```

## Diagrama (Generado por GitDiagram)

```mermaid
%%{ init: { "theme": "dark" } }%%
graph TD
    ExternalClient["External Client (HTTP)"]:::external
    APIServer["Flask API Server"]:::api

    ExternalClient -->|"sends request"| APIServer

    %% Users Module Subgraph
    subgraph "Users Module"
        UsersRoutes["Users Routes"]:::module
        UsersBL["Users Business Logic"]:::business
        UsersDB["Users DB Operations"]:::db_module
        UsersRoutes -->|"calls"| UsersBL
        UsersBL -->|"queries"| UsersDB
    end

    %% Products Module Subgraph
    subgraph "Products Module"
        ProductsRoutes["Products Routes"]:::module
        ProductsBL["Products Business Logic"]:::business
        ProductsDB["Products DB Operations"]:::db_module
        ProductsRoutes -->|"calls"| ProductsBL
        ProductsBL -->|"queries"| ProductsDB
    end

    %% Orders Module Subgraph
    subgraph "Orders Module"
        OrdersRoutes["Orders Routes"]:::module
        OrdersServices["Orders Services"]:::business
        OrdersDB["Orders DB Operations"]:::db_module
        OrdersRoutes -->|"calls"| OrdersServices
        OrdersServices -->|"queries"| OrdersDB
    end

    %% Payments Module Subgraph
    subgraph "Payments Module"
        PaymentsRoutes["Payments Routes"]:::module
        PaymentsBL["Payments Business Logic"]:::business
        PaymentsDB["Payments DB Operations"]:::db_module
        PaymentsRoutes -->|"calls"| PaymentsBL
        PaymentsBL -->|"queries"| PaymentsDB
    end

    %% Connections from API Server to Modules Routes
    APIServer -->|"routes to"| UsersRoutes
    APIServer -->|"routes to"| ProductsRoutes
    APIServer -->|"routes to"| OrdersRoutes
    APIServer -->|"routes to"| PaymentsRoutes

    %% Database Utility and Oracle Database
    DBUtility["DB Connection Utility"]:::util
    OracleDB["Oracle Database"]:::database

    %% All module DB Operations connect to DB Utility
    UsersDB -->|"uses"| DBUtility
    ProductsDB -->|"uses"| DBUtility
    OrdersDB -->|"uses"| DBUtility
    PaymentsDB -->|"uses"| DBUtility

    DBUtility -->|"connects to"| OracleDB

    %% Click Events
    click APIServer "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/run.py"
    click UsersRoutes "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/app/users/routes.py"
    click UsersDB "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/app/users/db_users.py"
    click UsersBL "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/app/users/users.py"
    click ProductsRoutes "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/app/products/routes.py"
    click ProductsDB "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/app/products/db_products.py"
    click ProductsBL "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/app/products/products.py"
    click OrdersRoutes "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/app/orders/routes.py"
    click OrdersServices "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/app/orders/services.py"
    click OrdersDB "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/app/orders/db_operations.py"
    click PaymentsRoutes "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/app/payments/routes.py"
    click PaymentsDB "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/app/payments/db_payments.py"
    click PaymentsBL "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/app/payments/payments.py"
    click DBUtility "https://github.com/sudokentucky/-sbd1-p1_202100106/blob/main/client/utils/db.py"

    %% Styles (modo oscuro, fondo blanco y bordes llamativos)
    classDef external fill:#ffffff,color:#000000,stroke:#e67e22,stroke-width:2px;
    classDef api fill:#ffffff,color:#000000,stroke:#3498db,stroke-width:2px;
    classDef module fill:#ffffff,color:#000000,stroke:#2ecc71,stroke-width:2px;
    classDef business fill:#ffffff,color:#000000,stroke:#f1c40f,stroke-width:2px;
    classDef db_module fill:#ffffff,color:#000000,stroke:#9b59b6,stroke-width:2px;
    classDef util fill:#ffffff,color:#000000,stroke:#e74c3c,stroke-width:2px;
    classDef database fill:#ffffff,color:#000000,stroke:#1abc9c,stroke-width:2px,stroke-dasharray: 5,5;


```

---
