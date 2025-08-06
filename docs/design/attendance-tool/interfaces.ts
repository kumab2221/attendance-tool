// 勤怠管理自動集計ツール - TypeScript型定義
// Python実装での型安全性確保のためのインターフェース定義

// ===== 基本エンティティ =====

export interface Employee {
  id: string;
  name: string;
  department: string;
  employeeNumber: string;
  hireDate: Date;
  isActive: boolean;
}

export interface AttendanceRecord {
  id: string;
  employeeId: string;
  date: Date;
  clockIn?: Date;
  clockOut?: Date;
  breakStart?: Date;
  breakEnd?: Date;
  attendanceType: AttendanceType;
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  parentDepartmentId?: string;
}

// ===== 列挙型 =====

export enum AttendanceType {
  PRESENT = 'present',              // 出勤
  ABSENT = 'absent',               // 欠勤
  LATE = 'late',                   // 遅刻
  EARLY_LEAVE = 'early_leave',     // 早退
  PAID_LEAVE = 'paid_leave',       // 有給休暇
  SPECIAL_LEAVE = 'special_leave', // 特別休暇
  SICK_LEAVE = 'sick_leave',       // 病気休暇
  HOLIDAY = 'holiday',             // 祝日
  WEEKEND = 'weekend'              // 週末
}

export enum ReportFormat {
  CSV = 'csv',
  EXCEL = 'excel'
}

export enum PeriodType {
  MONTHLY = 'monthly',
  DATE_RANGE = 'date_range',
  YEARLY = 'yearly'
}

// ===== 集計関連 =====

export interface AttendanceSummary {
  employeeId: string;
  employeeName: string;
  department: string;
  period: Period;
  workingDays: number;
  presentDays: number;
  absentDays: number;
  lateCount: number;
  earlyLeaveCount: number;
  totalWorkingHours: number;
  overtimeHours: number;
  paidLeaveUsed: number;
  specialLeaveUsed: number;
  calculatedAt: Date;
}

export interface DepartmentSummary {
  departmentId: string;
  departmentName: string;
  period: Period;
  employeeCount: number;
  totalWorkingDays: number;
  averageAttendanceRate: number;
  totalOvertimeHours: number;
  totalPaidLeaveUsed: number;
  employeeSummaries: AttendanceSummary[];
}

export interface Period {
  type: PeriodType;
  startDate: Date;
  endDate: Date;
  year?: number;
  month?: number;
}

// ===== 設定・ルール関連 =====

export interface WorkRules {
  standardWorkingHours: number;      // 標準労働時間（分）
  standardWorkingDays: number;       // 月間標準労働日数
  lateThresholdMinutes: number;      // 遅刻判定閾値（分）
  earlyLeaveThresholdMinutes: number; // 早退判定閾値（分）
  overtimeThresholdHours: number;    // 残業時間上限（時間）
  maxDailyWorkingHours: number;      // 1日最大労働時間（時間）
  breakTimeMinutes: number;          // 休憩時間（分）
  paidLeaveAllowance: number;        // 年間有給付与日数
}

export interface CSVFormat {
  encoding: string;                  // ファイルエンコーディング
  delimiter: string;                 // 区切り文字
  hasHeader: boolean;               // ヘッダー行の有無
  columnMapping: ColumnMapping;     // カラムマッピング
  dateFormat: string;               // 日付フォーマット
  timeFormat: string;               // 時刻フォーマット
}

export interface ColumnMapping {
  employeeId: string;               // 社員IDカラム名
  employeeName: string;             // 社員名カラム名
  date: string;                     // 日付カラム名
  clockIn: string;                  // 出勤時刻カラム名
  clockOut: string;                 // 退勤時刻カラム名
  attendanceType: string;           // 勤怠区分カラム名
  department?: string;              // 部門カラム名
}

// ===== コマンドライン・実行関連 =====

