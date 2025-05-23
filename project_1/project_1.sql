-- extend statement timeout to execute properly on iLab
SET statement_timeout = '10min';

-- drop previous tables to reduce conflict when rerunning
DROP TABLE IF EXISTS DenialReasons CASCADE;
DROP TABLE IF EXISTS CoApplicantRace CASCADE;
DROP TABLE IF EXISTS ApplicantRace CASCADE;
DROP TABLE IF EXISTS LoanApplication CASCADE;
DROP TABLE IF EXISTS RespondentAgency CASCADE;
DROP TABLE IF EXISTS Location CASCADE;
DROP TABLE IF EXISTS EditStatus CASCADE;
DROP TABLE IF EXISTS LienStatus CASCADE;
DROP TABLE IF EXISTS HOEPAStatus CASCADE;
DROP TABLE IF EXISTS DenialReason CASCADE;
DROP TABLE IF EXISTS PurchaserType CASCADE;
DROP TABLE IF EXISTS Sex CASCADE;
DROP TABLE IF EXISTS Race CASCADE;
DROP TABLE IF EXISTS Ethnicity CASCADE;
DROP TABLE IF EXISTS County CASCADE;
DROP TABLE IF EXISTS State CASCADE;
DROP TABLE IF EXISTS MSA CASCADE;
DROP TABLE IF EXISTS ActionTaken CASCADE;
DROP TABLE IF EXISTS Preapproval CASCADE;
DROP TABLE IF EXISTS OwnerOccupancy CASCADE;
DROP TABLE IF EXISTS LoanPurpose CASCADE;
DROP TABLE IF EXISTS PropertyType CASCADE;
DROP TABLE IF EXISTS LoanType CASCADE;
DROP TABLE IF EXISTS Agency CASCADE;

-- create initial tables based on 3NF

CREATE TABLE Agency (
    agency_code SMALLINT PRIMARY KEY,
    agency_name VARCHAR(100) NOT NULL,
    agency_abbr VARCHAR(20) NOT NULL
);

CREATE TABLE LoanType (
    loan_type SMALLINT PRIMARY KEY,
    loan_type_name VARCHAR(100) NOT NULL
);

CREATE TABLE PropertyType (
    property_type SMALLINT PRIMARY KEY,
    property_type_name VARCHAR(100) NOT NULL
);

CREATE TABLE LoanPurpose (
    loan_purpose SMALLINT PRIMARY KEY,
    loan_purpose_name VARCHAR(100) NOT NULL
);

CREATE TABLE OwnerOccupancy (
    owner_occupancy SMALLINT PRIMARY KEY,
    owner_occupancy_name VARCHAR(100) NOT NULL
);

CREATE TABLE Preapproval (
    preapproval SMALLINT PRIMARY KEY,
    preapproval_name VARCHAR(100) NOT NULL
);

CREATE TABLE ActionTaken (
    action_taken SMALLINT PRIMARY KEY,
    action_taken_name VARCHAR(100) NOT NULL
);

CREATE TABLE MSA (
    msamd VARCHAR(5) PRIMARY KEY,
    msamd_name VARCHAR(100)
);

CREATE TABLE State (
    state_code CHAR(2) PRIMARY KEY,
    state_name VARCHAR(100) NOT NULL,
    state_abbr CHAR(2) NOT NULL
);

CREATE TABLE County (
    county_code CHAR(3),
    state_code CHAR(2),
    county_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (county_code, state_code),
    FOREIGN KEY (state_code) REFERENCES State(state_code)
);

CREATE TABLE Ethnicity (
    ethnicity_code SMALLINT PRIMARY KEY,
    ethnicity_name VARCHAR(100) NOT NULL
);

CREATE TABLE Race (
    race_code SMALLINT PRIMARY KEY,
    race_name VARCHAR(100) NOT NULL
);

CREATE TABLE Sex (
    sex_code SMALLINT PRIMARY KEY,
    sex_name VARCHAR(100) NOT NULL
);

