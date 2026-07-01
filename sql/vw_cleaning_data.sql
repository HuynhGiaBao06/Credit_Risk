-- 1. Xóa View cũ để tránh lỗi xung đột cấu trúc cột
DROP VIEW IF EXISTS vw_cleaning_data;

-- 2. Tạo lại View mới
CREATE VIEW vw_cleaning_data AS
WITH MedianByGrade AS (
    SELECT
        loan_grade,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY loan_int_rate) AS median_rate
    FROM db_credit_risk
    WHERE loan_int_rate IS NOT NULL
    GROUP BY loan_grade
),
MedianPercentIncome AS (
    SELECT
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY loan_percent_income) AS median_pct_income
    FROM db_credit_risk
    WHERE loan_percent_income IS NOT NULL
),
MedianEmpByAge AS (
    SELECT
        person_age,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY person_emp_length) AS median_emp
    FROM db_credit_risk
    WHERE person_emp_length > 0 AND person_emp_length IS NOT NULL
    GROUP BY person_age
),
CleanData AS (
    -- Khối này CHỈ tính toán Imputation cho các biến bị khuyết
    SELECT
        d.id,
        COALESCE(
            NULLIF(d.person_emp_length, 0), 
            ea.median_emp, 
            0.5
        ) AS person_emp_length,
        
        COALESCE(d.loan_int_rate, m.median_rate) AS loan_int_rate,
        COALESCE(d.loan_percent_income, mpi.median_pct_income) AS loan_percent_income,
        
        ROW_NUMBER() OVER (PARTITION BY d.id ORDER BY d.id) AS rn
    FROM db_credit_risk d
    LEFT JOIN MedianByGrade m ON d.loan_grade = m.loan_grade
    LEFT JOIN MedianEmpByAge ea ON d.person_age = ea.person_age
    CROSS JOIN MedianPercentIncome mpi
    WHERE d.person_age <= 100
      AND (
          d.person_emp_length IS NULL 
          OR (d.person_emp_length >= 0 AND d.person_emp_length <= d.person_age AND d.person_emp_length <= 100)
      )
      AND d.loan_amnt > 0
      AND d.person_income >= 0
)
-- Truy vấn chính: SELECT trực tiếp từ db_credit_risk kết hợp các cột đã làm sạch từ CleanData
SELECT 
    d.loan_status, 
    d.person_age, 
    d.person_income, 
    d.person_home_ownership, 
    c.person_emp_length, 
    d.cb_person_default_on_file, 
    d.cb_person_cred_hist_length, 
    d.loan_intent, 
    d.loan_grade, 
    d.loan_amnt, 
    c.loan_int_rate, 
    c.loan_percent_income
FROM db_credit_risk d
JOIN CleanData c ON d.id = c.id
WHERE c.rn = 1;

SELECT
    COUNT(*) FILTER (WHERE person_age IS NULL) AS person_age_null,
    COUNT(*) FILTER (WHERE person_age = 0) AS person_age_zero,

    COUNT(*) FILTER (WHERE person_income IS NULL) AS person_income_null,
    COUNT(*) FILTER (WHERE person_income = 0) AS person_income_zero,

    COUNT(*) FILTER (WHERE person_emp_length IS NULL) AS person_emp_length_null,
    COUNT(*) FILTER (WHERE person_emp_length = 0) AS person_emp_length_zero,

    COUNT(*) FILTER (WHERE cb_person_cred_hist_length IS NULL) AS cred_hist_length_null,
    COUNT(*) FILTER (WHERE cb_person_cred_hist_length = 0) AS cred_hist_length_zero,

    COUNT(*) FILTER (WHERE loan_amnt IS NULL) AS loan_amnt_null,
    COUNT(*) FILTER (WHERE loan_amnt = 0) AS loan_amnt_zero,

    COUNT(*) FILTER (WHERE loan_int_rate IS NULL) AS loan_int_rate_null,
    COUNT(*) FILTER (WHERE loan_int_rate = 0) AS loan_int_rate_zero,

    COUNT(*) FILTER (WHERE loan_percent_income IS NULL) AS loan_percent_income_null,
    COUNT(*) FILTER (WHERE loan_percent_income = 0) AS loan_percent_income_zero
FROM vw_cleaning_data;