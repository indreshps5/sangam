# Shared API Contracts
# TypeScript types and OpenAPI specifications shared between frontend and backend

## Purpose
This package contains the single source of truth for API contracts between
the SANGAM frontend and backend services.

## Contents
- `src/types/` - TypeScript type definitions matching backend schemas
- `src/openapi/` - OpenAPI 3.1 specification
- `src/constants/` - Shared constants and enums

## Usage
```typescript
import { Shipment, Warehouse, Forecast } from '@sangam/contracts';
```