CREATE TABLE PurchaserType (
    purchaser_type SMALLINT PRIMARY KEY,
    purchaser_type_name VARCHAR(100) NOT NULL
);

CREATE TABLE DenialReason (
    denial_reason_code SMALLINT PRIMARY KEY,
    denial_reason_name VARCHAR(100) NOT NULL
);

CREATE TABLE HOEPAStatus (
    hoepa_status SMALLINT PRIMARY KEY,
    hoepa_status_name VARCHAR(100) NOT NULL
);

CREATE TABLE LienStatus (
    lien_status SMALLINT PRIMARY KEY,
    lien_status_name VARCHAR(100) NOT NULL
);

CREATE TABLE EditStatus (
    edit_status SMALLINT PRIMARY KEY,
    edit_status_name VARCHAR(100) NOT NULL
);

-- added location_id primary key for unique locations
CREATE TABLE Location (
    location_id SERIAL PRIMARY KEY,
    msamd VARCHAR(5),
    state_code CHAR(2),
    county_code CHAR(3),
    census_tract_number VARCHAR(8),
    population INTEGER,
    minority_population NUMERIC,
    hud_median_family_income INTEGER,
    tract_to_msamd_income NUMERIC,
    number_of_owner_occupied_units INTEGER,
    number_of_1_to_4_family_units INTEGER,
    FOREIGN KEY (msamd) REFERENCES MSA(msamd),
    FOREIGN KEY (state_code) REFERENCES State(state_code),
    FOREIGN KEY (county_code, state_code) REFERENCES County(county_code, state_code)
);

CREATE TABLE RespondentAgency (
    as_of_year INTEGER,
    respondent_id VARCHAR(10),
    agency_code SMALLINT,
    PRIMARY KEY (as_of_year, respondent_id),
    FOREIGN KEY (agency_code) REFERENCES Agency(agency_code)
);

CREATE TABLE LoanApplication (
    ID INTEGER PRIMARY KEY,
    as_of_year INTEGER NOT NULL,
    respondent_id VARCHAR(10) NOT NULL,
    loan_type SMALLINT NOT NULL,
    property_type SMALLINT NOT NULL,
    loan_purpose SMALLINT NOT NULL,
    owner_occupancy SMALLINT NOT NULL,
    loan_amount_000s NUMERIC,
    preapproval SMALLINT NOT NULL,
    action_taken SMALLINT NOT NULL,
    location_id INTEGER NOT NULL,
    applicant_ethnicity SMALLINT NOT NULL,
    co_applicant_ethnicity SMALLINT,
    applicant_sex SMALLINT NOT NULL,
    co_applicant_sex SMALLINT,
    applicant_income_000s NUMERIC,
    purchaser_type SMALLINT,
    rate_spread VARCHAR(10),
    hoepa_status SMALLINT,
    lien_status SMALLINT,
    edit_status SMALLINT,
    sequence_number VARCHAR(20),
    application_date_indicator SMALLINT,
    FOREIGN KEY (as_of_year, respondent_id) REFERENCES RespondentAgency(as_of_year, respondent_id),
    FOREIGN KEY (loan_type) REFERENCES LoanType(loan_type),
    FOREIGN KEY (property_type) REFERENCES PropertyType(property_type),
    FOREIGN KEY (loan_purpose) REFERENCES LoanPurpose(loan_purpose),
    FOREIGN KEY (owner_occupancy) REFERENCES OwnerOccupancy(owner_occupancy),
    FOREIGN KEY (preapproval) REFERENCES Preapproval(preapproval),
    FOREIGN KEY (action_taken) REFERENCES ActionTaken(action_taken),
    FOREIGN KEY (location_id) REFERENCES Location(location_id),
    FOREIGN KEY (applicant_ethnicity) REFERENCES Ethnicity(ethnicity_code),
    FOREIGN KEY (co_applicant_ethnicity) REFERENCES Ethnicity(ethnicity_code),
    FOREIGN KEY (applicant_sex) REFERENCES Sex(sex_code),
    FOREIGN KEY (co_applicant_sex) REFERENCES Sex(sex_code),
    FOREIGN KEY (purchaser_type) REFERENCES PurchaserType(purchaser_type),
    FOREIGN KEY (hoepa_status) REFERENCES HOEPAStatus(hoepa_status),
    FOREIGN KEY (lien_status) REFERENCES LienStatus(lien_status),
    FOREIGN KEY (edit_status) REFERENCES EditStatus(edit_status)
);

