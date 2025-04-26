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