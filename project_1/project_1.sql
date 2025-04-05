-- create initial tables based on 3NF

CREATE TABLE Agency (
    agency_code TINYINT PRIMARY KEY,
    agency_name VARCHAR(100) NOT NULL,
    agency_abbr VARCHAR(20) NOT NULL
);

CREATE TABLE LoanType (
    loan_type TINYINT PRIMARY KEY,
    loan_type_name VARCHAR(100) NOT NULL
);

CREATE TABLE PropertyType (
    property_type TINYINT PRIMARY KEY,
    property_type_name VARCHAR(100) NOT NULL
);

CREATE TABLE LoanPurpose (
    loan_purpose TINYINT PRIMARY KEY,
    loan_purpose_name VARCHAR(100) NOT NULL
);

CREATE TABLE OwnerOccupancy (
    owner_occupancy TINYINT PRIMARY KEY,
    owner_occupancy_name VARCHAR(100) NOT NULL
);

CREATE TABLE Preapproval (
    preapproval TINYINT PRIMARY KEY,
    preapproval_name VARCHAR(100) NOT NULL
);

CREATE TABLE ActionTaken (
    action_taken TINYINT PRIMARY KEY,
    action_taken_name VARCHAR(100) NOT NULL
);

CREATE TABLE MSA (
    msamd VARCHAR(5) PRIMARY KEY,
    msamd_name VARCHAR(100) NOT NULL
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
    ethnicity_code TINYINT PRIMARY KEY,
    ethnicity_name VARCHAR(100) NOT NULL
);

CREATE TABLE Race (
    race_code TINYINT PRIMARY KEY,
    race_name VARCHAR(100) NOT NULL
);

CREATE TABLE ApplicantRace (
    ID INTEGER,
    race_number TINYINT,
    race_code TINYINT NOT NULL,
    PRIMARY KEY (ID, race_number),
    FOREIGN KEY (ID) REFERENCES LoanApplication(ID),
    FOREIGN KEY (race_code) REFERENCES Race(race_code)
);

CREATE TABLE CoApplicantRace (
    ID INTEGER,
    race_number TINYINT,
    race_code TINYINT NOT NULL,
    PRIMARY KEY (ID, race_number),
    FOREIGN KEY (ID) REFERENCES LoanApplication(ID),
    FOREIGN KEY (race_code) REFERENCES Race(race_code)
);

CREATE TABLE Sex (
    sex_code TINYINT PRIMARY KEY,
    sex_name VARCHAR(100) NOT NULL
);

CREATE TABLE PurchaserType (
    purchaser_type TINYINT PRIMARY KEY,
    purchaser_type_name VARCHAR(100) NOT NULL
);

CREATE TABLE DenialReason (
    denial_reason_code TINYINT PRIMARY KEY,
    denial_reason_name VARCHAR(100) NOT NULL
);

CREATE TABLE DenialReasons (
    ID INTEGER,
    reason_number TINYINT,
    denial_reason_code TINYINT NOT NULL,
    PRIMARY KEY (ID, reason_number),
    FOREIGN KEY (ID) REFERENCES LoanApplication(ID),
    FOREIGN KEY (denial_reason_code) REFERENCES DenialReason(denial_reason_code)
);

CREATE TABLE HOEPAStatus (
    hoepa_status TINYINT PRIMARY KEY,
    hoepa_status_name VARCHAR(100) NOT NULL
);

CREATE TABLE LienStatus (
    lien_status TINYINT PRIMARY KEY,
    lien_status_name VARCHAR(100) NOT NULL
);

CREATE TABLE EditStatus (
    edit_status TINYINT PRIMARY KEY,
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
    agency_code TINYINT,
    PRIMARY KEY (as_of_year, respondent_id),
    FOREIGN KEY (agency_code) REFERENCES Agency(agency_code)
);