CREATE TABLE ApplicantRace (
    ID INTEGER,
    race_number SMALLINT,
    race_code SMALLINT NOT NULL,
    PRIMARY KEY (ID, race_number),
    FOREIGN KEY (ID) REFERENCES LoanApplication(ID),
    FOREIGN KEY (race_code) REFERENCES Race(race_code)
);

CREATE TABLE CoApplicantRace (
    ID INTEGER,
    race_number SMALLINT,
    race_code SMALLINT NOT NULL,
    PRIMARY KEY (ID, race_number),
    FOREIGN KEY (ID) REFERENCES LoanApplication(ID),
    FOREIGN KEY (race_code) REFERENCES Race(race_code)
);

CREATE TABLE DenialReasons (
    ID INTEGER,
    reason_number SMALLINT,
    denial_reason_code SMALLINT NOT NULL,
    PRIMARY KEY (ID, reason_number),
    FOREIGN KEY (ID) REFERENCES LoanApplication(ID),
    FOREIGN KEY (denial_reason_code) REFERENCES DenialReason(denial_reason_code)
);

-- fill lookup tables with distinct values
INSERT INTO Agency (agency_code, agency_name, agency_abbr)
SELECT DISTINCT
    NULLIF(agency_code, '')::SMALLINT,
    NULLIF(agency_name, ''),
    NULLIF(agency_abbr, '')
FROM Preliminary
WHERE agency_code != '';

INSERT INTO LoanType (loan_type, loan_type_name)
SELECT DISTINCT
    NULLIF(loan_type, '')::SMALLINT,
    NULLIF(loan_type_name, '')
FROM Preliminary
WHERE loan_type != '';

INSERT INTO PropertyType (property_type, property_type_name)
SELECT DISTINCT
    NULLIF(property_type, '')::SMALLINT,
    NULLIF(property_type_name, '')
FROM Preliminary
WHERE property_type != '';

INSERT INTO LoanPurpose (loan_purpose, loan_purpose_name)
SELECT DISTINCT
    NULLIF(loan_purpose, '')::SMALLINT,
    NULLIF(loan_purpose_name, '')
FROM Preliminary
WHERE loan_purpose != '';

INSERT INTO OwnerOccupancy (owner_occupancy, owner_occupancy_name)
SELECT DISTINCT
    NULLIF(owner_occupancy, '')::SMALLINT,
    NULLIF(owner_occupancy_name, '')
FROM Preliminary
WHERE owner_occupancy != '';

INSERT INTO Preapproval (preapproval, preapproval_name)
SELECT DISTINCT
    NULLIF(preapproval, '')::SMALLINT,
    NULLIF(preapproval_name, '')
FROM Preliminary
WHERE preapproval != '';

INSERT INTO ActionTaken (action_taken, action_taken_name)
SELECT DISTINCT
    NULLIF(action_taken, '')::SMALLINT,
    NULLIF(action_taken_name, '')
FROM Preliminary
WHERE action_taken != '';

INSERT INTO MSA (msamd, msamd_name)
SELECT DISTINCT
    NULLIF(msamd, ''),
    NULLIF(msamd_name, '')
FROM Preliminary
WHERE msamd != '';

INSERT INTO State (state_code, state_name, state_abbr)
SELECT DISTINCT
    NULLIF(state_code, ''),
    NULLIF(state_name, ''),
    NULLIF(state_abbr, '')
