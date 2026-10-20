#!/usr/bin/env python3
"""
SANGAM Integration Verification Script

This script verifies all integration points and deployment readiness.
Run this before deployment to ensure everything is working correctly.

Usage:
    python verify_integration.py
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Tuple

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header(text: str):
    """Print a section header."""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")

def print_success(text: str):
    """Print success message."""
    print(f"{GREEN}✓{RESET} {text}")

def print_error(text: str):
    """Print error message."""
    print(f"{RED}✗{RESET} {text}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{YELLOW}⚠{RESET} {text}")

def print_info(text: str):
    """Print info message."""
    print(f"{BLUE}ℹ{RESET} {text}")

def check_file_exists(path: str) -> bool:
    """Check if a file exists."""
    return Path(path).exists()

def check_command_exists(command: str) -> bool:
    """Check if a command exists."""
    try:
        subprocess.run([command, '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def verify_repository_structure() -> Tuple[bool, List[str]]:
    """Verify repository structure."""
    print_header("1. Repository Structure Verification")
    
    checks = []
    all_passed = True
    
    # Check root files
    root_files = [
        'package.json',
        'tsconfig.json',
        'vite.config.js',
        'vercel.json',
        '.gitignore',
        '.gitattributes',
        '.editorconfig',
        'README.md',
    ]
    
    for file in root_files:
        if check_file_exists(file):
            print_success(f"Root file exists: {file}")
            checks.append(True)
        else:
            print_error(f"Missing root file: {file}")
            checks.append(False)
            all_passed = False
    
    # Check backend structure
    backend_files = [
        'apps/api/pyproject.toml',
        'apps/api/src/sangam_api/main.py',
        'apps/api/src/sangam_api/config.py',
        'apps/api/src/sangam_api/core/database.py',
        'apps/api/src/sangam_api/core/auth.py',
        'apps/api/.env.example',
    ]
    
    for file in backend_files:
        if check_file_exists(file):
            print_success(f"Backend file exists: {file}")
            checks.append(True)
        else:
            print_error(f"Missing backend file: {file}")
            checks.append(False)
            all_passed = False
    
    # Check frontend structure
    frontend_files = [
        'src/App.tsx',
        'src/main.tsx',
        'src/lib/api.ts',
        'src/contexts/AuthContext.tsx',
        'public/sw.js',
    ]
    
    for file in frontend_files:
        if check_file_exists(file):
            print_success(f"Frontend file exists: {file}")
            checks.append(True)
        else:
            print_error(f"Missing frontend file: {file}")
            checks.append(False)
            all_passed = False
    
    # Check modules
    modules = [
        'apps/api/src/sangam_api/inventory',
        'apps/api/src/sangam_api/shipments',
        'apps/api/src/sangam_api/routes',
        'apps/api/src/sangam_api/forecasting',
        'apps/api/src/sangam_api/simulation',
        'apps/api/src/sangam_api/iot',
        'apps/api/src/sangam_api/recommendations',
    ]
    
    for module in modules:
        if check_file_exists(module):
            print_success(f"Module exists: {module}")
            checks.append(True)
        else:
            print_error(f"Missing module: {module}")
            checks.append(False)
            all_passed = False
    
    return all_passed, checks

def verify_dependencies() -> Tuple[bool, List[str]]:
    """Verify dependencies."""
    print_header("2. Dependencies Verification")
    
    checks = []
    all_passed = True
    
    # Check Node.js
    if check_command_exists('node'):
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print_success(f"Node.js installed: {version}")
        checks.append(True)
    else:
        print_error("Node.js not installed")
        checks.append(False)
        all_passed = False
    
    # Check npm
    if check_command_exists('npm'):
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print_success(f"npm installed: {version}")
        checks.append(True)
    else:
        print_error("npm not installed")
        checks.append(False)
        all_passed = False
    
    # Check Python
    if check_command_exists('python3') or check_command_exists('python'):
        python_cmd = 'python3' if check_command_exists('python3') else 'python'
        result = subprocess.run([python_cmd, '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print_success(f"Python installed: {version}")
        checks.append(True)
    else:
        print_error("Python not installed")
        checks.append(False)
        all_passed = False
    
    # Check node_modules
    if check_file_exists('node_modules'):
        print_success("node_modules exists")
        checks.append(True)
    else:
        print_warning("node_modules not found (run 'npm install')")
        checks.append(False)
    
    # Check package.json dependencies
    with open('package.json', 'r') as f:
        package_json = json.load(f)
    
    required_deps = ['react', 'react-dom', 'typescript', 'vite']
    for dep in required_deps:
        if dep in package_json.get('dependencies', {}) or dep in package_json.get('devDependencies', {}):
            print_success(f"Dependency present: {dep}")
            checks.append(True)
        else:
            print_error(f"Missing dependency: {dep}")
            checks.append(False)
            all_passed = False
    
    return all_passed, checks

def verify_environment_config() -> Tuple[bool, List[str]]:
    """Verify environment configuration."""
    print_header("3. Environment Configuration Verification")
    
    checks = []
    all_passed = True
    
    # Check .env.example files
    if check_file_exists('.env.example'):
        print_success("Frontend .env.example exists")
        checks.append(True)
    else:
        print_warning("Frontend .env.example not found")
        checks.append(False)
    
    if check_file_exists('apps/api/.env.example'):
        print_success("Backend .env.example exists")
        checks.append(True)
    else:
        print_error("Backend .env.example not found")
        checks.append(False)
        all_passed = False
    
    # Check .gitignore
    with open('.gitignore', 'r') as f:
        gitignore = f.read()
    
    if '.env' in gitignore:
        print_success(".env files are in .gitignore")
        checks.append(True)
    else:
        print_error(".env files not in .gitignore")
        checks.append(False)
        all_passed = False
    
    # Check for committed .env files
    result = subprocess.run(['git', 'ls-files', '*.env'], capture_output=True, text=True)
    if result.stdout.strip():
        print_error(f"Committed .env files found: {result.stdout.strip()}")
        checks.append(False)
        all_passed = False
    else:
        print_success("No .env files committed to Git")
        checks.append(True)
    
    # Check CRLF configuration
    if check_file_exists('.gitattributes'):
        with open('.gitattributes', 'r') as f:
            content = f.read()
        if 'eol=crlf' in content:
            print_success("CRLF configured in .gitattributes")
            checks.append(True)
        else:
            print_warning("CRLF not configured in .gitattributes")
            checks.append(False)
    else:
        print_error(".gitattributes not found")
        checks.append(False)
        all_passed = False
    
    if check_file_exists('.editorconfig'):
        with open('.editorconfig', 'r') as f:
            content = f.read()
        if 'end_of_line = crlf' in content:
            print_success("CRLF configured in .editorconfig")
            checks.append(True)
        else:
            print_warning("CRLF not configured in .editorconfig")
            checks.append(False)
    else:
        print_error(".editorconfig not found")
        checks.append(False)
        all_passed = False
    
    return all_passed, checks

def verify_build() -> Tuple[bool, List[str]]:
    """Verify build process."""
    print_header("4. Build Verification")
    
    checks = []
    all_passed = True
    
    # Check frontend build
    print_info("Running frontend build...")
    result = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True)
    
    if result.returncode == 0:
        print_success("Frontend build successful")
        checks.append(True)
        
        # Check dist directory
        if check_file_exists('dist'):
            print_success("dist directory created")
            checks.append(True)
        else:
            print_error("dist directory not created")
            checks.append(False)
            all_passed = False
    else:
        print_error("Frontend build failed")
        print_error(result.stderr)
        checks.append(False)
        all_passed = False
    
    # Check TypeScript
    print_info("Running TypeScript type check...")
    result = subprocess.run(['npm', 'run', 'typecheck'], capture_output=True, text=True)
    
    if result.returncode == 0:
        print_success("TypeScript type check passed")
        checks.append(True)
    else:
        print_error("TypeScript type check failed")
        print_error(result.stderr)
        checks.append(False)
        all_passed = False
    
    return all_passed, checks

def verify_database_schema() -> Tuple[bool, List[str]]:
    """Verify database schema."""
    print_header("5. Database Schema Verification")
    
    checks = []
    all_passed = True
    
    # Check migration file
    migration_file = 'infra/database/migrations/001_initial_schema.sql'
    if check_file_exists(migration_file):
        print_success(f"Migration file exists: {migration_file}")
        checks.append(True)
        
        # Check for required tables
        with open(migration_file, 'r') as f:
            content = f.read()
        
        required_tables = [
            'users', 'roles', 'user_roles', 'depots',
            'inventory_items', 'inventory_transactions',
            'shipments', 'routes', 'forecasts',
            'sensor_readings', 'sensor_alerts',
            'simulation_scenarios', 'recommendations'
        ]
        
        for table in required_tables:
            if f'CREATE TABLE IF NOT EXISTS {table}' in content:
                print_success(f"Table defined: {table}")
                checks.append(True)
            else:
                print_error(f"Table not defined: {table}")
                checks.append(False)
                all_passed = False
    else:
        print_error(f"Migration file not found: {migration_file}")
        checks.append(False)
        all_passed = False
    
    # Check seed script
    if check_file_exists('apps/api/src/sangam_api/scripts/seed.py'):
        print_success("Seed script exists")
        checks.append(True)
    else:
        print_error("Seed script not found")
        checks.append(False)
        all_passed = False
    
    return all_passed, checks

def verify_api_endpoints() -> Tuple[bool, List[str]]:
    """Verify API endpoints."""
    print_header("6. API Endpoints Verification")
    
    checks = []
    all_passed = True
    
    # Check routes registration
    routes_file = 'apps/api/src/sangam_api/api/routes/__init__.py'
    if check_file_exists(routes_file):
        with open(routes_file, 'r') as f:
            content = f.read()
        
        required_routers = [
            'health_router',
            'auth_router',
            'admin_router',
            'depots_router',
            'shipments_router',
            'routes_router',
            'inventory_router',
            'forecasting_router',
            'simulation_router',
            'iot_router',
            'recommendations_router',
        ]
        
        for router in required_routers:
            if router in content:
                print_success(f"Router registered: {router}")
                checks.append(True)
            else:
                print_error(f"Router not registered: {router}")
                checks.append(False)
                all_passed = False
    else:
        print_error(f"Routes file not found: {routes_file}")
        checks.append(False)
        all_passed = False
    
    return all_passed, checks

def verify_tests() -> Tuple[bool, List[str]]:
    """Verify test setup."""
    print_header("7. Tests Verification")
    
    checks = []
    all_passed = True
    
    # Check test directories
    test_dirs = [
        'tests',
        'tests/unit',
        'tests/integration',
        'apps/api/tests',
        'apps/api/tests/unit',
        'src/tests',
    ]
    
    for test_dir in test_dirs:
        if check_file_exists(test_dir):
            print_success(f"Test directory exists: {test_dir}")
            checks.append(True)
        else:
            print_warning(f"Test directory not found: {test_dir}")
            checks.append(False)
    
    # Check test files
    test_files = [
        'tests/unit/test_auth.py',
        'tests/unit/test_permissions.py',
        'tests/unit/test_inventory_service.py',
        'tests/unit/test_forecasting_models.py',
        'tests/unit/test_iot.py',
        'tests/unit/test_recommendations.py',
        'src/tests/offline.test.ts',
    ]
    
    for test_file in test_files:
        if check_file_exists(test_file):
            print_success(f"Test file exists: {test_file}")
            checks.append(True)
        else:
            print_warning(f"Test file not found: {test_file}")
            checks.append(False)
    
    return all_passed, checks

def verify_documentation() -> Tuple[bool, List[str]]:
    """Verify documentation."""
    print_header("8. Documentation Verification")
    
    checks = []
    all_passed = True
    
    # Check documentation files
    doc_files = [
        'README.md',
        'docs/ARCHITECTURE.md',
        'docs/AUTHENTICATION.md',
        'docs/DEPLOYMENT.md',
        'docs/SETUP.md',
        'docs/INVENTORY.md',
        'docs/IOT_MODULE.md',
        'docs/RECOMMENDATIONS_MODULE.md',
        'docs/OFFLINE_SUPPORT.md',
    ]
    
    for doc_file in doc_files:
        if check_file_exists(doc_file):
            print_success(f"Documentation exists: {doc_file}")
            checks.append(True)
        else:
            print_warning(f"Documentation not found: {doc_file}")
            checks.append(False)
    
    return all_passed, checks

def verify_deployment_config() -> Tuple[bool, List[str]]:
    """Verify deployment configuration."""
    print_header("9. Deployment Configuration Verification")
    
    checks = []
    all_passed = True
    
    # Check Vercel config
    if check_file_exists('vercel.json'):
        with open('vercel.json', 'r') as f:
            vercel_config = json.load(f)
        
        if 'buildCommand' in vercel_config and 'outputDirectory' in vercel_config:
            print_success("Vercel configuration valid")
            checks.append(True)
        else:
            print_error("Vercel configuration incomplete")
            checks.append(False)
            all_passed = False
    else:
        print_error("vercel.json not found")
        checks.append(False)
        all_passed = False
    
    # Check Docker config
    docker_files = [
        'infra/docker/Dockerfile.api',
        'infra/docker/docker-compose.yml',
    ]
    
    for docker_file in docker_files:
        if check_file_exists(docker_file):
            print_success(f"Docker config exists: {docker_file}")
            checks.append(True)
        else:
            print_warning(f"Docker config not found: {docker_file}")
            checks.append(False)
    
    # Check Service Worker
    if check_file_exists('public/sw.js'):
        print_success("Service Worker exists")
        checks.append(True)
    else:
        print_error("Service Worker not found")
        checks.append(False)
        all_passed = False
    
    return all_passed, checks

def main():
    """Main verification function."""
    print_header("SANGAM Integration Verification")
    print_info("Starting comprehensive integration and deployment readiness check...\n")
    
    results = []
    
    # Run all verifications
    results.append(("Repository Structure", *verify_repository_structure()))
    results.append(("Dependencies", *verify_dependencies()))
    results.append(("Environment Configuration", *verify_environment_config()))
    results.append(("Build", *verify_build()))
    results.append(("Database Schema", *verify_database_schema()))
    results.append(("API Endpoints", *verify_api_endpoints()))
    results.append(("Tests", *verify_tests()))
    results.append(("Documentation", *verify_documentation()))
    results.append(("Deployment Configuration", *verify_deployment_config()))
    
    # Print summary
    print_header("Verification Summary")
    
    total_checks = 0
    passed_checks = 0
    
    for name, passed, checks in results:
        status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
        print(f"{name}: {status} ({sum(checks)}/{len(checks)} checks)")
        total_checks += len(checks)
        passed_checks += sum(checks)
    
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}Total: {passed_checks}/{total_checks} checks passed{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")
    
    # Final verdict
    all_passed = all(passed for _, passed, _ in results)
    
    if all_passed:
        print_success("✅ ALL CHECKS PASSED - Ready for deployment!")
        print_info("\nNext steps:")
        print_info("1. Review DEPLOYMENT_GUIDE.md for deployment instructions")
        print_info("2. Set up staging environment")
        print_info("3. Conduct security audit")
        print_info("4. Plan production deployment")
        return 0
    else:
        print_error("❌ SOME CHECKS FAILED - Review issues before deployment")
        print_info("\nPlease address the issues above and re-run verification.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
