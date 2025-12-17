# DBS Event Management System - Test Suite

## Overview

This test suite implements both unit testing and integration testing approaches for the DBS Event Management System, focusing on core functionality as required by the client.

## Test Files

### Core Test Files
- **`test_unit.py`** - Unit tests for core models and basic routes
- **`test_integration.py`** - Integration tests for core workflows
- **`conftest.py`** - Test configuration and fixtures

## Test Coverage

### Unit Tests (`test_unit.py`)
- **User Model**: User creation, password hashing
- **Event Model**: Event creation, capacity management methods
- **Registration Model**: Registration creation
- **Basic Routes**: Homepage, login, registration, protected routes, role-based access

### Integration Tests (`test_integration.py`)
- **Student Registration Workflow**: Complete student journey from registration to event participation
- **Event Management Workflow**: Organizer and admin event creation
- **Registration System Workflow**: Event capacity, duplicate prevention, unregistration
- **Role-Based Access Workflow**: Authorization control for different user roles

## Running Tests

### Prerequisites
```bash
pip install pytest pytest-flask
```

### Run All Tests
```bash
python -m pytest tests/ -v
```

### Run Specific Test File
```bash
# Unit tests only
python -m pytest tests/test_unit.py -v

# Integration tests only  
python -m pytest tests/test_integration.py -v
```

### Run with Coverage
```bash
python -m pytest tests/ --cov=backend --cov-report=html
```

## Test Results

The test suite currently contains **25 tests** covering:
- 13 unit tests
- 12 integration tests

All tests pass successfully, validating the core functionality of the event management system.

## Key Features Tested

### User Management
- Student registration and login
- Password hashing and verification
- Role-based access control (student, organizer, admin)

### Event Management  
- Event creation by organizers and admins
- Event capacity management
- Society-linked and standalone events

### Registration System
- Event registration (free and paid)
- Invoice upload for paid events
- Capacity enforcement
- Duplicate registration prevention
- Event unregistration

### Security & Access Control
- Protected route authentication
- Role-based authorization
- Login/logout functionality

This focused test suite ensures the core features of the DBS Event Management System work correctly while maintaining a manageable scope for ongoing development and maintenance.