FROM Preliminary
WHERE state_code != '';

INSERT INTO County (county_code, state_code, county_name)
SELECT DISTINCT
    NULLIF(county_code, ''),
    NULLIF(state_code, ''),
    NULLIF(county_name, '')
FROM Preliminary
WHERE county_code != '' AND state_code != '';

INSERT INTO Ethnicity (ethnicity_code, ethnicity_name)
SELECT DISTINCT
    NULLIF(applicant_ethnicity, '')::SMALLINT,
    NULLIF(applicant_ethnicity_name, '')
FROM Preliminary
WHERE applicant_ethnicity != ''
UNION
SELECT DISTINCT
    NULLIF(co_applicant_ethnicity, '')::SMALLINT,
    NULLIF(co_applicant_ethnicity_name, '')
FROM Preliminary
WHERE co_applicant_ethnicity != '';

INSERT INTO Race (race_code, race_name)
SELECT DISTINCT 
    NULLIF(applicant_race_1, '')::SMALLINT, 
    NULLIF(applicant_race_name_1, '')
FROM Preliminary
WHERE applicant_race_1 != ''
UNION
SELECT DISTINCT 
    NULLIF(applicant_race_2, '')::SMALLINT, 
    NULLIF(applicant_race_name_2, '')
FROM Preliminary
WHERE applicant_race_2 != ''
UNION
SELECT DISTINCT 
    NULLIF(applicant_race_3, '')::SMALLINT, 
    NULLIF(applicant_race_name_3, '')
FROM Preliminary
WHERE applicant_race_3 != ''
UNION
SELECT DISTINCT 
    NULLIF(applicant_race_4, '')::SMALLINT, 
    NULLIF(applicant_race_name_4, '')
FROM Preliminary
WHERE applicant_race_4 != ''
UNION
SELECT DISTINCT 
    NULLIF(applicant_race_5, '')::SMALLINT, 
    NULLIF(applicant_race_name_5, '')
FROM Preliminary
WHERE applicant_race_5 != ''
UNION
SELECT DISTINCT 
    NULLIF(co_applicant_race_1, '')::SMALLINT, 
    NULLIF(co_applicant_race_name_1, '')
FROM Preliminary
WHERE co_applicant_race_1 != ''
UNION
SELECT DISTINCT 
    NULLIF(co_applicant_race_2, '')::SMALLINT, 
    NULLIF(co_applicant_race_name_2, '')
FROM Preliminary
WHERE co_applicant_race_2 != ''
UNION
SELECT DISTINCT 
    NULLIF(co_applicant_race_3, '')::SMALLINT, 
    NULLIF(co_applicant_race_name_3, '')
FROM Preliminary
WHERE co_applicant_race_3 != ''
UNION
SELECT DISTINCT 
    NULLIF(co_applicant_race_4, '')::SMALLINT, 
    NULLIF(co_applicant_race_name_4, '')
FROM Preliminary
WHERE co_applicant_race_4 != ''
UNION
SELECT DISTINCT 
    NULLIF(co_applicant_race_5, '')::SMALLINT, 
    NULLIF(co_applicant_race_name_5, '')
FROM Preliminary
WHERE co_applicant_race_5 != '';

INSERT INTO Sex (sex_code, sex_name)
SELECT DISTINCT 
    NULLIF(applicant_sex, '')::SMALLINT, 
    NULLIF(applicant_sex_name, '')
FROM Preliminary
WHERE applicant_sex != ''
UNION
SELECT DISTINCT 
    NULLIF(co_applicant_sex, '')::SMALLINT, 
    NULLIF(co_applicant_sex_name, '')
FROM Preliminary
WHERE co_applicant_sex != '';

INSERT INTO PurchaserType (purchaser_type, purchaser_type_name)
SELECT DISTINCT 
    NULLIF(purchaser_type, '')::SMALLINT, 
    NULLIF(purchaser_type_name, '')
