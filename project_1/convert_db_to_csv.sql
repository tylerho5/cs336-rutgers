-- create a view that reconstructs the original data format
DROP VIEW IF EXISTS to_csv;
CREATE VIEW to_csv AS
SELECT
    COALESCE(la.ID::text, '') AS ID,
    COALESCE(la.as_of_year::text, '') AS as_of_year,
    COALESCE(la.respondent_id, '') AS respondent_id,
    COALESCE(a.agency_name, '') AS agency_name,
    COALESCE(a.agency_abbr, '') AS agency_abbr,
    COALESCE(ra.agency_code::text, '') AS agency_code,
    
    -- loan details
    COALESCE(lt.loan_type_name, '') AS loan_type_name,
    COALESCE(la.loan_type::text, '') AS loan_type,
    COALESCE(pt.property_type_name, '') AS property_type_name,
    COALESCE(la.property_type::text, '') AS property_type,
    COALESCE(lp.loan_purpose_name, '') AS loan_purpose_name,
    COALESCE(la.loan_purpose::text, '') AS loan_purpose,
    COALESCE(oo.owner_occupancy_name, '') AS owner_occupancy_name,
    COALESCE(la.owner_occupancy::text, '') AS owner_occupancy,
    COALESCE(la.loan_amount_000s::text, '') AS loan_amount_000s,
    COALESCE(pa.preapproval_name, '') AS preapproval_name,
    COALESCE(la.preapproval::text, '') AS preapproval,
    COALESCE(at.action_taken_name, '') AS action_taken_name,
    COALESCE(la.action_taken::text, '') AS action_taken,
    
    -- location information
    COALESCE(m.msamd_name, '') AS msamd_name,
    COALESCE(loc.msamd, '') AS msamd,
    COALESCE(s.state_name, '') AS state_name,
    COALESCE(s.state_abbr, '') AS state_abbr,
    COALESCE(loc.state_code, '') AS state_code,
    COALESCE(c.county_name, '') AS county_name,
    COALESCE(loc.county_code, '') AS county_code,
    COALESCE(loc.census_tract_number, '') AS census_tract_number,

    
    -- applicant and co-applicant ethnicity fields
    COALESCE(e1.ethnicity_name, '') AS applicant_ethnicity_name,   
    COALESCE(la.applicant_ethnicity::text, '') AS applicant_ethnicity,
    COALESCE(e2.ethnicity_name, '') AS co_applicant_ethnicity_name,
    COALESCE(la.co_applicant_ethnicity::text, '') AS co_applicant_ethnicity,

    -- applicant race fields
    COALESCE((SELECT r.race_name FROM ApplicantRace ar JOIN Race r ON ar.race_code = r.race_code WHERE ar.ID = la.ID AND ar.race_number = 1), '') AS applicant_race_name_1,
    COALESCE((SELECT race_code::text FROM ApplicantRace WHERE ID = la.ID AND race_number = 1), '') AS applicant_race_1,
    COALESCE((SELECT r.race_name FROM ApplicantRace ar JOIN Race r ON ar.race_code = r.race_code WHERE ar.ID = la.ID AND ar.race_number = 2), '') AS applicant_race_name_2,
    COALESCE((SELECT race_code::text FROM ApplicantRace WHERE ID = la.ID AND race_number = 2), '') AS applicant_race_2,
    COALESCE((SELECT r.race_name FROM ApplicantRace ar JOIN Race r ON ar.race_code = r.race_code WHERE ar.ID = la.ID AND ar.race_number = 3), '') AS applicant_race_name_3,
    COALESCE((SELECT race_code::text FROM ApplicantRace WHERE ID = la.ID AND race_number = 3), '') AS applicant_race_3,
    COALESCE((SELECT r.race_name FROM ApplicantRace ar JOIN Race r ON ar.race_code = r.race_code WHERE ar.ID = la.ID AND ar.race_number = 4), '') AS applicant_race_name_4,
    COALESCE((SELECT race_code::text FROM ApplicantRace WHERE ID = la.ID AND race_number = 4), '') AS applicant_race_4,
    COALESCE((SELECT r.race_name FROM ApplicantRace ar JOIN Race r ON ar.race_code = r.race_code WHERE ar.ID = la.ID AND ar.race_number = 5), '') AS applicant_race_name_5,
    COALESCE((SELECT race_code::text FROM ApplicantRace WHERE ID = la.ID AND race_number = 5), '') AS applicant_race_5,
 
    -- co-applicant race fields
    COALESCE((SELECT r.race_name FROM CoApplicantRace car JOIN Race r ON car.race_code = r.race_code WHERE car.ID = la.ID AND car.race_number = 1), '') AS co_applicant_race_name_1,
    COALESCE((SELECT race_code::text FROM CoApplicantRace WHERE ID = la.ID AND race_number = 1), '') AS co_applicant_race_1,
    COALESCE((SELECT r.race_name FROM CoApplicantRace car JOIN Race r ON car.race_code = r.race_code WHERE car.ID = la.ID AND car.race_number = 2), '') AS co_applicant_race_name_2,
    COALESCE((SELECT race_code::text FROM CoApplicantRace WHERE ID = la.ID AND race_number = 2), '') AS co_applicant_race_2,
    COALESCE((SELECT r.race_name FROM CoApplicantRace car JOIN Race r ON car.race_code = r.race_code WHERE car.ID = la.ID AND car.race_number = 3), '') AS co_applicant_race_name_3,
    COALESCE((SELECT race_code::text FROM CoApplicantRace WHERE ID = la.ID AND race_number = 3), '') AS co_applicant_race_3,
    COALESCE((SELECT r.race_name FROM CoApplicantRace car JOIN Race r ON car.race_code = r.race_code WHERE car.ID = la.ID AND car.race_number = 4), '') AS co_applicant_race_name_4,
    COALESCE((SELECT race_code::text FROM CoApplicantRace WHERE ID = la.ID AND race_number = 4), '') AS co_applicant_race_4,
    COALESCE((SELECT r.race_name FROM CoApplicantRace car JOIN Race r ON car.race_code = r.race_code WHERE car.ID = la.ID AND car.race_number = 5), '') AS co_applicant_race_name_5,
    COALESCE((SELECT race_code::text FROM CoApplicantRace WHERE ID = la.ID AND race_number = 5), '') AS co_applicant_race_5,
    
    -- applicant and co-applicant sex fields
    COALESCE(s1.sex_name, '') AS applicant_sex_name,
    COALESCE(la.applicant_sex::text, '') AS applicant_sex,
    COALESCE(s2.sex_name, '') AS co_applicant_sex_name,
    COALESCE(la.co_applicant_sex::text, '') AS co_applicant_sex,
    
    COALESCE(la.applicant_income_000s::text, '') AS applicant_income_000s,
    COALESCE(pt2.purchaser_type_name, '') AS purchaser_type_name,
    COALESCE(la.purchaser_type::text, '') AS purchaser_type,
    
    -- denial reasons
    COALESCE((SELECT dr.denial_reason_name FROM DenialReasons d JOIN DenialReason dr ON d.denial_reason_code = dr.denial_reason_code WHERE d.ID = la.ID AND d.reason_number = 1), '') AS denial_reason_name_1,
    COALESCE((SELECT denial_reason_code::text FROM DenialReasons WHERE ID = la.ID AND reason_number = 1), '') AS denial_reason_1,
    COALESCE((SELECT dr.denial_reason_name FROM DenialReasons d JOIN DenialReason dr ON d.denial_reason_code = dr.denial_reason_code WHERE d.ID = la.ID AND d.reason_number = 2), '') AS denial_reason_name_2,
    COALESCE((SELECT denial_reason_code::text FROM DenialReasons WHERE ID = la.ID AND reason_number = 2), '') AS denial_reason_2,
    COALESCE((SELECT dr.denial_reason_name FROM DenialReasons d JOIN DenialReason dr ON d.denial_reason_code = dr.denial_reason_code WHERE d.ID = la.ID AND d.reason_number = 3), '') AS denial_reason_name_3,    
    COALESCE((SELECT denial_reason_code::text FROM DenialReasons WHERE ID = la.ID AND reason_number = 3), '') AS denial_reason_3,
    
    -- location details
    COALESCE(la.rate_spread, '') AS rate_spread,
    COALESCE(h.hoepa_status_name, '') AS hoepa_status_name,
    COALESCE(la.hoepa_status::text, '') AS hoepa_status,  
    COALESCE(ls.lien_status_name, '') AS lien_status_name, 
    COALESCE(la.lien_status::text, '') AS lien_status,
    COALESCE(es.edit_status_name, '') AS edit_status_name,
    COALESCE(la.edit_status::text, '') AS edit_status,
    COALESCE(la.sequence_number, '') AS sequence_number,
    COALESCE(loc.population::text, '') AS population,
    COALESCE(loc.minority_population::text, '') AS minority_population,
    COALESCE(loc.hud_median_family_income::text, '') AS hud_median_family_income,
    COALESCE(loc.tract_to_msamd_income::text, '') AS tract_to_msamd_income,
    COALESCE(loc.number_of_owner_occupied_units::text, '') AS number_of_owner_occupied_units,
    COALESCE(loc.number_of_1_to_4_family_units::text, '') AS number_of_1_to_4_family_units,
    COALESCE(la.application_date_indicator::text, '') AS application_date_indicator

