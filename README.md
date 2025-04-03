
# [SBD1]P1_202100106

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

![Diagrama Mermaid]([[https://mermaid.ink/img/eyJjb2RlIjoiZ3JhcGggVERcbiAgICBBWyJBIl0gLS0-IEJbIkIiXSIsIm1lcm1haWQiOnsidGhlbWUiOiJkZWZhdWx0In19](https://mermaid.live/edit#pako:eNq1V12PozYU_SuWVyu1UjKQACFhpUqbyVattNWOOrMvXaqVAZOgIUBts510dv57Df4AEpjwwI7mAdvn3nM492I7zzDMIww9CADYE1QcwMPOz_gAfHhimGQovU0TnLEvPlQTQMyAn357eLj72Yd_e56H5ZoIfX_3-z0m3zDhUb-miD5WM0BMCTwqEj_r4wHz-S_ffUhxFlFA8D8lpsyH35uUKuztW_CZYkLBH3lUphjcl0GtX6xSOQI-bKN8KJarv3r-z7xkmH5RKDEUEo8ioovfftTYbUmTDFMKPub7JBQxgZw7i9ptddRuCz4VmCCW5JkkioKvvVxCjDQkRGlKKyOkjAtdEscNIwlukLutQHI_W87dEU4YsuvmnQHb_qklbaHGvuaiAtVG6ohxXip4baeOHedoV-25qY2qPqWX1jZK-tz9RKIxjdmBtZ0VC9pXiXvNVQGpPpAkbMeomSFHBaz2U0aMc7Ot8NzLrpYhjZeeKi29_YpOR745jOjXLrDTr3Kp6VeFfbVfJUj0q4oY2a8SLvpVxY7s147ai37VqvqU9vSrVtLn7m2eZTis9YCY5MfWbg1YLq3UNnV3eMlFhEyW641nNLr7ZY4IaDffmPwdJ1uvvUMMBYhi8JklacJOAGURT45C3mBqTYB3WwnhdeTla_xSoaKMJR-IAJFFflfdhKLgOr1W8z5NgWiCboeAULBVleALijBrHS7yrUsqiq3VClCzV72OU9_flWy6k4ZxZ6ap5hXv0VRRWNTuwzQJH8GHb1V-MRnWM015fXhgrKCeYewTdiiDmzA_GrSM8kceU4aPJ2NOg2gxLxZfl-ZyYZoLc2UEaR4YR5RkRlhfMQxSZjfFSe0NgqN94k7DgorCKKushmjHfkru49R0fDepH_oJ-fYwNWE_29mJOx1pIRMP-dpq-B9Ayt1Vz4PMk3qsmQdpO6fxdMR5nXbI5bPjfHJaKjMPEE9aXEnJS5vrffeyuN0TecICy8SD_dxsuT-AtOpn-TzIPG0_K-ZB2ubkmIa1OperF5VE-ry5Z6cU65MGUbrDMVC_ZEGcpKn3Jt5gdxPPKCOc03sTWY5tmnI4_zeJ2MFbFk_vzpLwn7cyHuFoFS90_NJ2F8i6Gi8vAiJF5MQOtpoULsKr6xLUdVS9RxhbYfMe8SK0zfhqEn0xVVJWGMVrncWyN-souJql8l_JQFEQNQmwa4dWeF2GuqnJJE7gBo2noWltlpcq1ESE6AERgk4ecGbOOziDR0x4e0TQg88VkQ_ZAR_5zczjjxEij1WTvHAcKll-f8pC6DFS4ll1rdwfoBejlPJRWXBZeJcg_tvjqCAFyv7Kcz3ck4pGRvNLNya3eZkx6FlWjYXeM3yC3txa3Dib9do2N6bjLhzLmcGTmLbtNf9fmxt7tXbdlxn8r05v3qwde7laOyvX3Zg8bvnyP17U9jU)](https://mermaidchart.com/play?utm_source=mermaid_live&utm_medium=share#pako:eNq1V12PozYU_SuWVyu1UjKQACFhpUqbyVattNWOOrMvXaqVAZOgIUBts510dv57Df4AEpjwwI7mAdvn3nM492I7zzDMIww9CADYE1QcwMPOz_gAfHhimGQovU0TnLEvPlQTQMyAn357eLj72Yd_e56H5ZoIfX_3-z0m3zDhUb-miD5WM0BMCTwqEj_r4wHz-S_ffUhxFlFA8D8lpsyH35uUKuztW_CZYkLBH3lUphjcl0GtX6xSOQI-bKN8KJarv3r-z7xkmH5RKDEUEo8ioovfftTYbUmTDFMKPub7JBQxgZw7i9ptddRuCz4VmCCW5JkkioKvvVxCjDQkRGlKKyOkjAtdEscNIwlukLutQHI_W87dEU4YsuvmnQHb_qklbaHGvuaiAtVG6ohxXip4baeOHedoV-25qY2qPqWX1jZK-tz9RKIxjdmBtZ0VC9pXiXvNVQGpPpAkbMeomSFHBaz2U0aMc7Ot8NzLrpYhjZeeKi29_YpOR745jOjXLrDTr3Kp6VeFfbVfJUj0q4oY2a8SLvpVxY7s147ai37VqvqU9vSrVtLn7m2eZTis9YCY5MfWbg1YLq3UNnV3eMlFhEyW641nNLr7ZY4IaDffmPwdJ1uvvUMMBYhi8JklacJOAGURT45C3mBqTYB3WwnhdeTla_xSoaKMJR-IAJFFflfdhKLgOr1W8z5NgWiCboeAULBVleALijBrHS7yrUsqiq3VClCzV72OU9_flWy6k4ZxZ6ap5hXv0VRRWNTuwzQJH8GHb1V-MRnWM015fXhgrKCeYewTdiiDmzA_GrSM8kceU4aPJ2NOg2gxLxZfl-ZyYZoLc2UEaR4YR5RkRlhfMQxSZjfFSe0NgqN94k7DgorCKKushmjHfkru49R0fDepH_oJ-fYwNWE_29mJOx1pIRMP-dpq-B9Ayt1Vz4PMk3qsmQdpO6fxdMR5nXbI5bPjfHJaKjMPEE9aXEnJS5vrffeyuN0TecICy8SD_dxsuT-AtOpn-TzIPG0_K-ZB2ubkmIa1OperF5VE-ry5Z6cU65MGUbrDMVC_ZEGcpKn3Jt5gdxPPKCOc03sTWY5tmnI4_zeJ2MFbFk_vzpLwn7cyHuFoFS90_NJ2F8i6Gi8vAiJF5MQOtpoULsKr6xLUdVS9RxhbYfMe8SK0zfhqEn0xVVJWGMVrncWyN-souJql8l_JQFEQNQmwa4dWeF2GuqnJJE7gBo2noWltlpcq1ESE6AERgk4ecGbOOziDR0x4e0TQg88VkQ_ZAR_5zczjjxEij1WTvHAcKll-f8pC6DFS4ll1rdwfoBejlPJRWXBZeJcg_tvjqCAFyv7Kcz3ck4pGRvNLNya3eZkx6FlWjYXeM3yC3txa3Dib9do2N6bjLhzLmcGTmLbtNf9fmxt7tXbdlxn8r05v3qwde7laOyvX3Zg8bvnyP17U9jU))

---
