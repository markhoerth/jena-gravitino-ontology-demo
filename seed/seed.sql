-- The Acme estate: five Iceberg tables across five schemas, created through
-- Gravitino's Iceberg REST catalog. Card numbers are fake test numbers.

CREATE NAMESPACE IF NOT EXISTS crm;
CREATE NAMESPACE IF NOT EXISTS sales;
CREATE NAMESPACE IF NOT EXISTS payments;
CREATE NAMESPACE IF NOT EXISTS finance;
CREATE NAMESPACE IF NOT EXISTS games;

CREATE TABLE IF NOT EXISTS crm.customers (
  customer_id BIGINT, full_name STRING, email STRING, phone STRING, ssn STRING, city STRING
) USING iceberg;

CREATE TABLE IF NOT EXISTS sales.orders (
  order_id BIGINT, customer_id BIGINT, card STRING, amount DECIMAL(10,2), order_ts TIMESTAMP
) USING iceberg;

CREATE TABLE IF NOT EXISTS payments.refunds (
  refund_id BIGINT, order_id BIGINT, pan_7 STRING, amount DECIMAL(10,2)
) USING iceberg;

CREATE TABLE IF NOT EXISTS finance.accounts (
  account_no STRING, customer_id BIGINT, balance DECIMAL(12,2), currency STRING
) USING iceberg;

CREATE TABLE IF NOT EXISTS games.sessions (
  session_id BIGINT, player_id BIGINT, card_game_id STRING, score INT
) USING iceberg;

INSERT INTO crm.customers VALUES
  (1, 'Ada Park',    'ada@example.com',   '555-0101', '900-11-0001', 'Omaha'),
  (2, 'Ben Ortiz',   'ben@example.com',   '555-0102', '900-11-0002', 'Grand Island'),
  (3, 'Cleo Nakamura','cleo@example.com', '555-0103', '900-11-0003', 'San Mateo');

INSERT INTO sales.orders VALUES
  (1001, 1, '4111-1111-1111-1111', 42.50,  TIMESTAMP '2026-11-01 10:15:00'),
  (1002, 2, '5500-0000-0000-0004', 19.99,  TIMESTAMP '2026-11-02 14:02:00'),
  (1003, 3, '3400-0000-0000-009',  250.00, TIMESTAMP '2026-11-03 09:40:00');

INSERT INTO payments.refunds VALUES
  (9001, 1002, '5500-0000-0000-0004', 19.99);

INSERT INTO finance.accounts VALUES
  ('AC-1001', 1, 1520.33, 'USD'),
  ('AC-1002', 2,  310.00, 'USD');

INSERT INTO games.sessions VALUES
  (1, 77, 'SOLITAIRE-KLONDIKE', 1200),
  (2, 78, 'POKER-HOLDEM',        640);