CREATE TABLE LoanApplication (
    ID INTEGER PRIMARY KEY,
    as_of_year INTEGER NOT NULL,
    respondent_id VARCHAR(10) NOT NULL,
    loan_type TINYINT NOT NULL,
    property_type TINYINT NOT NULL,
    loan_purpose TINYINT NOT NULL,
    owner_occupancy TINYINT NOT NULL,
    loan_amount_000s NUMERIC,
    preapproval TINYINT NOT NULL,
    action_taken TINYINT NOT NULL,
    location_id INTEGER NOT NULL,
    applicant_ethnicity TINYINT NOT NULL,
    co_applicant_ethnicity TINYINT,
    applicant_sex TINYINT NOT NULL,
    co_applicant_sex TINYINT,
    applicant_income_000s NUMERIC,
    purchaser_type TINYINT,
    rate_spread VARCHAR(10),
    hoepa_status TINYINT,
    lien_status TINYINT,
    edit_status TINYINT,
    sequence_number VARCHAR(20),
    application_date_indicator TINYINT,
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

-- fill lookup tables with distinct values
INSERT INTO Agency (agency_code, agency_name, agency_abbr)
SELECT DISTINCT
    NULLIF(agency_code, '')::TINYINT,
    NULLIF(agency_name, ''),
    NULLIF(agency_abbr, '')
FROM Preliminary
WHERE agency_code != '';

INSERT INTO LoanType (loan_type, loan_type_name)
SELECT DISTINCT
    NULLIF(loan_type, '')::TINYINT,
    NULLIF(loan_type_name, '')
FROM Preliminary
WHERE loan_type != '';

INSERT INTO PropertyType (property_type, property_type_name)
SELECT DISTINCT
    NULLIF(property_type, '')::TINYINT,
    NULLIF(property_type_name, '')
FROM Preliminary
WHERE property_type != '';

INSERT INTO LoanPurpose (loan_purpose, loan_purpose_name)
SELECT DISTINCT
    NULLIF(loan_purpose, '')::TINYINT,
    NULLIF(loan_purpose_name, '')
FROM Preliminary
WHERE loan_purpose != '';

INSERT INTO OwnerOccupancy (owner_occupancy, owner_occupancy_name)
SELECT DISTINCT
    NULLIF(owner_occupancy, '')::TINYINT,
    NULLIF(owner_occupancy_name, '')
FROM Preliminary
WHERE owner_occupancy != '';

INSERT INTO Preapproval (preapproval, preapproval_name)
SELECT DISTINCT
    NULLIF(preapproval, '')::TINYINT,
    NULLIF(preapproval_name, '')
FROM Preliminary
WHERE preapproval != '';

INSERT INTO ActionTaken (action_taken, action_taken_name)
SELECT DISTINCT
    NULLIF(action_taken, '')::TINYINT,
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

INSRT INTO Ethnicity (ethnicity_code, ethnicity_name)
SELECT DISTINCT
    NULLIF(applicant_ethnicity, '')::TINYINT,
    NULLIF(applicant_ethnicity_name, '')
FROM Preliminary
WHERE applicant_ethnicity != ''
UNION
SELECT DISTINCT
    NULLIF(co_applicant_ethnicity, '')::TINYINT,
    NULL(co_applicant_ethnicity_name, '')
FROM Preliminary
WHERE co_applicant_ethnicity != '';

INSERT INTO Race (race_code, race_name)
SELECT DISTINCT 
    NULLIF(applicant_race_1, '')::TINYINT, 
    NULLIF(applicant_race_name_1, '')
FROM Preliminary
WHERE applicant_race_1 != ''
UNION
SELECT DISTINCT 
    NULLIF(applicant_race_2, '')::TINYINT, 
    NULLIF(applicant_race_name_2, '')
FROM Preliminary
WHERE applicant_race_2 != ''
UNION
SELECT DISTINCT 
    NULLIF(applicant_race_3, '')::TINYINT, 
    NULLIF(applicant_race_name_3, '')
FROM Preliminary
WHERE applicant_race_3 != ''
UNION
SELECT DISTINCT 
    NULLIF(applicant_race_4, '')::TINYINT, 
    NULLIF(applicant_race_name_4, '')
FROM Preliminary
WHERE applicant_race_4 != ''
UNION
SELECT DISTINCT 
    NULLIF(applicant_race_5, '')::TINYINT, 
    NULLIF(applicant_race_name_5, '')
FROM Preliminary
WHERE applicant_race_5 != ''
UNION
SELECT DISTINCT 
    NULLIF(co_applicant_race_1, '')::TINYINT, 
    NULLIF(co_applicant_race_name_1, '')
FROM Preliminary
WHERE co_applicant_race_1 != ''
UNION
SELECT DISTINCT 
    NULLIF(co_applicant_race_2, '')::TINYINT, 
    NULLIF(co_applicant_race_name_2, '')
FROM Preliminary
WHERE co_applicant_race_2 != ''
UNION
SELECT DISTINCT 
    NULLIF(co_applicant_race_3, '')::TINYINT, 
    NULLIF(co_applicant_race_name_3, '')
FROM Preliminary
WHERE co_applicant_race_3 != ''
UNION
SELECT DISTINCT 
    NULLIF(co_applicant_race_4, '')::TINYINT, 
    NULLIF(co_applicant_race_name_4, '')
FROM Preliminary
WHERE co_applicant_race_4 != ''
UNION
SELECT DISTINCT 
    NULLIF(co_applicant_race_5, '')::TINYINT, 
    NULLIF(co_applicant_race_name_5, '')
FROM Preliminary
WHERE co_applicant_race_5 != '';

INSERT INTO Sex (sex_code, sex_name)
SELECT DISTINCT 
    NULLIF(applicant_sex, '')::TINYINT, 
    NULLIF(applicant_sex_name, '')
FROM Preliminary
WHERE applicant_sex != ''
UNION
SELECT DISTINCT 
    NULLIF(co_applicant_sex, '')::TINYINT, 
    NULLIF(co_applicant_sex_name, '')
FROM Preliminary
WHERE co_applicant_sex != '';

INSERT INTO PurchaserType (purchaser_type, purchaser_type_name)
SELECT DISTINCT 
    NULLIF(purchaser_type, '')::TINYINT, 
    NULLIF(purchaser_type_name, '')
FROM Preliminary
WHERE purchaser_type != '';

INSERT INTO DenialReason (denial_reason_code, denial_reason_name)
SELECT DISTINCT 
    NULLIF(denial_reason_1, '')::TINYINT, 
    NULLIF(denial_reason_name_1, '')
FROM Preliminary
WHERE denial_reason_1 != ''
UNION
SELECT DISTINCT 
    NULLIF(denial_reason_2, '')::TINYINT, 
    NULLIF(denial_reason_name_2, '')
FROM Preliminary
WHERE denial_reason_2 != ''
UNION
SELECT DISTINCT 
    NULLIF(denial_reason_3, '')::TINYINT, 
    NULLIF(denial_reason_name_3, '')
FROM Preliminary
WHERE denial_reason_3 != '';

INSERT INTO HOEPAStatus (hoepa_status, hoepa_status_name)
SELECT DISTINCT 
    NULLIF(hoepa_status, '')::TINYINT, 
    NULLIF(hoepa_status_name, '')
FROM Preliminary
WHERE hoepa_status != '';

INSERT INTO LienStatus (lien_status, lien_status_name)
SELECT DISTINCT 
    NULLIF(lien_status, '')::TINYINT, 
    NULLIF(lien_status_name, '')
FROM Preliminary
WHERE lien_status != '';

INSERT INTO EditStatus (edit_status, edit_status_name)
SELECT DISTINCT 
    NULLIF(edit_status, '')::TINYINT, 
    NULLIF(edit_status_name, '')
FROM Preliminary
WHERE edit_status != '';

-- Insert into RespondentAgency
INSERT INTO RespondentAgency (as_of_year, respondent_id, agency_code)
SELECT DISTINCT 
    NULLIF(as_of_year, '')::INTEGER, 
    NULLIF(respondent_id, ''), 
    NULLIF(agency_code, '')::TINYINT
FROM Preliminary
WHERE as_of_year != '' AND respondent_id != '' AND agency_code != '';



-- LOCATION TABLE NEXT
-- use temporary table to store distinct locations

CREATE TEMP TABLE DistinctLocations AS

-- to be done

FROM Preliminary;