@echo off
:: Windows Makefile Wrapper
setlocal

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="complexity" goto complexity
if "%1"=="complexity-report" goto complexity-report
if "%1"=="complexity-ci" goto complexity-ci
if "%1"=="test" goto test
if "%1"=="unit-test" goto unit-test
if "%1"=="clean" goto clean
goto invalid

:help
echo Windows Makefile Wrapper
echo.
echo Available targets:
echo   help               Show this help
echo   complexity         Run complexity check
echo   complexity-report  Generate HTML complexity report  
echo   complexity-ci      Run complexity check for CI
echo   test               Run unit tests
echo   unit-test          Run unit tests
echo   clean              Clean temporary files
goto end

:complexity
echo Running complexity check...
python scripts/complexity_check.py --threshold 10 --verbose
goto end

:complexity-report
echo Generating complexity report...
python scripts/complexity_check.py --threshold 10 --format html --output reports/complexity/complexity_report.html
echo HTML report generated: reports/complexity/complexity_report.html
goto end

:complexity-ci
echo Running CI complexity check...
python scripts/complexity_check.py --threshold 10 --ci
goto end

:test
echo Running unit tests...
python -m pytest tests/unit/ -v --cov=attendance_tool --cov-report=term-missing
goto end

:unit-test
echo Running unit tests...
python -m pytest tests/unit/ -v --cov=attendance_tool --cov-report=term-missing
goto end

:clean
echo Cleaning temporary files...
for /r . %%i in (*.pyc) do del "%%i" 2>nul
for /r . %%i in (__pycache__) do rmdir /s /q "%%i" 2>nul
rmdir /s /q .pytest_cache 2>nul
del .coverage 2>nul
rmdir /s /q htmlcov 2>nul
rmdir /s /q reports 2>nul
goto end

:invalid
echo Invalid target: %1
echo Use 'make.cmd help' to see available targets
exit /b 1

:end