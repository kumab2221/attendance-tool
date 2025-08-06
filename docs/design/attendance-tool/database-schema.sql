-- 勤怠管理自動集計ツール データベーススキーマ
-- 将来的なデータベース化を考慮した設計（現在はCSVファイルベース）

-- データベース作成
-- CREATE DATABASE attendance_tool_db;
-- USE attendance_tool_db;

-- ===== マスターテーブル =====

-- 部門マスター
CREATE TABLE departments (
    id VARCHAR(36) PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    parent_department_id VARCHAR(36),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (parent_department_id) REFERENCES departments(id),
    INDEX idx_departments_code (code),
    INDEX idx_departments_parent (parent_department_id),
    INDEX idx_departments_active (is_active)
);

-- 社員マスター
CREATE TABLE employees (
    id VARCHAR(36) PRIMARY KEY,
    employee_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    department_id VARCHAR(36) NOT NULL,
    hire_date DATE NOT NULL,
    termination_date DATE NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (department_id) REFERENCES departments(id),
    INDEX idx_employees_number (employee_number),
    INDEX idx_employees_dept (department_id),
    INDEX idx_employees_active (is_active),
    INDEX idx_employees_hire_date (hire_date)
);

-- 就業規則マスター
CREATE TABLE work_rules (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    standard_working_hours INT NOT NULL DEFAULT 480,     -- 標準労働時間（分）
    standard_working_days INT NOT NULL DEFAULT 20,      -- 月間標準労働日数
    late_threshold_minutes INT NOT NULL DEFAULT 15,     -- 遅刻判定閾値（分）
    early_leave_threshold_minutes INT NOT NULL DEFAULT 15, -- 早退判定閾値（分）
    overtime_threshold_hours INT NOT NULL DEFAULT 45,   -- 残業時間上限（時間/月）
    max_daily_working_hours INT NOT NULL DEFAULT 12,    -- 1日最大労働時間（時間）
    break_time_minutes INT NOT NULL DEFAULT 60,         -- 休憩時間（分）
    paid_leave_allowance INT NOT NULL DEFAULT 20,       -- 年間有給付与日数
    effective_from DATE NOT NULL,
    effective_to DATE NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_work_rules_effective (effective_from, effective_to),
    INDEX idx_work_rules_active (is_active)
);

-- ===== 勤怠データテーブル =====

-- 勤怠記録
CREATE TABLE attendance_records (
    id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL,
    attendance_date DATE NOT NULL,
    clock_in TIME NULL,
    clock_out TIME NULL,
    break_start TIME NULL,
    break_end TIME NULL,
    attendance_type ENUM('present', 'absent', 'late', 'early_leave', 'paid_leave', 'special_leave', 'sick_leave', 'holiday', 'weekend') NOT NULL DEFAULT 'present',
    notes TEXT NULL,
    is_manual_entry BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    UNIQUE KEY uk_attendance_employee_date (employee_id, attendance_date),
    INDEX idx_attendance_date (attendance_date),
    INDEX idx_attendance_type (attendance_type),
    INDEX idx_attendance_employee_date (employee_id, attendance_date)
);

-- 勤怠記録詳細（将来拡張用）
CREATE TABLE attendance_record_details (
    id VARCHAR(36) PRIMARY KEY,
    attendance_record_id VARCHAR(36) NOT NULL,
    detail_type ENUM('overtime', 'night_shift', 'holiday_work', 'special_allowance') NOT NULL,
    start_time TIME NULL,
    end_time TIME NULL,
    duration_minutes INT NULL,
    rate DECIMAL(3,2) NULL,  -- 割増率（1.25など）
    notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (attendance_record_id) REFERENCES attendance_records(id) ON DELETE CASCADE,
    INDEX idx_attendance_details_record (attendance_record_id),
    INDEX idx_attendance_details_type (detail_type)
);

-- ===== 集計結果テーブル =====

-- 月次勤怠集計
CREATE TABLE monthly_attendance_summary (
    id VARCHAR(36) PRIMARY KEY,
    employee_id VARCHAR(36) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    working_days INT NOT NULL DEFAULT 0,
    present_days INT NOT NULL DEFAULT 0,
    absent_days INT NOT NULL DEFAULT 0,
    late_count INT NOT NULL DEFAULT 0,
    early_leave_count INT NOT NULL DEFAULT 0,
    total_working_hours DECIMAL(6,2) NOT NULL DEFAULT 0.00,  -- 総労働時間
    overtime_hours DECIMAL(6,2) NOT NULL DEFAULT 0.00,       -- 残業時間
    night_shift_hours DECIMAL(6,2) NOT NULL DEFAULT 0.00,    -- 深夜労働時間
    holiday_work_hours DECIMAL(6,2) NOT NULL DEFAULT 0.00,   -- 休日労働時間
    paid_leave_used INT NOT NULL DEFAULT 0,
    special_leave_used INT NOT NULL DEFAULT 0,
    sick_leave_used INT NOT NULL DEFAULT 0,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    UNIQUE KEY uk_summary_employee_period (employee_id, year, month),
    INDEX idx_summary_period (year, month),
    INDEX idx_summary_calculated (calculated_at)
);

