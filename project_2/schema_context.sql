-- Describes the regulatory agency associated with the respondent.
CREATE TABLE Agency (
    agency_code SMALLINT PRIMARY KEY, -- Unique code for the agency
    agency_name VARCHAR(100) NOT NULL, -- Full name of the agency
    agency_abbr VARCHAR(20) NOT NULL -- Abbreviation for the agency
);

-- Describes the type of loan (e.g., Conventional, FHA, VA).
CREATE TABLE LoanType (
    loan_type SMALLINT PRIMARY KEY, -- Unique code for the loan type
    loan_type_name VARCHAR(100) NOT NULL -- Name of the loan type
);

-- Describes the type of property (e.g., 1-4 family, Manufactured housing).
CREATE TABLE PropertyType (
    property_type SMALLINT PRIMARY KEY, -- Unique code for the property type
    property_type_name VARCHAR(100) NOT NULL -- Name of the property type
);

-- Describes the purpose of the loan (e.g., Home purchase, Refinancing).
CREATE TABLE LoanPurpose (
    loan_purpose SMALLINT PRIMARY KEY, -- Unique code for the loan purpose
    loan_purpose_name VARCHAR(100) NOT NULL -- Name of the loan purpose
);

-- Describes the owner occupancy status (e.g., Owner-occupied, Not owner-occupied).
CREATE TABLE OwnerOccupancy (
    owner_occupancy SMALLINT PRIMARY KEY, -- Unique code for occupancy status
    owner_occupancy_name VARCHAR(100) NOT NULL -- Name of the occupancy status
);

-- Describes whether preapproval was requested.
CREATE TABLE Preapproval (
    preapproval SMALLINT PRIMARY KEY, -- Unique code for preapproval status
    preapproval_name VARCHAR(100) NOT NULL -- Name of the preapproval status
);

-- Describes the action taken on the loan application (e.g., Loan originated, Application denied).
CREATE TABLE ActionTaken (
    action_taken SMALLINT PRIMARY KEY, -- Unique code for the action taken
    action_taken_name VARCHAR(100) NOT NULL -- Name of the action taken
);

-- Describes the Metropolitan Statistical Area/Metropolitan Division.
CREATE TABLE MSA (
    msamd VARCHAR(5) PRIMARY KEY, -- Unique code for the MSA/MD
    msamd_name VARCHAR(100) -- Name of the MSA/MD
);

-- Describes the state.
CREATE TABLE State (
    state_code CHAR(2) PRIMARY KEY, -- Unique 2-character code for the state (e.g., NJ)
    state_name VARCHAR(100) NOT NULL, -- Full name of the state
    state_abbr CHAR(2) NOT NULL -- Abbreviation for the state
);

-- Describes the county within a state.
CREATE TABLE County (
    county_code CHAR(3), -- Unique 3-digit code for the county within a state
    state_code CHAR(2), -- Foreign key referencing the State table
    county_name VARCHAR(100) NOT NULL, -- Name of the county
    PRIMARY KEY (county_code, state_code),
    FOREIGN KEY (state_code) REFERENCES State(state_code)
);

-- Describes the ethnicity of an applicant.
CREATE TABLE Ethnicity (
    ethnicity_code SMALLINT PRIMARY KEY, -- Unique code for ethnicity
    ethnicity_name VARCHAR(100) NOT NULL -- Name of the ethnicity (e.g., Hispanic or Latino)
);

-- Describes the race of an applicant. Note: Applicants can report multiple races.
CREATE TABLE Race (
    race_code SMALLINT PRIMARY KEY, -- Unique code for race
    race_name VARCHAR(100) NOT NULL -- Name of the race (e.g., White, Black or African American)
);

-- Describes the sex of an applicant.
CREATE TABLE Sex (
    sex_code SMALLINT PRIMARY KEY, -- Unique code for sex
    sex_name VARCHAR(100) NOT NULL -- Name of the sex (e.g., Male, Female)
);

-- Describes the type of entity that purchased the loan.
CREATE TABLE PurchaserType (
    purchaser_type SMALLINT PRIMARY KEY, -- Unique code for the purchaser type
    purchaser_type_name VARCHAR(100) NOT NULL -- Name of the purchaser type (e.g., Fannie Mae, Ginnie Mae)
);

-- Describes the reasons for loan denial. Note: Multiple reasons can be reported.
CREATE TABLE DenialReason (
    denial_reason_code SMALLINT PRIMARY KEY, -- Unique code for the denial reason
    denial_reason_name VARCHAR(100) NOT NULL -- Name of the denial reason (e.g., Debt-to-income ratio)
);

-- Describes the HOEPA (Home Ownership and Equity Protection Act) status.
CREATE TABLE HOEPAStatus (
    hoepa_status SMALLINT PRIMARY KEY, -- Unique code for HOEPA status
    hoepa_status_name VARCHAR(100) NOT NULL -- Name of the HOEPA status (e.g., HOEPA loan, Not a HOEPA loan)
);

-- Describes the lien status of the loan.
CREATE TABLE LienStatus (
    lien_status SMALLINT PRIMARY KEY, -- Unique code for lien status
    lien_status_name VARCHAR(100) NOT NULL -- Name of the lien status (e.g., Secured by first lien)
);

-- Describes the edit status (related to data validation).
CREATE TABLE EditStatus (
    edit_status SMALLINT PRIMARY KEY, -- Unique code for edit status
    edit_status_name VARCHAR(100) NOT NULL -- Name of the edit status
);