FROM Preliminary
WHERE purchaser_type != '';

INSERT INTO DenialReason (denial_reason_code, denial_reason_name)
SELECT DISTINCT 
    NULLIF(denial_reason_1, '')::SMALLINT, 
    NULLIF(denial_reason_name_1, '')
FROM Preliminary
WHERE denial_reason_1 != ''
UNION
SELECT DISTINCT 
    NULLIF(denial_reason_2, '')::SMALLINT, 
    NULLIF(denial_reason_name_2, '')
FROM Preliminary
WHERE denial_reason_2 != ''
UNION
SELECT DISTINCT 
    NULLIF(denial_reason_3, '')::SMALLINT, 
    NULLIF(denial_reason_name_3, '')
FROM Preliminary
WHERE denial_reason_3 != '';

INSERT INTO HOEPAStatus (hoepa_status, hoepa_status_name)
SELECT DISTINCT 
    NULLIF(hoepa_status, '')::SMALLINT, 
    NULLIF(hoepa_status_name, '')
FROM Preliminary
WHERE hoepa_status != '';

INSERT INTO LienStatus (lien_status, lien_status_name)
SELECT DISTINCT 
    NULLIF(lien_status, '')::SMALLINT, 
    NULLIF(lien_status_name, '')
FROM Preliminary
WHERE lien_status != '';

INSERT INTO EditStatus (edit_status, edit_status_name)
SELECT DISTINCT 
    NULLIF(edit_status, '')::SMALLINT, 
    NULLIF(edit_status_name, '')
FROM Preliminary
WHERE edit_status != '';

INSERT INTO RespondentAgency (as_of_year, respondent_id, agency_code)
SELECT DISTINCT 
    NULLIF(as_of_year, '')::INTEGER, 
    NULLIF(respondent_id, ''), 
    NULLIF(agency_code, '')::SMALLINT
FROM Preliminary
WHERE as_of_year != '' AND respondent_id != '' AND agency_code != ''
ON CONFLICT (as_of_year, respondent_id) DO NOTHING;

-- create temp table to handle location data
CREATE TEMPORARY TABLE temp_location AS
SELECT DISTINCT
    NULLIF(msamd, '') AS msamd,
    NULLIF(state_code, '') AS state_code,
    NULLIF(county_code, '') AS county_code,
    NULLIF(census_tract_number, '') AS census_tract_number,
    NULLIF(population, '')::INTEGER AS population,
    NULLIF(minority_population, '')::NUMERIC AS minority_population,
    NULLIF(hud_median_family_income, '')::INTEGER AS hud_median_family_income,
    NULLIF(tract_to_msamd_income, '')::NUMERIC AS tract_to_msamd_income,
    NULLIF(number_of_owner_occupied_units, '')::INTEGER AS number_of_owner_occupied_units,
    NULLIF(number_of_1_to_4_family_units, '')::INTEGER AS number_of_1_to_4_family_units,
    CONCAT(
        COALESCE(msamd, ''), '|',
        COALESCE(state_code, ''), '|',
        COALESCE(county_code, ''), '|',
        COALESCE(census_tract_number, ''), '|',
        COALESCE(population, ''), '|',
        COALESCE(minority_population, ''), '|',
        COALESCE(hud_median_family_income, ''), '|',
        COALESCE(tract_to_msamd_income, ''), '|',
        COALESCE(number_of_owner_occupied_units, ''), '|',
        COALESCE(number_of_1_to_4_family_units, '')
    ) as location_key
FROM Preliminary;

-- ensure every msamd in the location data exists in MSA.
INSERT INTO MSA (msamd, msamd_name)
SELECT DISTINCT msamd, NULL
FROM temp_location
WHERE msamd IS NOT NULL
  AND msamd NOT IN (SELECT msamd FROM MSA);

