--ID Already exists
INSERT INTO LoanApplication (
    ID, as_of_year, respondent_id,
    loan_type, property_type, loan_purpose, owner_occupancy,
    loan_amount_000s, preapproval, action_taken,
    location_id, applicant_ethnicity, co_applicant_ethnicity,
    applicant_sex, co_applicant_sex, applicant_income_000s,
    purchaser_type, hoepa_status, lien_status
)
VALUES (
    1, 2017, '0000035186',
    1, 1, 1, 1,
    250, 1, 1,
    1, 1, NULL,
    1, NULL, 80,
    1, 1, 1
);



-- Invalid respondent_id, as_of_year combination
INSERT INTO LoanApplication (
    ID, as_of_year, respondent_id,
    loan_type, property_type, loan_purpose, owner_occupancy,
    loan_amount_000s, preapproval, action_taken,
    location_id, applicant_ethnicity, co_applicant_ethnicity,
    applicant_sex, co_applicant_sex, applicant_income_000s,
    purchaser_type, hoepa_status, lien_status
)
VALUES (
    123456789, 2022, 'test01',
    1, 1, 1, 1,
    250, 1, 1,
    1, 1, NULL,
    1, NULL, 80,
    1, 1, 1
);



-- Invalid Property type code: 999 is not a valid property type
INSERT INTO LoanApplication (
    ID, as_of_year, respondent_id,
    loan_type, property_type, loan_purpose, owner_occupancy,
    loan_amount_000s, preapproval, action_taken,
    location_id, applicant_ethnicity, co_applicant_ethnicity,
    applicant_sex, co_applicant_sex, applicant_income_000s,
    purchaser_type, hoepa_status, lien_status
)
VALUES (
    123456789, 2017, '0000035186',
    1, 999, 1, 1,
    250, 1, 1,
    1, 1, NULL,
    1, NULL, 80,
    1, 1, 1
);



-- VALID INSERTION
INSERT INTO LoanApplication (
    ID, as_of_year, respondent_id,
    loan_type, property_type, loan_purpose, owner_occupancy,
    loan_amount_000s, preapproval, action_taken,
    location_id, applicant_ethnicity, co_applicant_ethnicity,
    applicant_sex, co_applicant_sex, applicant_income_000s,
    purchaser_type, hoepa_status, lien_status
)
VALUES (
    123456789, 2017, '0000035186',
    1, 1, 1, 1,
    250, 1, 1,
    1, 1, NULL,
    1, NULL, 80,
    1, 1, 1
);