-- Stores detailed location information including census tract data. Links to MSA, State, and County.
CREATE TABLE Location (
    location_id SERIAL PRIMARY KEY, -- Unique identifier for a specific location combination
    msamd VARCHAR(5), -- Foreign key referencing MSA
    state_code CHAR(2), -- Foreign key referencing State
    county_code CHAR(3), -- Foreign key referencing County (part of composite key)
    census_tract_number VARCHAR(8), -- Census tract number
    population INTEGER, -- Population of the census tract
    minority_population NUMERIC, -- Percentage of minority population in the tract
    hud_median_family_income INTEGER, -- HUD median family income for the area
    tract_to_msamd_income NUMERIC, -- Ratio of tract income to MSA/MD income
    number_of_owner_occupied_units INTEGER, -- Number of owner-occupied units in the tract
    number_of_1_to_4_family_units INTEGER, -- Number of 1-to-4 family units in the tract
    FOREIGN KEY (msamd) REFERENCES MSA(msamd),
    FOREIGN KEY (state_code) REFERENCES State(state_code),
    FOREIGN KEY (county_code, state_code) REFERENCES County(county_code, state_code)
);

-- Associates a respondent (lender) with their regulatory agency for a specific year.
CREATE TABLE RespondentAgency (
    as_of_year INTEGER, -- Reporting year
    respondent_id VARCHAR(10), -- Unique identifier for the respondent (lender)
    agency_code SMALLINT, -- Foreign key referencing Agency
    PRIMARY KEY (as_of_year, respondent_id),
    FOREIGN KEY (agency_code) REFERENCES Agency(agency_code)
);

-- Main table containing loan application details. Links to many other lookup tables.
CREATE TABLE LoanApplication (
    ID INTEGER PRIMARY KEY, -- Unique identifier for the loan application (generated during import)
    as_of_year INTEGER NOT NULL, -- Reporting year
    respondent_id VARCHAR(10) NOT NULL, -- Identifier for the respondent (lender)
    loan_type SMALLINT NOT NULL, -- Foreign key referencing LoanType
    property_type SMALLINT NOT NULL, -- Foreign key referencing PropertyType
    loan_purpose SMALLINT NOT NULL, -- Foreign key referencing LoanPurpose
    owner_occupancy SMALLINT NOT NULL, -- Foreign key referencing OwnerOccupancy
    loan_amount_000s NUMERIC, -- Loan amount in thousands of dollars
    preapproval SMALLINT NOT NULL, -- Foreign key referencing Preapproval
    action_taken SMALLINT NOT NULL, -- Foreign key referencing ActionTaken
    location_id INTEGER NOT NULL, -- Foreign key referencing Location
    applicant_ethnicity SMALLINT NOT NULL, -- Foreign key referencing Ethnicity
    co_applicant_ethnicity SMALLINT, -- Foreign key referencing Ethnicity (nullable)
    applicant_sex SMALLINT NOT NULL, -- Foreign key referencing Sex
    co_applicant_sex SMALLINT, -- Foreign key referencing Sex (nullable)
    applicant_income_000s NUMERIC, -- Applicant income in thousands of dollars (nullable)
    purchaser_type SMALLINT, -- Foreign key referencing PurchaserType (nullable)
    rate_spread VARCHAR(10), -- Rate spread information (nullable)
    hoepa_status SMALLINT, -- Foreign key referencing HOEPAStatus (nullable)
    lien_status SMALLINT, -- Foreign key referencing LienStatus (nullable)
    edit_status SMALLINT, -- Foreign key referencing EditStatus (nullable)
    sequence_number VARCHAR(20), -- Sequence number (nullable)
    application_date_indicator SMALLINT, -- Indicator for application date reporting (nullable)
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

-- Junction table linking LoanApplication to Race for the primary applicant. Allows multiple races per applicant.
CREATE TABLE ApplicantRace (
    ID INTEGER, -- Foreign key referencing LoanApplication
    race_number SMALLINT, -- Identifier for the race entry (1-5) for a given applicant
    race_code SMALLINT NOT NULL, -- Foreign key referencing Race
    PRIMARY KEY (ID, race_number),
    FOREIGN KEY (ID) REFERENCES LoanApplication(ID),
    FOREIGN KEY (race_code) REFERENCES Race(race_code)
);

-- Junction table linking LoanApplication to Race for the co-applicant. Allows multiple races per co-applicant.
CREATE TABLE CoApplicantRace (
    ID INTEGER, -- Foreign key referencing LoanApplication
    race_number SMALLINT, -- Identifier for the race entry (1-5) for a given co-applicant
    race_code SMALLINT NOT NULL, -- Foreign key referencing Race
    PRIMARY KEY (ID, race_number),
    FOREIGN KEY (ID) REFERENCES LoanApplication(ID),
    FOREIGN KEY (race_code) REFERENCES Race(race_code)
);

-- Junction table linking LoanApplication to DenialReason. Allows multiple denial reasons per application.
CREATE TABLE DenialReasons (
    ID INTEGER, -- Foreign key referencing LoanApplication
    reason_number SMALLINT, -- Identifier for the denial reason entry (1-3) for a given application
    denial_reason_code SMALLINT NOT NULL, -- Foreign key referencing DenialReason
    PRIMARY KEY (ID, reason_number),
    FOREIGN KEY (ID) REFERENCES LoanApplication(ID),
    FOREIGN KEY (denial_reason_code) REFERENCES DenialReason(denial_reason_code)
);