export interface ExecutionConfig {
  inputPath: string;                // 入力CSVディレクトリパス
  outputPath: string;               // 出力ディレクトリパス
  period: Period;                   // 集計期間
  reportFormats: ReportFormat[];    // 出力形式
  includeDetails: boolean;          // 詳細情報含む
  departmentSummary: boolean;       // 部門別集計
  configPath?: string;              // 設定ファイルパス
  logLevel: LogLevel;               // ログレベル
  progressDisplay: boolean;         // 進捗表示
}

export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARNING = 'warning',
  ERROR = 'error'
}

// ===== バリデーション関連 =====

export interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

export interface ValidationError {
  code: string;
  message: string;
  field?: string;
  recordIndex?: number;
  severity: ErrorSeverity;
}

export interface ValidationWarning {
  code: string;
  message: string;
  field?: string;
  recordIndex?: number;
  suggestion?: string;
}

export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical'
}

// ===== 出力関連 =====

export interface ReportData {
  summary: AttendanceSummary[];
  departmentSummary?: DepartmentSummary[];
  period: Period;
  generatedAt: Date;
  metadata: ReportMetadata;
}

export interface ReportMetadata {
  totalEmployees: number;
  processedRecords: number;
  errorCount: number;
  warningCount: number;
  processingTimeMs: number;
  version: string;
}

export interface ExcelSheetConfig {
  sheetName: string;
  includeCharts: boolean;
  applyFormatting: boolean;
  freezeHeader: boolean;
  autoFilter: boolean;
}

// ===== エラーハンドリング =====

export interface ProcessingError {
  type: ErrorType;
  message: string;
  details?: any;
  timestamp: Date;
  stackTrace?: string;
}

export enum ErrorType {
  FILE_NOT_FOUND = 'file_not_found',
  FILE_ACCESS_ERROR = 'file_access_error',
  INVALID_FORMAT = 'invalid_format',
  DATA_VALIDATION_ERROR = 'data_validation_error',
  CALCULATION_ERROR = 'calculation_error',
  OUTPUT_ERROR = 'output_error',
  SYSTEM_ERROR = 'system_error'
}

// ===== 統計・分析関連 =====

export interface AttendanceStatistics {
  period: Period;
  totalEmployees: number;
  averageAttendanceRate: number;
  topDepartmentByAttendance: string;
  totalOvertimeHours: number;
  averageOvertimePerEmployee: number;
  paidLeaveUtilizationRate: number;
  lateArrivalRate: number;
  earlyDepartureRate: number;
}

export interface TrendData {
  period: Period;
  attendanceRate: number;
  overtimeHours: number;
  leaveUsage: number;
}

// ===== プログレス・モニタリング =====

export interface ProcessingProgress {
  currentStep: ProcessingStep;
  totalSteps: number;
  currentStepProgress: number;
  overallProgress: number;
  estimatedRemainingMs?: number;
  message: string;
}

export enum ProcessingStep {
  INITIALIZATION = 'initialization',
  FILE_READING = 'file_reading',
  DATA_VALIDATION = 'data_validation',
  CALCULATION = 'calculation',
  REPORT_GENERATION = 'report_generation',
  OUTPUT_WRITING = 'output_writing',
  CLEANUP = 'cleanup'
}

// ===== API仕様（将来拡張用） =====

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: any;
  };
  metadata?: {
    requestId: string;
    timestamp: Date;
    processingTimeMs: number;
  };
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number;
    limit: number;
    total: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
}

// ===== ユーティリティ型 =====

export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

export type OptionalFields<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// ===== カスタム型ガード（Python実装での型チェック用） =====

export interface TypeGuards {
  isValidDate(value: any): value is Date;
  isValidEmployee(value: any): value is Employee;
  isValidAttendanceRecord(value: any): value is AttendanceRecord;
  isValidPeriod(value: any): value is Period;
  isValidWorkRules(value: any): value is WorkRules;
}