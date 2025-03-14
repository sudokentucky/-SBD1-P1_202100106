--Tabla cliente
CREATE TABLE Cliente (
    id                INTEGER         NOT NULL PRIMARY KEY,
    national_document VARCHAR2(9)     NOT NULL,
    name              VARCHAR2(23)    NOT NULL,
    lastname          VARCHAR2(10)    NOT NULL,
    username          VARCHAR2(32)    NOT NULL,
    phone             VARCHAR2(22),
    active            VARCHAR2(5)     NOT NULL,
    password          VARCHAR2(100)    NOT NULL,
    created_at        TIMESTAMP       NOT NULL,
    updated_at        TIMESTAMP
);
--tabla trabajo
CREATE TABLE Trabajo (
    id         INTEGER         NOT NULL PRIMARY KEY,
    job_name   VARCHAR2(43)    NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP
);
--tabla departamento
CREATE TABLE Departamento (
    id         INTEGER         NOT NULL PRIMARY KEY,
    name       VARCHAR2(62)    NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP
);
--tabla sede
CREATE TABLE Sede (
    id         INTEGER         NOT NULL PRIMARY KEY,
    name       VARCHAR2(18)    NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP
);
--tabla categoria
CREATE TABLE Categoria (
    id         INTEGER         NOT NULL PRIMARY KEY,
    name       VARCHAR2(24)    NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP
);
--tabla estado de pago
CREATE TABLE EstadoPago (
    id         INTEGER         NOT NULL PRIMARY KEY,
    name       VARCHAR2(11)     NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP
);
--tabla estado de envio
CREATE TABLE EstadoEnvio (
    id         INTEGER         NOT NULL PRIMARY KEY,
    name       VARCHAR2(9)     NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP
);
--tabla empresa de transporte
CREATE TABLE EmpresaTransporte (
    id         INTEGER         NOT NULL PRIMARY KEY,
    name       VARCHAR2(36)    NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP
);
--tabla estado de devolucion
CREATE TABLE EstadoDevolucion (
    id         INTEGER         NOT NULL PRIMARY KEY,
    name       VARCHAR2(9)     NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP
);
--tabla estado de movimiento
CREATE TABLE EstadoMovimiento (
    id         INTEGER         NOT NULL PRIMARY KEY,
    name       VARCHAR2(9)     NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP
);

-----------------
--email de un cliente
CREATE TABLE EmailCliente (
    id         INTEGER         NOT NULL PRIMARY KEY,  
    client_id  INTEGER         NOT NULL,              
    email      VARCHAR2(32)    NOT NULL,
    confirmed  VARCHAR2(5)     NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP,                              
    FOREIGN KEY (client_id) REFERENCES Cliente(id)
);
--direccion del cliente
CREATE TABLE Direccion (
    id         INTEGER         NOT NULL PRIMARY KEY,  
    client_id  INTEGER         NOT NULL,               
    address    VARCHAR2(58)    NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP,                              
    FOREIGN KEY (client_id) REFERENCES Cliente(id)
);
--trabajador
CREATE TABLE Trabajador (
    id                INTEGER         NOT NULL PRIMARY KEY,
    national_document VARCHAR2(9)     NOT NULL,
    name              VARCHAR2(20)    NOT NULL,
    lastname          VARCHAR2(10)    NOT NULL,
    phone             VARCHAR2(21),
    email             VARCHAR2(30)    NOT NULL,
    active            VARCHAR2(5)     NOT NULL,
    job_id            INTEGER         NOT NULL,               
    department_id     INTEGER         NOT NULL,               
    location_id       INTEGER         NOT NULL,              
    created_at        TIMESTAMP       NOT NULL,
    updated_at        TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES Trabajo(id),
    FOREIGN KEY (department_id) REFERENCES Departamento(id),
    FOREIGN KEY (location_id) REFERENCES Sede(id)
);
--producto
CREATE TABLE Producto (
    id          INTEGER         NOT NULL PRIMARY KEY,  
    sku         VARCHAR2(8)     NOT NULL,
    name        VARCHAR2(30)    NOT NULL,
    description VARCHAR2(199),                             
    price       NUMBER(9)       NOT NULL,
    slug        VARCHAR2(30),                              
    active      NUMBER(1)     NOT NULL,
    category_id INTEGER         NOT NULL,                  
    created_at  TIMESTAMP       NOT NULL,
    updated_at  TIMESTAMP,                                 
    FOREIGN KEY (category_id) REFERENCES Categoria(id)
);
--inventario
CREATE TABLE Inventario (
    id          INTEGER         NOT NULL PRIMARY KEY,
    quantity    NUMBER(6)       NOT NULL,  
    product_id  INTEGER         NOT NULL,                  
    location_id INTEGER         NOT NULL,                  
    created_at  TIMESTAMP       NOT NULL,
    updated_at  TIMESTAMP,                                
    FOREIGN KEY (product_id) REFERENCES Producto(id),
    FOREIGN KEY (location_id) REFERENCES Sede(id)
);
--imagen
CREATE TABLE Imagen (
    id         INTEGER         NOT NULL PRIMARY KEY,  
    product_id INTEGER         NOT NULL,                  
    image      VARCHAR2(33)    NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP,                                 
    FOREIGN KEY (product_id) REFERENCES Producto(id)
);
--orden
CREATE TABLE OrdenCompra (
    id          INTEGER         NOT NULL PRIMARY KEY,  
    client_id   INTEGER         NOT NULL,                  
    location_id INTEGER         NOT NULL,                 
    created_at  TIMESTAMP       NOT NULL,
    updated_at  TIMESTAMP,                                 
    FOREIGN KEY (client_id) REFERENCES Cliente(id),
    FOREIGN KEY (location_id) REFERENCES Sede(id)
);
--detalle de la orden
CREATE TABLE DetalleOrden (
    id         INTEGER         NOT NULL PRIMARY KEY,  
    order_id   INTEGER         NOT NULL,                  
    product_id INTEGER         NOT NULL,                  
    quantity   NUMBER(5)       NOT NULL,
    unit_price NUMBER(9)       NOT NULL,
    subtotal   NUMBER(9)       NOT NULL,
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP,                                 
    FOREIGN KEY (order_id) REFERENCES OrdenCompra(id),
    FOREIGN KEY (product_id) REFERENCES Producto(id)
);
--metodo pago cliente
CREATE TABLE MetodoPagoCliente (
    id         INTEGER         NOT NULL PRIMARY KEY,  
    client_id  INTEGER         NOT NULL,                  
    created_at TIMESTAMP       NOT NULL,
    updated_at TIMESTAMP,                                 
    FOREIGN KEY (client_id) REFERENCES Cliente(id)
);

