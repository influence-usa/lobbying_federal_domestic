BEGIN WORK;


CREATE EXTENSION "uuid-ossp";


CREATE TABLE clients (
  "id" SERIAL PRIMARY KEY,
  "data" JSON NOT NULL
);


CREATE TABLE registrants (
  "id" SERIAL PRIMARY KEY,
  "data" JSON NOT NULL
);


CREATE TABLE issues (
  "id" SERIAL PRIMARY KEY,
  "data" JSON NOT NULL
);


CREATE TABLE lobbyists (
  "id" SERIAL PRIMARY KEY,
  "data" JSON NOT NULL
);


CREATE TYPE entity_types AS ENUM (
  'Government',
  'Foreign'
);


CREATE TABLE entities (
  "id" SERIAL PRIMARY KEY,
  "type" entity_types NOT NULL,
  "data" JSON NOT NULL
);


CREATE TABLE affiliated_organizations (
  "id" SERIAL PRIMARY KEY,
  "data" JSON NOT NULL
);


CREATE TABLE filings (
  "id" UUID PRIMARY KEY,
  "amount" INT,
  "period" TEXT,
  "received" timestamp with time zone,
  "client_id" INT NOT NULL,
  "registrant_id" INT NOT NULL,
  "type" TEXT NOT NULL,
  "year" TEXT,
  FOREIGN KEY (client_id) REFERENCES "clients" DEFERRABLE,
  FOREIGN KEY (registrant_id) REFERENCES "registrants" DEFERRABLE
);


CREATE TABLE filings_lobbyist_association (
  filing_id UUID,
  lobbyist_id INT,
  PRIMARY KEY (filing_id, lobbyist_id),
  FOREIGN KEY (filing_id) REFERENCES "filings",
  FOREIGN KEY (lobbyist_id) REFERENCES "lobbyists"
);


CREATE TABLE filings_entity_association (
  filing_id UUID,
  entity_id INT,
  PRIMARY KEY (filing_id, entity_id),
  FOREIGN KEY (filing_id) REFERENCES "filings",
  FOREIGN KEY (entity_id) REFERENCES "entities"
);


CREATE TABLE filings_issues_association (
  filing_id UUID,
  issue_id INT,
  PRIMARY KEY (filing_id, issue_id),
  FOREIGN KEY (filing_id) REFERENCES "filings",
  FOREIGN KEY (issue_id) REFERENCES "issues"
);


COMMIT;
