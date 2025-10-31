-- TimescaleDB hypertable definitions.
CREATE TABLE IF NOT EXISTS bars (
    symbol TEXT NOT NULL,
    ts TIMESTAMPTZ NOT NULL,
    o NUMERIC,
    h NUMERIC,
    l NUMERIC,
    c NUMERIC,
    v NUMERIC,
    vwap NUMERIC,
    interval TEXT,
    PRIMARY KEY (symbol, ts)
);

SELECT create_hypertable('bars', 'ts', if_not_exists => TRUE);