CREATE TABLE MetodoPago (
    id                INTEGER         NOT NULL PRIMARY KEY,  
    payment_client_id INTEGER         NOT NULL,                  
    name              VARCHAR2(17)    NOT NULL,
    created_at        TIMESTAMP       NOT NULL,
    updated_at        TIMESTAMP,                               
    FOREIGN KEY (payment_client_id) REFERENCES MetodoPagoCliente(id)
);

CREATE TABLE Pago (
    id              INTEGER         NOT NULL PRIMARY KEY,  
    order_id        INTEGER         NOT NULL,                 
    metodo_pago_id  INTEGER         NOT NULL,                  
    estado_pago_id  INTEGER         NOT NULL,                 
    total_amount    NUMBER(10)      NOT NULL,
    created_at      TIMESTAMP       NOT NULL,
    updated_at      TIMESTAMP,                                 
    FOREIGN KEY (order_id) REFERENCES OrdenCompra(id),
    FOREIGN KEY (metodo_pago_id) REFERENCES MetodoPago(id),
    FOREIGN KEY (estado_pago_id) REFERENCES EstadoPago(id)
);

CREATE TABLE Envio (
    id                   INTEGER         NOT NULL PRIMARY KEY,  
    order_id             INTEGER         NOT NULL,                  
    company_id           INTEGER         ,                  
    shipping_status_id   INTEGER         NOT NULL,                  
    address              VARCHAR2(65)    NOT NULL,
    number_company_guide VARCHAR2(5)     NOT NULL,
    dispatch_date        TIMESTAMP       NOT NULL,
    delivered_at         TIMESTAMP,                                
    created_at           TIMESTAMP       NOT NULL,
    updated_at           TIMESTAMP,                                 
    FOREIGN KEY (order_id) REFERENCES OrdenCompra(id),
    FOREIGN KEY (company_id) REFERENCES EmpresaTransporte(id),
    FOREIGN KEY (shipping_status_id) REFERENCES EstadoEnvio(id)
);

CREATE TABLE Devolucion (
    id                   INTEGER         NOT NULL PRIMARY KEY,  
    order_id             INTEGER         NOT NULL,                 
    product_id           INTEGER         NOT NULL,                  
    estado_devolucion_id INTEGER         NOT NULL,                  
    description          VARCHAR2(199),                             
    requested_at         TIMESTAMP       NOT NULL,
    created_at           TIMESTAMP       NOT NULL,
    updated_at           TIMESTAMP,                                 
    FOREIGN KEY (order_id) REFERENCES OrdenCompra(id),
    FOREIGN KEY (product_id) REFERENCES Producto(id),
    FOREIGN KEY (estado_devolucion_id) REFERENCES EstadoDevolucion(id)
);

CREATE TABLE Movimiento (
    id                    INTEGER         NOT NULL PRIMARY KEY, 
    location_origin_id    INTEGER         NOT NULL,                  
    location_dest_id      INTEGER         NOT NULL,                  
    movement_status_id    INTEGER         NOT NULL,                  
    estimate_arrive_date  TIMESTAMP       NOT NULL,
    requested_at          TIMESTAMP       NOT NULL,
    created_at            TIMESTAMP       NOT NULL,
    updated_at            TIMESTAMP,                                 
    FOREIGN KEY (location_origin_id) REFERENCES Sede(id),
    FOREIGN KEY (location_dest_id) REFERENCES Sede(id),
    FOREIGN KEY (movement_status_id) REFERENCES EstadoMovimiento(id)
);

CREATE TABLE DetalleMovimiento (
    id          INTEGER         NOT NULL PRIMARY KEY,  
    movement_id INTEGER         NOT NULL,                  
    product_id  INTEGER         NOT NULL,                  
    quantity    NUMBER(6)       NOT NULL,
    created_at  TIMESTAMP       NOT NULL,
    updated_at  TIMESTAMP,                                
    FOREIGN KEY (movement_id) REFERENCES Movimiento(id),
    FOREIGN KEY (product_id) REFERENCES Producto(id)
);


