# API エンドポイント仕様

## 概要

勤怠管理自動集計ツールは現在CLI/バッチツールとして設計されていますが、将来的なWebアプリケーション化を考慮したRESTful API設計案を記載します。

## 基本情報

- **Base URL**: `https://api.attendance-tool.local/v1`
- **認証方式**: JWT Bearer Token
- **Content-Type**: `application/json`
- **文字エンコーディング**: UTF-8

## 共通レスポンス形式

### 成功レスポンス
```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "requestId": "req-12345",
    "timestamp": "2024-01-15T10:30:00Z",
    "processingTimeMs": 250
  }
}
```

### エラーレスポンス
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力データに不正があります",
    "details": { ... }
  },
  "metadata": {
    "requestId": "req-12345",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## 認証エンドポイント

### POST /auth/login
ユーザー認証とトークン取得

**リクエスト:**
```json
{
  "username": "user@company.com",
  "password": "password123"
}
```

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "refresh_token_here",
    "expiresIn": 3600,
    "user": {
      "id": "user-001",
      "name": "田中太郎",
      "role": "hr_manager"
    }
  }
}
```

### POST /auth/refresh
トークン更新

**リクエスト:**
```json
{
  "refreshToken": "refresh_token_here"
}
```

## ファイル管理エンドポイント

### POST /files/upload
CSVファイルのアップロード

**リクエスト:**
- Content-Type: `multipart/form-data`
- Files: `files[]` (複数ファイル対応)

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "uploadedFiles": [
      {
        "id": "file-001",
        "filename": "attendance_202401.csv",
        "size": 1024000,
        "records": 2500,
        "uploadedAt": "2024-01-15T10:30:00Z"
      }
    ],
    "validationResults": [
      {
        "fileId": "file-001",
        "isValid": true,
        "errors": [],
        "warnings": [
          {
            "code": "MISSING_DATA",
            "message": "1月5日のデータが不足しています",
            "recordIndex": 125
          }
        ]
      }
    ]
  }
}
```

### GET /files
アップロード済みファイル一覧取得

**クエリパラメータ:**
- `page` (optional): ページ番号 (default: 1)
- `limit` (optional): 1ページあたりの件数 (default: 20)
- `status` (optional): ファイルステータス (`uploaded`, `processing`, `completed`)

**レスポンス:**
```json
{
  "success": true,
  "data": [
    {
      "id": "file-001",
      "filename": "attendance_202401.csv",
      "size": 1024000,
      "records": 2500,
      "status": "completed",
      "uploadedAt": "2024-01-15T10:30:00Z",
      "processedAt": "2024-01-15T10:35:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 50,
    "hasNext": true,
    "hasPrevious": false
  }
}
```

## 処理実行エンドポイント

### POST /processing/execute
集計処理の実行

**リクエスト:**
```json
{
  "fileIds": ["file-001", "file-002"],
  "period": {
    "type": "monthly",
    "year": 2024,
    "month": 1
  },
  "outputFormats": ["csv", "excel"],
  "options": {
    "includeDepartmentSummary": true,
    "includeDetails": true,
    "applyWorkRules": true
  }
}
```

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "jobId": "job-12345",
    "status": "queued",
    "estimatedCompletionTime": "2024-01-15T10:40:00Z"
  }
}
```

### GET /processing/jobs/{jobId}
処理ジョブのステータス取得

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "jobId": "job-12345",
    "status": "processing",
    "progress": {
      "currentStep": "calculation",
      "totalSteps": 6,
      "currentStepProgress": 45,
      "overallProgress": 60,
      "estimatedRemainingMs": 120000,
      "message": "社員別集計処理中..."
    },
    "startedAt": "2024-01-15T10:30:00Z",
    "estimatedCompletionTime": "2024-01-15T10:40:00Z"
  }
}
```

