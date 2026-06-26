-- Phân tích đối với person_emp_length
SELECT 
    CASE 
        WHEN person_age <= 25 THEN 'Under 25'
        WHEN person_age >= 26 AND person_age < 40 THEN '26 to 39'
        WHEN person_age >= 40 THEN '40 and above'
    END AS age_group,
    AVG(person_emp_length) AS avg_emp_length, -- Tính trung bình thời gian làm việc
    COUNT(*) AS total_people                  -- Đếm số lượng người trong mỗi nhóm
FROM db_credit_risk
GROUP BY 
    CASE 
        WHEN person_age <= 25 THEN 'Under 25'
        WHEN person_age >= 26 AND person_age < 40 THEN '26 to 39'
        WHEN person_age >= 40 THEN '40 and above'
    END;

-- Phân tích đối với person_int_rate
SELECT 
    loan_grade, 
    COUNT(*) as loan_count,
    MIN(loan_int_rate) as min_rate,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY loan_int_rate) as median_rate,
    MAX(loan_int_rate) as max_rate
FROM db_credit_risk
GROUP BY loan_grade
ORDER BY loan_grade

SELECT 
    loan_grade, 
    COUNT(loan_int_rate) as valid_loans,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY loan_int_rate) as p25_rate,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY loan_int_rate) as median_rate,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY loan_int_rate) as p75_rate
FROM db_credit_risk
WHERE loan_int_rate IS NOT NULL
GROUP BY loan_grade
ORDER BY loan_grade

-- Bước 1: Tính Median cho từng hạng
WITH MedianData AS (
    SELECT 
        loan_grade, 
        COUNT(loan_int_rate) as valid_loans,
        -- PERCENTILE_CONT là chuẩn của PostgreSQL để tính trung vị
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY loan_int_rate) as median_rate
    FROM db_credit_risk 
    WHERE loan_int_rate IS NOT NULL
    GROUP BY loan_grade
)

SELECT 
    m.loan_grade,
    m.median_rate,
    m.valid_loans as total_loans,
    -- Tận dụng FILTER của PostgreSQL: Ngắn gọn và tối ưu hiệu suất hơn CASE WHEN
    COUNT(*) FILTER (
        WHERE l.loan_int_rate >= (m.median_rate - 1.5) 
          AND l.loan_int_rate <= (m.median_rate + 1.5)
    ) as loans_in_range,
    -- Tính tỷ lệ phần trăm (%)
    ROUND(
        (COUNT(*) FILTER (
            WHERE l.loan_int_rate >= (m.median_rate - 1.5) 
              AND l.loan_int_rate <= (m.median_rate + 1.5)
        ) * 100.0 / m.valid_loans), 2
    ) as pct_in_range

FROM db_credit_risk l
JOIN MedianData m ON l.loan_grade = m.loan_grade
WHERE l.loan_int_rate IS NOT NULL
GROUP BY m.loan_grade, m.median_rate, m.valid_loans
ORDER BY m.loan_grade