WITH MedianByGrade AS (
    SELECT
        loan_grade,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY loan_int_rate) AS median_rate
    FROM db_credit_risk
    WHERE loan_int_rate IS NOT NULL
    GROUP BY loan_grade
),
-- Tạo thêm CTE để tính thâm niên trung vị theo từng độ tuổi
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

SELECT *
FROM CleanData
WHERE rn = 1;s