FROM LoanApplication la
LEFT JOIN Location loc ON la.location_id = loc.location_id
LEFT JOIN LoanType lt ON la.loan_type = lt.loan_type
LEFT JOIN PropertyType pt ON la.property_type = pt.property_type
LEFT JOIN LoanPurpose lp ON la.loan_purpose = lp.loan_purpose
LEFT JOIN OwnerOccupancy oo ON la.owner_occupancy = oo.owner_occupancy
LEFT JOIN Preapproval pa ON la.preapproval = pa.preapproval
LEFT JOIN ActionTaken at ON la.action_taken = at.action_taken
LEFT JOIN MSA m ON loc.msamd = m.msamd
LEFT JOIN State s ON loc.state_code = s.state_code
LEFT JOIN County c ON loc.county_code = c.county_code AND loc.state_code = c.state_code
LEFT JOIN Ethnicity e1 ON la.applicant_ethnicity = e1.ethnicity_code
LEFT JOIN Ethnicity e2 ON la.co_applicant_ethnicity = e2.ethnicity_code
LEFT JOIN Sex s1 ON la.applicant_sex = s1.sex_code
LEFT JOIN Sex s2 ON la.co_applicant_sex = s2.sex_code
LEFT JOIN PurchaserType pt2 ON la.purchaser_type = pt2.purchaser_type
LEFT JOIN HOEPAStatus h ON la.hoepa_status = h.hoepa_status
LEFT JOIN LienStatus ls ON la.lien_status = ls.lien_status
LEFT JOIN EditStatus es ON la.edit_status = es.edit_status
LEFT JOIN RespondentAgency ra ON la.as_of_year = ra.as_of_year AND la.respondent_id = ra.respondent_id
LEFT JOIN Agency a ON ra.agency_code = a.agency_code;

-- export the view to a CSV file
\COPY (SELECT * from to_csv) TO '/Users/tylerho/Docs/GitHub/cs336-rutgers/project_1/recreated_mortgage_data.csv' WITH CSV HEADER DELIMITER ',';


