CREATE VIEW vw_credit_risk
AS
SELECT 
    loan_status, 
    person_age, 
    person_income, 
    person_home_ownership, 
    person_emp_length, 
    cb_person_default_on_file, 
    cb_person_cred_hist_length, 
    loan_intent, 
    loan_grade, 
    loan_amnt, 
    loan_int_rate, 
    loan_percent_income
FROM db_credit_risk;

DROP VIEW vw_credit_risk