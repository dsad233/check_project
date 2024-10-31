SET SQL_SAFE_UPDATES = 0;
SET FOREIGN_KEY_CHECKS = 0;
-- branches 테이블에 데이터 삽입
INSERT INTO branches (code, name, representative_name, registration_number, call_number, address, mail_address, created_at, updated_at, deleted_yn)
VALUES
('BR001', '서울 본원', '김원장', '123-45-67890', '02-1234-5678', '서울시 강남구', 'seoul@skincare.com', '2024-10-28 11:23:16', '2024-10-28 11:23:16', 'N'),
('BR002', '부산 지점', '이원장', '234-56-78901', '051-2345-6789', '부산시 해운대구', 'busan@skincare.com', '2024-10-28 11:23:16', '2024-10-28 11:23:16', 'N'),
('BR003', '대구 지점', '박원장', '345-67-89012', '053-3456-7890', '대구시 중구', 'daegu@skincare.com', '2024-10-28 11:23:16', '2024-10-28 11:23:16', 'N');
-- parts 테이블에 데이터 삽입
INSERT INTO parts (branch_id, name, task, is_doctor, required_certification, leave_granting_authority, auto_annual_leave_grant, deleted_yn)
VALUES
(1, '피부과 의사', '진료', TRUE, TRUE, TRUE, '회계기준 부여', 'N'),
(1, '간호사', '간호', FALSE, TRUE, FALSE, '입사일 기준 부여', 'N'),
(2, '피부과 의사', '진료', TRUE, TRUE, TRUE, '회계기준 부여', 'N'),
(2, '피부관리사', '피부관리', FALSE, TRUE, FALSE, '입사일 기준 부여', 'N'),
(3, '피부과 의사', '진료', TRUE, TRUE, TRUE, '회계기준 부여', 'N'),
(3, '레이저 전문가', '레이저 시술', FALSE, TRUE, FALSE, '입사일 기준 부여', 'N');
-- users 테이블에 데이터 삽입
INSERT INTO users (name, email, password, phone_number, gender, branch_id, role, birth_date, address, hire_date, part_id, deleted_yn, employment_status)
VALUES
('김태희', 'kim', '1234', '010-1234-5678', '여자', 1, 'MSO 최고권한', '1980-01-01', '서울시 강남구', '2020-01-01', 1, 'N', '정규직'),
('이지은', 'lee', '1234', '010-2345-6789', '여자', 1, '사원', '1990-05-05', '서울시 서초구', '2021-03-01', 2, 'N', '계약직'),
('박서준', 'park', '1234', '010-3456-7890', '남자', 2, '최고관리자', '1985-12-20', '부산시 해운대구', '2019-06-01', 3, 'N', '정규직'),
('정유미', 'jung', '1234', '010-4567-8901', '여자', 3, '관리자', '1988-07-15', '대구시 수성구', '2022-01-01', 5, 'N', '정규직'),
('송중기', 'song', '1234', '010-5678-9012', '남자', 3, '사원', '1992-09-30', '대구시 달서구', '2023-02-01', 6, 'N', '계약직');
-- work_policies 테이블에 데이터 삽입
INSERT INTO work_policies (branch_id, weekly_work_days, weekday_start_time, weekday_end_time, weekday_is_holiday, saturday_start_time, saturday_end_time, saturday_is_holiday, sunday_start_time, sunday_end_time, sunday_is_holiday, doctor_lunch_start_time, doctor_lunch_end_time, doctor_dinner_start_time, doctor_dinner_end_time, common_lunch_start_time, common_lunch_end_time, common_dinner_start_time, common_dinner_end_time, created_at, updated_at, deleted_yn)
VALUES
(1, 5, '09:00:00', '18:00:00', FALSE, '16:26:39', '16:26:39', 1, '16:26:39', '16:26:39', 1, '16:26:39', '16:26:39', '16:26:39', '16:26:39', '16:26:39', '16:26:39', '16:26:39', '16:26:39', '2024-10-25 14:30:00', '2024-10-25 14:30:00', 'N'),
(2, 5, '09:00:00', '18:00:00', FALSE, '16:26:39', '16:26:39', 1, '16:26:39', '16:26:39', 1, '16:26:39', '16:26:39', '16:26:39', '16:26:39', '16:26:39', '16:26:39', '16:26:39', '16:26:39', '2024-10-25 14:30:00', '2024-10-25 14:30:00', 'N'),
(3, 5, '09:00:00', '18:00:00', FALSE, '16:26:39', '16:26:39', 1, '16:26:39', '16:26:39', 1, '16:26:39', '16:26:39', '16:26:39', '16:26:39', '16:26:39', '16:26:39', '16:26:39', '16:26:39', '2024-10-25 14:30:00', '2024-10-25 14:30:00', 'N');
-- leave_categories 테이블에 데이터 삽입
INSERT INTO leave_categories (branch_id, name, leave_count, is_paid, deleted_yn)
VALUES
(1, '연차', 15, TRUE, 'N'),
(1, '병가', 3, FALSE, 'N'),
(2, '연차', 15, TRUE, 'N'),
(2, '경조사', 5, TRUE, 'N'),
(3, '연차', 15, TRUE, 'N'),
(3, '출산휴가', 90, TRUE, 'N');
-- salary_policies 테이블에 데이터 삽입
INSERT INTO salary_policies (part_id, base_salary, annual_leave_days, sick_leave_days, overtime_rate, night_work_allowance, holiday_work_allowance, branch_id, deleted_yn)
VALUES
(1, 6000000, 15, 3, 1.5, 20000, 50000, 1, 'N'),
(2, 3500000, 15, 3, 1.5, 15000, 30000, 1, 'N'),
(3, 5800000, 15, 3, 1.5, 20000, 50000, 2, 'N'),
(4, 3000000, 15, 3, 1.5, 12000, 25000, 2, 'N'),
(5, 5500000, 15, 3, 1.5, 18000, 45000, 3, 'N'),
(6, 3800000, 15, 3, 1.5, 15000, 30000, 3, 'N');
-- commutes 테이블에 데이터 삽입
INSERT INTO commutes (user_id, clock_in, clock_out, work_hours, deleted_yn)
VALUES
(1, '2024-10-23 09:00:00', '2024-10-23 18:00:00', 8, 'N'),
(2, '2024-10-23 08:50:00', '2024-10-23 17:50:00', 8, 'N'),
(3, '2024-10-23 09:20:00', '2024-10-23 18:20:00', 8, 'N'),
(4, '2024-10-23 08:55:00', '2024-10-23 17:55:00', 8, 'N'),
(5, '2024-10-23 09:05:00', '2024-10-23 18:05:00', 8, 'N');
-- leave_histories 테이블에 데이터 삽입
INSERT INTO leave_histories (branch_id, user_id, leave_category_id, application_date, approve_date, applicant_description, admin_description, status, deleted_yn)
VALUES
(1, 2, 1, '2024-11-01', '2024-10-25', '개인 휴가', '승인합니다', '승인', 'N'),
(2, 3, 3, '2024-12-01', '2024-11-20', '연차 사용', '승인합니다', '승인', 'N'),
(3, 4, 5, '2024-12-15', '2024-12-10', '연말 휴가', '승인합니다', '승인', 'N'),
(3, 5, 6, '2025-01-10', NULL, '개인 사유', NULL, '확인중', 'N');
-- allowance_policies 테이블에 데이터 삽입
INSERT INTO allowance_policies (branch_id, payment_day, comprehensive_overtime, annual_leave, holiday_work, job_duty, meal, base_salary, doctor_holiday_work_pay, common_holiday_work_pay, deleted_yn)
VALUES
(1, 25, TRUE, TRUE, TRUE, TRUE, TRUE, 1, 200000, 100000, 'N'),
(2, 25, TRUE, TRUE, TRUE, FALSE, TRUE, 1, 180000, 90000, 'N'),
(3, 25, TRUE, TRUE, TRUE, TRUE, TRUE, 0, 190000, 95000, 'N');
-- user_parts 테이블에 데이터 삽입
INSERT INTO user_parts (user_id, part_id)
VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 5),
(5, 6);
-- user_salaries 테이블에 데이터 삽입
INSERT INTO user_salaries (user_id, branch_id, part_id, monthly_salary, annual_salary, hourly_wage, deleted_yn)
VALUES
(1, 1, 1, 6000000, 72000000, 36000, 'N'),
(2, 1, 2, 3500000, 42000000, 21000, 'N'),
(3, 2, 3, 5800000, 69600000, 34800, 'N'),
(4, 3, 5, 5500000, 66000000, 33000, 'N'),
(5, 3, 6, 3800000, 45600000, 22800, 'N');
-- tax_brackets 테이블에 데이터 삽입
INSERT INTO tax_brackets (salary_bracket_id, lower_limit, upper_limit, tax_rate, deduction, deleted_yn)
VALUES
(1, 0, 1000000, 0.06, 0, 'N'),
(2, 1000001, 4000000, 0.15, 90000, 'N'),
(3, 4000001, 8000000, 0.24, 450000, 'N'),
(4, 8000001, 12000000, 0.35, 1290000, 'N'),
(5, 12000001, 999999999, 0.40, 1940000, 'N');
-- rest_days 테이블에 데이터 삽입
INSERT INTO rest_days (branch_id, date, rest_type, description, is_paid, is_holiday_work_allowed, deleted_yn)
VALUES
(1, '2024-12-25', '공휴일', '크리스마스', 1, 0, 'N'),
(2, '2025-01-01', '공휴일', '신년', 1, 0, 'N'),
(3, '2025-05-05', '공휴일', '어린이날', 1, 0, 'N'),
(1, '2024-12-31', '주말', '연말', 1, 1, 'N');
-- overtime_policies 테이블에 데이터 삽입
INSERT INTO overtime_policies (branch_id, doctor_ot_30, doctor_ot_60, doctor_ot_90, doctor_ot_120, common_ot_30, common_ot_60, common_ot_90, common_ot_120, deleted_yn)
VALUES
(1, 30000, 60000, 90000, 120000, 15000, 30000, 45000, 60000, 'N'),
(2, 28000, 56000, 84000, 112000, 14000, 28000, 42000, 56000, 'N'),
(3, 29000, 58000, 87000, 116000, 14500, 29000, 43500, 58000, 'N');
-- holiday_work_policies 테이블에 데이터 삽입
INSERT INTO holiday_work_policies (branch_id, do_holiday_work, deleted_yn)
VALUES
(1, 1, 'N'),
(2, 1, 'N'),
(3, 1, 'N');
-- document_policies 테이블에 데이터 삽입
INSERT INTO document_policies (branch_id, document_type, can_view, can_edit, can_delete, deleted_yn)
VALUES
(1, '휴가신청서', 1, 1, 0, 'N'),
(2, '휴가신청서', 1, 1, 0, 'N'),
(3, '휴가신청서', 1, 1, 0, 'N');
-- commute_policies 테이블에 데이터 삽입
INSERT INTO commute_policies (branch_id, do_commute, allowed_ip_commute, deleted_yn)
VALUES
(1, 1, '192.168.1.1,192.168.1.2', 'N'),
(2, 1, '192.168.2.1,192.168.2.2', 'N'),
(3, 1, '192.168.3.1,192.168.3.2', 'N');
-- auto_overtime_policies 테이블에 데이터 삽입
INSERT INTO auto_overtime_policies (branch_id, top_auto_applied, total_auto_applied, part_auto_applied, deleted_yn)
VALUES
(1, 1, 1, 1, 'N'),
(2, 1, 1, 0, 'N'),
(3, 0, 1, 1, 'N');
-- auto_annual_leave_approval 테이블에 데이터 삽입
INSERT INTO auto_annual_leave_approval (branch_id, top_auto_approval, total_auto_approval, part_auto_approval, deleted_yn)
VALUES
(1, TRUE, TRUE, FALSE, 'N'),
(2, FALSE, TRUE, FALSE, 'N'),
(3, TRUE, FALSE, TRUE, 'N');
-- salary_templates 테이블에 데이터 삽입
INSERT INTO salary_templates (
  branch_id, part_id, name, is_january_entry, weekly_work_days,
  month_salary, included_holiday_allowance, included_job_allowance, hour_wage,
  basic_salary, contractual_working_hours, weekly_rest_hours, annual_salary,
  comprehensive_overtime_allowance, comprehensive_overtime_hour,
  annual_leave_allowance, annual_leave_allowance_hour, annual_leave_allowance_day, hire_year
) VALUES
(1, 1, '의사 급여 템플릿', 1, 5, 6000000, 1, 1, 36000, 5000000, 40, 15, 72000000, 500000, 20, 300000, 8, 15, 2024),
(1, 2, '간호사 급여 템플릿', 0, 5, 3500000, 1, 0, 21000, 3000000, 40, 15, 42000000, 300000, 15, 200000, 8, 15, 2024),
(2, 3, '의사 급여 템플릿', 1, 5, 5800000, 1, 1, 34800, 4800000, 40, 15, 69600000, 480000, 20, 290000, 8, 15, 2024),
(2, 4, '피부관리사 급여 템플릿', 0, 5, 3000000, 1, 0, 18000, 2500000, 40, 15, 36000000, 250000, 15, 150000, 8, 15, 2024),
(3, 5, '의사 급여 템플릿', 1, 5, 5500000, 1, 1, 33000, 4500000, 40, 15, 66000000, 460000, 20, 275000, 8, 15, 2024),
(3, 6, '레이저 전문가 급여 템플릿', 0, 5, 3800000, 1, 1, 22800, 3200000, 40, 15, 45600000, 320000, 15, 190000, 8, 15, 2024);
-- leave_excluded_parts 테이블에 데이터 삽입
INSERT INTO leave_excluded_parts (leave_category_id, part_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4),
(5, 5),
(6, 6);
-- user_menus 테이블에 데이터 삽입
INSERT INTO user_menus (user_id, part_id, menu_name, is_permitted)
VALUES
(1, 1, 'P.T관리', TRUE),
(1, 1, '계약관리(P.T)포함', TRUE),
(2, 2, '휴무관리', TRUE),
(2, 2, 'O.T관리', TRUE),
(3, 3, '인사관리', TRUE),
(3, 3, '근로관리', TRUE),
(4, 5, '급여정산', TRUE),
(4, 5, '문서설정관리', TRUE),
(5, 6, '휴직관리', TRUE),
(5, 6, '출퇴근기록관리', TRUE);
-- overtimes 테이블에 데이터 삽입
INSERT INTO overtimes (applicant_id, manager_id, overtime_hours, status, application_date, application_memo, manager_memo, processed_date, is_approved, deleted_yn)
VALUES
(2, 1, '60', 'approved', '2024-10-24', '프로젝트 마감으로 인한 연장 근무', '승인합니다', '2024-10-25', 'Y', 'N'),
(3, 1, '30', 'pending', '2024-10-25', '고객 미팅 준비', NULL, NULL, 'N', 'N'),
(4, 3, '90', 'rejected', '2024-10-23', '재고 정리', '현재 불필요합니다', '2024-10-24', 'N', 'N'),
(5, 4, '120', 'approved', '2024-10-26', '연말 결산 작업', '승인합니다', '2024-10-27', 'Y', 'N');
-- salary_brackets 테이블에 데이터 삽입
INSERT INTO salary_brackets (year, minimum_hourly_rate, minimum_monthly_rate, national_pension, health_insurance, employment_insurance, long_term_care_insurance, minimum_pension_income, maximum_pension_income, maximum_national_pension, minimum_health_insurance, maximum_health_insurance, local_income_tax_rate, deleted_yn)
VALUES
(2024, 9620, 2010580, 4.5, 3.545, 0.9, 12.81, 350000, 5530000, 248850, 71160, 7106100, 10, 'N'),
(2025, 10000, 2090000, 4.5, 3.6, 0.9, 13, 360000, 5700000, 256500, 73440, 7320000, 10, 'N');
-- minimum_wage_policies 테이블에 데이터 삽입
INSERT INTO minimum_wage_policies (minimum_wage, person_in_charge, created_at, updated_at, deleted_yn)
VALUES
(9620, '김인사', '2024-10-25 14:30:00', '2024-10-25 14:30:00', 'N');
-- 외래 키 체크 및 안전 모드 다시 활성화
SET FOREIGN_KEY_CHECKS = 1;
SET SQL_SAFE_UPDATES = 1;