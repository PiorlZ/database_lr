-- Таблица категорий сувениров
CREATE TABLE souvenirscategories (
    id SERIAL PRIMARY KEY,
    idparent INTEGER REFERENCES souvenirscategories(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL
);

-- Таблица цветов
CREATE TABLE color (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Таблица материалов сувениров
CREATE TABLE souvenirmaterials (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Таблица методов нанесения
CREATE TABLE applicationmethods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Таблица сувениров
CREATE TABLE souvenirs (
    id SERIAL PRIMARY KEY,
    shortname VARCHAR(255),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    rating NUMERIC,
    idcategory INTEGER REFERENCES souvenirscategories(id),
    idcolor INTEGER REFERENCES color(id),
    size VARCHAR(255),
    idmaterial INTEGER REFERENCES souvenirmaterials(id),
    weight NUMERIC,
    qtypics INTEGER,
    picssize NUMERIC,
    idapplicmethod INTEGER REFERENCES applicationmethods(id),
    allcategories TEXT,
    dealerprice NUMERIC,
    price NUMERIC,
    comments TEXT
);

-- Таблица поставщиков
CREATE TABLE providers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    contactperson VARCHAR(255),
    comments TEXT
);

-- Таблица статусов закупок
CREATE TABLE procurementstatuses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Таблица закупок сувениров
CREATE TABLE souvenirprocurements (
    id SERIAL PRIMARY KEY,
    idprovider INTEGER REFERENCES providers(id),
    data DATE NOT NULL,
    idstatus INTEGER REFERENCES procurementstatuses(id),
    amount NUMERIC
);

-- Таблица связей между закупками и сувенирами
CREATE TABLE procurementsouvenirs (
    id SERIAL PRIMARY KEY,
    idsouvenir INTEGER REFERENCES souvenirs(id),
    idprocurement INTEGER REFERENCES souvenirprocurements(id),
    amount NUMERIC,
    price NUMERIC
);

-- Таблица складов сувениров
CREATE TABLE souvenirstores (
    id SERIAL PRIMARY KEY,
    idprocurement INTEGER REFERENCES souvenirprocurements(id),
    idsouvenir INTEGER REFERENCES souvenirs(id),
    amount NUMERIC,
    comments TEXT
);