-- fill location table with values from temp table
INSERT INTO Location (
    msamd,
    state_code,
    county_code,
    census_tract_number,
    population,
    minority_population,
    hud_median_family_income,
    tract_to_msamd_income,
    number_of_owner_occupied_units,
    number_of_1_to_4_family_units
)
SELECT
    msamd,
    state_code,
    county_code,
    census_tract_number,
    population,
    minority_population,
    hud_median_family_income,
    tract_to_msamd_income,
    number_of_owner_occupied_units,
    number_of_1_to_4_family_units
FROM temp_location;

-- create temp table for creating location_id
CREATE TEMPORARY TABLE temp_location_id AS
SELECT 
    temp.location_key,
    loc.location_id
from temp_location temp
JOIN Location loc ON 
    (temp.msamd = loc.msamd OR (temp.msamd IS NULL AND loc.msamd IS NULL)) AND
    (temp.state_code = loc.state_code OR (temp.state_code IS NULL AND loc.state_code IS NULL)) AND
    (temp.county_code = loc.county_code OR (temp.county_code IS NULL AND loc.county_code IS NULL)) AND
    (temp.census_tract_number = loc.census_tract_number OR (temp.census_tract_number IS NULL AND loc.census_tract_number IS NULL)) AND
    (temp.population = loc.population OR (temp.population IS NULL AND loc.population IS NULL)) AND
    (temp.minority_population = loc.minority_population OR (temp.minority_population IS NULL AND loc.minority_population IS NULL)) AND
    (temp.hud_median_family_income = loc.hud_median_family_income OR (temp.hud_median_family_income IS NULL AND loc.hud_median_family_income IS NULL)) AND
    (temp.tract_to_msamd_income = loc.tract_to_msamd_income OR (temp.tract_to_msamd_income IS NULL AND loc.tract_to_msamd_income IS NULL)) AND
    (temp.number_of_owner_occupied_units = loc.number_of_owner_occupied_units OR (temp.number_of_owner_occupied_units IS NULL AND loc.number_of_owner_occupied_units IS NULL)) AND
    (temp.number_of_1_to_4_family_units = loc.number_of_1_to_4_family_units OR (temp.number_of_1_to_4_family_units IS NULL AND loc.number_of_1_to_4_family_units IS NULL));

-- use temp table to modify LoanApplication table to include location_id
INSERT INTO LoanApplication (
    ID, as_of_year, respondent_id, loan_type, property_type, loan_purpose,
    owner_occupancy, loan_amount_000s, preapproval, action_taken,
    location_id, applicant_ethnicity, co_applicant_ethnicity,
    applicant_sex, co_applicant_sex, applicant_income_000s,
    purchaser_type, rate_spread, hoepa_status, lien_status,
    edit_status, sequence_number, application_date_indicator
)
SELECT
    p.ID,
    NULLIF(p.as_of_year, '')::INTEGER,
    NULLIF(p.respondent_id, ''),
    NULLIF(p.loan_type, '')::SMALLINT,
    NULLIF(p.property_type, '')::SMALLINT,
    NULLIF(p.loan_purpose, '')::SMALLINT,
    NULLIF(p.owner_occupancy, '')::SMALLINT,
    NULLIF(p.loan_amount_000s, '')::NUMERIC,
    NULLIF(p.preapproval, '')::SMALLINT,
    NULLIF(p.action_taken, '')::SMALLINT,
    loc.location_id,
    NULLIF(p.applicant_ethnicity, '')::SMALLINT,
    NULLIF(p.co_applicant_ethnicity, '')::SMALLINT,
    NULLIF(p.applicant_sex, '')::SMALLINT,
    NULLIF(p.co_applicant_sex, '')::SMALLINT,
    NULLIF(p.applicant_income_000s, '')::NUMERIC,
    NULLIF(p.purchaser_type, '')::SMALLINT,
    NULLIF(p.rate_spread, ''),
    NULLIF(p.hoepa_status, '')::SMALLINT,
    NULLIF(p.lien_status, '')::SMALLINT,
    NULLIF(p.edit_status, '')::SMALLINT,
    NULLIF(p.sequence_number, ''),
    NULLIF(p.application_date_indicator, '')::SMALLINT