-- 部門別月次集計
CREATE TABLE monthly_department_summary (
    id VARCHAR(36) PRIMARY KEY,
    department_id VARCHAR(36) NOT NULL,
    year INT NOT NULL,
    month INT NOT NULL,
    employee_count INT NOT NULL DEFAULT 0,
    total_working_days INT NOT NULL DEFAULT 0,
    average_attendance_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    total_overtime_hours DECIMAL(8,2) NOT NULL DEFAULT 0.00,
    total_paid_leave_used INT NOT NULL DEFAULT 0,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (department_id) REFERENCES departments(id),
    UNIQUE KEY uk_dept_summary_period (department_id, year, month),
    INDEX idx_dept_summary_period (year, month)
);

-- ===== ファイル管理テーブル =====

-- アップロードファイル管理
CREATE TABLE uploaded_files (
    id VARCHAR(36) PRIMARY KEY,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type ENUM('csv', 'excel') NOT NULL,
    record_count INT NULL,
    upload_status ENUM('uploaded', 'processing', 'completed', 'failed') DEFAULT 'uploaded',
    processed_at TIMESTAMP NULL,
    error_message TEXT NULL,
    uploaded_by VARCHAR(36) NULL,  -- 将来のユーザー管理用
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_files_status (upload_status),
    INDEX idx_files_created (created_at),
    INDEX idx_files_type (file_type)
);

-- ファイル処理ログ
CREATE TABLE file_processing_logs (
    id VARCHAR(36) PRIMARY KEY,
    file_id VARCHAR(36) NOT NULL,
    processing_step ENUM('validation', 'import', 'calculation', 'export') NOT NULL,
    status ENUM('started', 'completed', 'failed') NOT NULL,
    message TEXT NULL,
    processing_time_ms INT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (file_id) REFERENCES uploaded_files(id) ON DELETE CASCADE,
    INDEX idx_processing_logs_file (file_id),
    INDEX idx_processing_logs_step (processing_step),
    INDEX idx_processing_logs_status (status)
);

-- ===== バリデーション・エラー管理 =====

-- データ検証結果
CREATE TABLE validation_results (
    id VARCHAR(36) PRIMARY KEY,
    file_id VARCHAR(36) NOT NULL,
    record_index INT NULL,  -- エラーが発生した行番号
    field_name VARCHAR(100) NULL,
    error_code VARCHAR(50) NOT NULL,
    error_message TEXT NOT NULL,
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    is_resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (file_id) REFERENCES uploaded_files(id) ON DELETE CASCADE,
    INDEX idx_validation_file (file_id),
    INDEX idx_validation_severity (severity),
    INDEX idx_validation_resolved (is_resolved)
);

-- ===== 設定・ログテーブル =====

-- システム設定
CREATE TABLE system_settings (
    id VARCHAR(36) PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT NULL,
    is_encrypted BOOLEAN DEFAULT FALSE,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_settings_key (setting_key)
);

-- 処理ログ
CREATE TABLE processing_logs (
    id VARCHAR(36) PRIMARY KEY,
    job_type ENUM('import', 'calculation', 'export', 'cleanup') NOT NULL,
    status ENUM('started', 'running', 'completed', 'failed') NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL,
    duration_ms INT NULL,
    records_processed INT NULL,
    error_count INT NULL,
    warning_count INT NULL,
    log_message TEXT NULL,
    
    INDEX idx_processing_logs_type (job_type),
    INDEX idx_processing_logs_status (status),
    INDEX idx_processing_logs_start (start_time)
);

-- ===== ビュー定義 =====

-- 社員情報ビュー（アクティブな社員のみ）
CREATE VIEW active_employees AS
SELECT 
    e.id,
    e.employee_number,
    e.name,
    e.hire_date,
    d.name as department_name,
    d.code as department_code
FROM employees e
JOIN departments d ON e.department_id = d.id
WHERE e.is_active = TRUE AND d.is_active = TRUE;

-- 月次勤怠サマリービュー
CREATE VIEW monthly_attendance_view AS
SELECT 
    mas.id,
    e.employee_number,
    e.name as employee_name,
    d.name as department_name,
    mas.year,
    mas.month,
    mas.working_days,
    mas.present_days,
    mas.absent_days,
    mas.late_count,
    mas.early_leave_count,
    mas.total_working_hours,
    mas.overtime_hours,
    mas.paid_leave_used,
    ROUND((mas.present_days / mas.working_days * 100), 2) as attendance_rate,
    mas.calculated_at
FROM monthly_attendance_summary mas
JOIN employees e ON mas.employee_id = e.id
JOIN departments d ON e.department_id = d.id;

