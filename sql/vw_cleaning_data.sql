CREATE OR REPLACE VIEW vw_cleaning_data AS
WITH MedianByGrade AS (
    SELECT
        loan_grade,
        -- Đã xóa loan_percent_income ở đây để tránh lỗi GROUP BY và thiếu dấu phẩy
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY loan_int_rate) AS median_rate
    FROM db_credit_risk
    WHERE loan_int_rate IS NOT NULL 
      AND loan_percent_income IS NOT NULL
    GROUP BY loan_grade
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
    SELECT
        d.id,
        d.person_age,
        d.person_income, 
        -- Nếu emp_length là NULL hoặc 0, thay bằng thâm niên trung vị của độ tuổi đó. 
        -- Nếu độ tuổi đó cũng không có trung vị, thì dự phòng gán bằng 0.5
        COALESCE(
            NULLIF(d.person_emp_length, 0), 
            ea.median_emp, 
            0.5
        ) AS person_emp_length,
        
        d.loan_amnt,
        COALESCE(d.loan_int_rate, m.median_rate) AS loan_int_rate,
        d.loan_status,
        d.loan_grade,
        d.cb_person_cred_hist_length,
        d.loan_percent_income,
        ROW_NUMBER() OVER (PARTITION BY d.id ORDER BY d.id) AS rn
    FROM db_credit_risk d
    LEFT JOIN MedianByGrade m
        ON d.loan_grade = m.loan_grade
    LEFT JOIN MedianEmpByAge ea
        ON d.person_age = ea.person_age
    WHERE d.person_age <= 100
      AND (
          d.person_emp_length IS NULL 
          OR (d.person_emp_length >= 0 AND d.person_emp_length <= d.person_age AND d.person_emp_length <= 100)
      )
      AND d.loan_amnt > 0
      AND d.person_income >= 0
)
-- Truy vấn chính của View (lọc rn = 1 để xóa trùng lặp và không hiển thị cột rn)
SELECT 
    id,
    person_age,
    person_income,
    person_emp_length,
    loan_amnt,
    loan_int_rate,
    loan_status,
    loan_grade,
    cb_person_cred_hist_length,
    loan_percent_income
FROM CleanData
WHERE rn = 1;

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