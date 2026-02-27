DROP TABLE IF EXISTS exchange_rates;
DROP TABLE IF EXISTS currencies;

CREATE TABLE currencies (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL
);

CREATE TABLE exchange_rates (
    id SERIAL PRIMARY KEY,
    base_currency_id INT REFERENCES currencies(id),
    target_currency_id INT REFERENCES currencies(id),
    rate NUMERIC(20,10) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_timestamp ON exchange_rates(timestamp);