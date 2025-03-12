# [SBD1]P1_202100106

# Sistema de Gestión de Órdenes y Productos

Este proyecto es una **API RESTful** desarrollada en **Python (Flask)** con base de datos **Oracle**, que permite gestionar un sistema de **usuarios**, **productos**, **órdenes de compra**, **pagos**, **envíos**, y más.

Pensado para ser **robusto, modular y escalable**, facilita el control completo del ciclo de vida de una compra, desde el registro del usuario hasta el seguimiento de la orden.

---

## Funcionalidades Principales

- Gestión de **Usuarios** (Registro, Login, CRUD, Dirección).
- Gestión de **Productos** (Alta, Baja, Stock, Categorías).
- Gestión de **Órdenes de Compra** (Creación, Listado, Detalle).
- Gestión de **Pagos** (Asociación de métodos de pago, registro de pagos).
- Gestión de **Envíos** (Integración de empresas de transporte y estados de envío).

---

## Estructura del Proyecto

```
arduino
CopiarEditar
client/
├── app/
│   ├── __init__.py
│   ├── users.py
│   ├── products.py
│   ├── orders.py
│   └── payments.py
├── utils/
│   ├── db.py
│   └── .env (configuración de conexión a Oracle)
└── run.py (archivo principal)

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
- [Manual de Usuario](??)


---

## 📝 Cómo Ejecutar el Proyecto

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
    
    ```
    DB_USER=system
    DB_PASSWORD=tuPassword
    DB_DSN=localhost:1521/XEPDB1
    
    ```
    
5. Corre el servidor Flask:
    
    ```bash
    python run.py
    ```
    

---