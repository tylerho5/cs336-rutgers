-- create initial tables based on 3NF

-- Agency table
CREATE TABLE Agency (
    agency_code CHAR(1) PRIMARY KEY,
    agency_name VARCHAR(100) NOT NULL,
    agency_abbr VARCHAR(20) NOT NULL
);

-- LoanType table
CREATE TABLE LoanType (
    loan_type CHAR(1) PRIMARY KEY,
    loan_type_name VARCHAR(100) NOT NULL
);

-- PropertyType table
CREATE TABLE PropertyType (
    property_type CHAR(1) PRIMARY KEY,
    property_type_name VARCHAR(100) NOT NULL
);

-- LoanPurpose table
CREATE TABLE LoanPurpose (
    loan_purpose CHAR(1) PRIMARY KEY,
    loan_purpose_name VARCHAR(100) NOT NULL
);

-- OwnerOccupancy table
CREATE TABLE OwnerOccupancy (
    owner_occupancy CHAR(1) PRIMARY KEY,
    owner_occupancy_name VARCHAR(100) NOT NULL
);

-- Preapproval table
CREATE TABLE Preapproval (
    preapproval CHAR(1) PRIMARY KEY,
    preapproval_name VARCHAR(100) NOT NULL
);

-- ActionTaken table
CREATE TABLE ActionTaken (
    action_taken CHAR(1) PRIMARY KEY,
    action_taken_name VARCHAR(100) NOT NULL
);

-- MSA table
CREATE TABLE MSA (
    msamd VARCHAR(5) PRIMARY KEY,
    msamd_name VARCHAR(100) NOT NULL
);

-- State table
CREATE TABLE State (
    state_code CHAR(2) PRIMARY KEY,
    state_name VARCHAR(100) NOT NULL,
    state_abbr CHAR(2) NOT NULL
);

-- County table
CREATE TABLE County (
    county_code CHAR(3),
    state_code CHAR(2),
    county_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (county_code, state_code),
    FOREIGN KEY (state_code) REFERENCES State(state_code)
);

-- EthnicityName table
CREATE TABLE EthnicityName (
    ethnicity_code CHAR(1) PRIMARY KEY,
    ethnicity_name VARCHAR(100) NOT NULL
);

-- RaceName table
CREATE TABLE RaceName (
    race_code CHAR(1) PRIMARY KEY,
    race_name VARCHAR(100) NOT NULL
);

-- SexName table
CREATE TABLE SexName (
    sex_code CHAR(1) PRIMARY KEY,
    sex_name VARCHAR(100) NOT NULL
);

-- PurchaserType table
CREATE TABLE PurchaserType (
    purchaser_type CHAR(1) PRIMARY KEY,
    purchaser_type_name VARCHAR(100) NOT NULL
);

-- DenialReasonName table
CREATE TABLE DenialReasonName (
    denial_reason_code CHAR(1) PRIMARY KEY,
    denial_reason_name VARCHAR(100) NOT NULL
);

-- HOEPAStatus table
CREATE TABLE HOEPAStatus (
    hoepa_status CHAR(1) PRIMARY KEY,
    hoepa_status_name VARCHAR(100) NOT NULL
);

-- LienStatus table
CREATE TABLE LienStatus (
    lien_status CHAR(1) PRIMARY KEY,
    lien_status_name VARCHAR(100) NOT NULL
);

-- EditStatus table
CREATE TABLE EditStatus (
    edit_status CHAR(1) PRIMARY KEY,
    edit_status_name VARCHAR(100) NOT NULL
);

-- Location table with added primary key
CREATE TABLE Location (
    location_id SERIAL PRIMARY KEY,
    msamd VARCHAR(5),
    state_code CHAR(2),
    county_code CHAR(3),
    census_tract_number VARCHAR(8),
    population INTEGER,
    minority_population NUMERIC(5,2),
    hud_median_family_income INTEGER,
    tract_to_msamd_income NUMERIC(6,2),
    number_of_owner_occupied_units INTEGER,
    number_of_1_to_4_family_units INTEGER,
    FOREIGN KEY (msamd) REFERENCES MSA(msamd),
    FOREIGN KEY (state_code) REFERENCES State(state_code),
    FOREIGN KEY (county_code, state_code) REFERENCES County(county_code, state_code)
);

-- RespondentAgency table
CREATE TABLE RespondentAgency (
    as_of_year INTEGER,
    respondent_id VARCHAR(10),
    agency_code CHAR(1),
    PRIMARY KEY (as_of_year, respondent_id),
    FOREIGN KEY (agency_code) REFERENCES Agency(agency_code)
);

-- Main LoanApplication table 
CREATE TABLE LoanApplication (
    ID INTEGER PRIMARY KEY,
    as_of_year INTEGER NOT NULL,
    respondent_id VARCHAR(10) NOT NULL,
    loan_type CHAR(1) NOT NULL,
    property_type CHAR(1) NOT NULL,
    loan_purpose CHAR(1) NOT NULL,
    owner_occupancy CHAR(1) NOT NULL,
    loan_amount_000s NUMERIC(8,2),
    preapproval CHAR(1) NOT NULL,
    action_taken CHAR(1) NOT NULL,
    location_id INTEGER NOT NULL,
    applicant_ethnicity CHAR(1) NOT NULL,
    co_applicant_ethnicity CHAR(1),
    applicant_sex CHAR(1) NOT NULL,
    co_applicant_sex CHAR(1),
    applicant_income_000s NUMERIC(8,2),
    purchaser_type CHAR(1),
    rate_spread VARCHAR(10),
    hoepa_status CHAR(1),
    lien_status CHAR(1),
    edit_status CHAR(1),
    sequence_number INTEGER,
    application_date_indicator CHAR(1),
    FOREIGN KEY (as_of_year, respondent_id) REFERENCES RespondentAgency(as_of_year, respondent_id),
    FOREIGN KEY (loan_type) REFERENCES LoanType(loan_type),
    FOREIGN KEY (property_type) REFERENCES PropertyType(property_type),
    FOREIGN KEY (loan_purpose) REFERENCES LoanPurpose(loan_purpose),
    FOREIGN KEY (owner_occupancy) REFERENCES OwnerOccupancy(owner_occupancy),
    FOREIGN KEY (preapproval) REFERENCES Preapproval(preapproval),
    FOREIGN KEY (action_taken) REFERENCES ActionTaken(action_taken),
    FOREIGN KEY (location_id) REFERENCES Location(location_id),
    FOREIGN KEY (applicant_ethnicity) REFERENCES EthnicityName(ethnicity_code),
    FOREIGN KEY (co_applicant_ethnicity) REFERENCES EthnicityName(ethnicity_code),
    FOREIGN KEY (applicant_sex) REFERENCES SexName(sex_code),
    FOREIGN KEY (co_applicant_sex) REFERENCES SexName(sex_code),
    FOREIGN KEY (purchaser_type) REFERENCES PurchaserType(purchaser_type),
    FOREIGN KEY (hoepa_status) REFERENCES HOEPAStatus(hoepa_status),
    FOREIGN KEY (lien_status) REFERENCES LienStatus(lien_status),
    FOREIGN KEY (edit_status) REFERENCES EditStatus(edit_status)
);