### GET /processing/jobs/{jobId}/results
処理結果の取得

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "jobId": "job-12345",
    "status": "completed",
    "results": {
      "summary": {
        "totalEmployees": 100,
        "processedRecords": 2500,
        "errorCount": 0,
        "warningCount": 3,
        "processingTimeMs": 45000
      },
      "outputFiles": [
        {
          "format": "excel",
          "url": "/files/download/report-12345.xlsx",
          "size": 256000
        },
        {
          "format": "csv",
          "url": "/files/download/summary-12345.csv",
          "size": 128000
        }
      ]
    },
    "completedAt": "2024-01-15T10:35:00Z"
  }
}
```

## 集計データエンドポイント

### GET /attendance/summary
勤怠集計データの取得

**クエリパラメータ:**
- `period.type`: `monthly` | `date_range` | `yearly`
- `period.year`: 年
- `period.month`: 月 (monthly の場合)
- `period.startDate`: 開始日 (date_range の場合)
- `period.endDate`: 終了日 (date_range の場合)
- `employeeIds` (optional): 社員ID (カンマ区切り)
- `departmentIds` (optional): 部門ID (カンマ区切り)

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "period": {
      "type": "monthly",
      "year": 2024,
      "month": 1,
      "startDate": "2024-01-01",
      "endDate": "2024-01-31"
    },
    "employeeSummaries": [
      {
        "employeeId": "emp-001",
        "employeeName": "田中太郎",
        "department": "営業部",
        "workingDays": 20,
        "presentDays": 19,
        "absentDays": 1,
        "lateCount": 2,
        "earlyLeaveCount": 0,
        "totalWorkingHours": 152.5,
        "overtimeHours": 15.5,
        "paidLeaveUsed": 1,
        "specialLeaveUsed": 0
      }
    ],
    "departmentSummaries": [
      {
        "departmentId": "dept-001",
        "departmentName": "営業部",
        "employeeCount": 25,
        "averageAttendanceRate": 95.2,
        "totalOvertimeHours": 380,
        "totalPaidLeaveUsed": 15
      }
    ]
  }
}
```

### GET /attendance/statistics
勤怠統計データの取得

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "period": {
      "type": "monthly",
      "year": 2024,
      "month": 1
    },
    "statistics": {
      "totalEmployees": 100,
      "averageAttendanceRate": 96.8,
      "topDepartmentByAttendance": "技術部",
      "totalOvertimeHours": 1250,
      "averageOvertimePerEmployee": 12.5,
      "paidLeaveUtilizationRate": 65.2,
      "lateArrivalRate": 8.3,
      "earlyDepartureRate": 2.1
    },
    "trends": [
      {
        "period": { "year": 2024, "month": 1 },
        "attendanceRate": 96.8,
        "overtimeHours": 1250,
        "leaveUsage": 85
      }
    ]
  }
}
```

## 設定管理エンドポイント

### GET /config/work-rules
就業規則設定の取得

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "standardWorkingHours": 480,
    "standardWorkingDays": 20,
    "lateThresholdMinutes": 15,
    "earlyLeaveThresholdMinutes": 15,
    "overtimeThresholdHours": 45,
    "maxDailyWorkingHours": 12,
    "breakTimeMinutes": 60,
    "paidLeaveAllowance": 20
  }
}
```

### PUT /config/work-rules
就業規則設定の更新

**リクエスト:**
```json
{
  "standardWorkingHours": 480,
  "lateThresholdMinutes": 10,
  "overtimeThresholdHours": 40
}
```

### GET /config/csv-format
CSV形式設定の取得

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "encoding": "utf-8",
    "delimiter": ",",
    "hasHeader": true,
    "columnMapping": {
      "employeeId": "社員ID",
      "employeeName": "氏名",
      "date": "日付",
      "clockIn": "出勤時刻",
      "clockOut": "退勤時刻",
      "attendanceType": "勤怠区分"
    },
    "dateFormat": "YYYY-MM-DD",
    "timeFormat": "HH:MM"
  }
}
```

## ダウンロードエンドポイント

### GET /files/download/{fileId}
処理結果ファイルのダウンロード

**レスポンス:**
- Content-Type: `application/octet-stream`
- Content-Disposition: `attachment; filename="report.xlsx"`
- ファイルのバイナリデータ

## エラーコード一覧

| コード | メッセージ | HTTPステータス |
|--------|------------|----------------|
| AUTHENTICATION_FAILED | 認証に失敗しました | 401 |
| AUTHORIZATION_FAILED | 権限がありません | 403 |
| FILE_NOT_FOUND | ファイルが見つかりません | 404 |
| INVALID_FORMAT | ファイル形式が不正です | 400 |
| VALIDATION_ERROR | 入力データに不正があります | 400 |
| PROCESSING_ERROR | 処理中にエラーが発生しました | 500 |
| SYSTEM_ERROR | システムエラーが発生しました | 500 |

## レート制限

- **一般API**: 100リクエスト/分
- **ファイルアップロード**: 10リクエスト/分
- **処理実行**: 5リクエスト/分

制限超過時は`429 Too Many Requests`を返却します。

## Webhookサポート（将来拡張）

処理完了時にWebhookでコールバック通知を送信する機能。

### POST {webhook_url}
処理完了通知

**送信データ:**
```json
{
  "jobId": "job-12345",
  "status": "completed",
  "results": {
    "outputFiles": [
      {
        "format": "excel",
        "downloadUrl": "https://api.attendance-tool.local/v1/files/download/report-12345.xlsx"
      }
    ]
  },
  "completedAt": "2024-01-15T10:35:00Z"
}
```