FROM Preliminary p
JOIN temp_location_id loc ON
    CONCAT(
        COALESCE(p.msamd, ''), '|',
        COALESCE(p.state_code, ''), '|',
        COALESCE(p.county_code, ''), '|',
        COALESCE(p.census_tract_number, ''), '|',
        COALESCE(p.population, ''), '|',
        COALESCE(p.minority_population, ''), '|',
        COALESCE(p.hud_median_family_income, ''), '|',
        COALESCE(p.tract_to_msamd_income, ''), '|',
        COALESCE(p.number_of_owner_occupied_units, ''), '|',
        COALESCE(p.number_of_1_to_4_family_units, '')
    ) = loc.location_key;

    -- fill ApplicantRace table
INSERT INTO ApplicantRace (ID, race_number, race_code)
SELECT ID, 1, NULLIF(applicant_race_1, '')::SMALLINT
FROM Preliminary
WHERE applicant_race_1 != '';

INSERT INTO ApplicantRace (ID, race_number, race_code)
SELECT ID, 2, NULLIF(applicant_race_2, '')::SMALLINT
FROM Preliminary
WHERE applicant_race_2 != '';

INSERT INTO ApplicantRace (ID, race_number, race_code)
SELECT ID, 3, NULLIF(applicant_race_3, '')::SMALLINT
FROM Preliminary
WHERE applicant_race_3 != '';

INSERT INTO ApplicantRace (ID, race_number, race_code)
SELECT ID, 4, NULLIF(applicant_race_4, '')::SMALLINT
FROM Preliminary
WHERE applicant_race_4 != '';

INSERT INTO ApplicantRace (ID, race_number, race_code)
SELECT ID, 5, NULLIF(applicant_race_5, '')::SMALLINT
FROM Preliminary
WHERE applicant_race_5 != '';

-- fill CoApplicantRace table
INSERT INTO CoApplicantRace (ID, race_number, race_code)
SELECT ID, 1, NULLIF(co_applicant_race_1, '')::SMALLINT
FROM Preliminary
WHERE co_applicant_race_1 != '';

INSERT INTO CoApplicantRace (ID, race_number, race_code)
SELECT ID, 2, NULLIF(co_applicant_race_2, '')::SMALLINT
FROM Preliminary
WHERE co_applicant_race_2 != '';

INSERT INTO CoApplicantRace (ID, race_number, race_code)
SELECT ID, 3, NULLIF(co_applicant_race_3, '')::SMALLINT
FROM Preliminary
WHERE co_applicant_race_3 != '';

INSERT INTO CoApplicantRace (ID, race_number, race_code)
SELECT ID, 4, NULLIF(co_applicant_race_4, '')::SMALLINT
FROM Preliminary
WHERE co_applicant_race_4 != '';

INSERT INTO CoApplicantRace (ID, race_number, race_code)
SELECT ID, 5, NULLIF(co_applicant_race_5, '')::SMALLINT
FROM Preliminary
WHERE co_applicant_race_5 != '';

-- fill DenialReasons table
INSERT INTO DenialReasons (ID, reason_number, denial_reason_code)
SELECT ID, 1, NULLIF(denial_reason_1, '')::SMALLINT
FROM Preliminary
WHERE denial_reason_1 != '';

INSERT INTO DenialReasons (ID, reason_number, denial_reason_code)
SELECT ID, 2, NULLIF(denial_reason_2, '')::SMALLINT
FROM Preliminary
WHERE denial_reason_2 != '';

INSERT INTO DenialReasons (ID, reason_number, denial_reason_code)
SELECT ID, 3, NULLIF(denial_reason_3, '')::SMALLINT
FROM Preliminary
WHERE denial_reason_3 != '';

-- remove temp tables
DROP TABLE temp_location;
DROP TABLE temp_location_id;