-- ===== インデックス最適化 =====

-- 複合インデックス（頻繁に使用されるクエリパターン用）
CREATE INDEX idx_attendance_employee_year_month ON attendance_records(employee_id, YEAR(attendance_date), MONTH(attendance_date));
CREATE INDEX idx_summary_dept_period ON monthly_attendance_summary(employee_id, year, month);

-- フルテキスト検索用インデックス
CREATE FULLTEXT INDEX ft_employees_name ON employees(name);
CREATE FULLTEXT INDEX ft_departments_name ON departments(name);

-- ===== ストアドプロシージャ（サンプル） =====

DELIMITER //

-- 月次集計計算プロシージャ
CREATE PROCEDURE CalculateMonthlyAttendance(
    IN p_employee_id VARCHAR(36),
    IN p_year INT,
    IN p_month INT
)
BEGIN
    DECLARE v_working_days INT DEFAULT 0;
    DECLARE v_present_days INT DEFAULT 0;
    DECLARE v_absent_days INT DEFAULT 0;
    DECLARE v_late_count INT DEFAULT 0;
    DECLARE v_early_leave_count INT DEFAULT 0;
    DECLARE v_overtime_hours DECIMAL(6,2) DEFAULT 0.00;
    DECLARE v_paid_leave_used INT DEFAULT 0;
    
    -- 勤務日数計算
    SELECT COUNT(*) INTO v_working_days
    FROM attendance_records
    WHERE employee_id = p_employee_id
      AND YEAR(attendance_date) = p_year
      AND MONTH(attendance_date) = p_month
      AND attendance_type NOT IN ('holiday', 'weekend');
    
    -- 出勤日数計算
    SELECT COUNT(*) INTO v_present_days
    FROM attendance_records
    WHERE employee_id = p_employee_id
      AND YEAR(attendance_date) = p_year
      AND MONTH(attendance_date) = p_month
      AND attendance_type IN ('present', 'late', 'early_leave');
    
    -- 欠勤日数計算
    SELECT COUNT(*) INTO v_absent_days
    FROM attendance_records
    WHERE employee_id = p_employee_id
      AND YEAR(attendance_date) = p_year
      AND MONTH(attendance_date) = p_month
      AND attendance_type = 'absent';
    
    -- 遅刻回数計算
    SELECT COUNT(*) INTO v_late_count
    FROM attendance_records
    WHERE employee_id = p_employee_id
      AND YEAR(attendance_date) = p_year
      AND MONTH(attendance_date) = p_month
      AND attendance_type = 'late';
    
    -- 有給取得日数計算
    SELECT COUNT(*) INTO v_paid_leave_used
    FROM attendance_records
    WHERE employee_id = p_employee_id
      AND YEAR(attendance_date) = p_year
      AND MONTH(attendance_date) = p_month
      AND attendance_type = 'paid_leave';
    
    -- 結果をサマリーテーブルに挿入または更新
    INSERT INTO monthly_attendance_summary (
        id, employee_id, year, month, working_days, present_days, absent_days,
        late_count, early_leave_count, overtime_hours, paid_leave_used
    ) VALUES (
        UUID(), p_employee_id, p_year, p_month, v_working_days, v_present_days,
        v_absent_days, v_late_count, v_early_leave_count, v_overtime_hours, v_paid_leave_used
    )
    ON DUPLICATE KEY UPDATE
        working_days = v_working_days,
        present_days = v_present_days,
        absent_days = v_absent_days,
        late_count = v_late_count,
        early_leave_count = v_early_leave_count,
        overtime_hours = v_overtime_hours,
        paid_leave_used = v_paid_leave_used,
        calculated_at = CURRENT_TIMESTAMP;
        
END //

DELIMITER ;

-- ===== 初期データ投入 =====

-- システム設定の初期データ
INSERT INTO system_settings (id, setting_key, setting_value, description) VALUES
(UUID(), 'app.version', '1.0.0', 'アプリケーションバージョン'),
(UUID(), 'csv.encoding', 'utf-8', 'CSVファイルエンコーディング'),
(UUID(), 'csv.delimiter', ',', 'CSV区切り文字'),
(UUID(), 'export.formats', 'csv,excel', 'サポートする出力形式'),
(UUID(), 'log.level', 'INFO', 'ログレベル'),
(UUID(), 'processing.max_records', '10000', '最大処理レコード数');

-- デフォルト就業規則
INSERT INTO work_rules (
    id, name, standard_working_hours, standard_working_days,
    late_threshold_minutes, early_leave_threshold_minutes,
    overtime_threshold_hours, max_daily_working_hours,
    break_time_minutes, paid_leave_allowance, effective_from
) VALUES (
    UUID(), 'デフォルト就業規則', 480, 20, 15, 15, 45, 12, 60, 20, '2024-01-01'
);