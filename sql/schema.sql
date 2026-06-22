
ALTER SCHEMA public OWNER TO CURRENT_USER;
GRANT ALL ON SCHEMA public TO CURRENT_USER;
SELECT current_user;

CREATE TABLE DB_CREDIT_RISK (
    id BIGINT PRIMARY KEY,                  -- Dùng ngoặc kép vì index là từ khóa nhạy cảm
    person_age INTEGER NOT NULL,
    person_income BIGINT NOT NULL,
    person_home_ownership VARCHAR(100) NOT NULL,
    person_emp_length DOUBLE PRECISION,          -- Bỏ trống NOT NULL để nhận giá trị NULL (từ 895 NaN)
    loan_intent VARCHAR(100) NOT NULL,
    loan_grade INTEGER NOT NULL,
    loan_amnt BIGINT NOT NULL,
    loan_int_rate DOUBLE PRECISION,              -- Bỏ trống NOT NULL để nhận giá trị NULL (từ 3116 NaN)
    loan_status BIT NOT NULL,
    loan_percent_income DOUBLE PRECISION NOT NULL,
    cb_person_default_on_file BIT NOT NULL,
    cb_person_cred_hist_length INTEGER NOT NULL
);