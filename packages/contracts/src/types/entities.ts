/**
 * Simulation, Recommendation, Approval, Audit, User & Role types.
 */

import type {
  SimulationStatus,
  RecommendationStatus,
  RecommendationCategory,
  ApprovalStatus,
  AuditAction,
} from './enums';

// ─── Simulation ───

export interface SimulationScenario {
  id: string;
  name: string;
  description: string | null;
  status: SimulationStatus;
  scenario_type: string;
  parameters: string | null;
  input_data_snapshot: string | null;
  results: string | null;
  created_by: string | null;
  started_at: string | null;
  completed_at: string | null;
  duration_seconds: number | null;
  created_at: string;
  updated_at: string;
}

export interface SimulationScenarioListResponse {
  items: SimulationScenario[];
  total: number;
  skip: number;
  limit: number;
}

// ─── Recommendation ───

export interface Recommendation {
  id: string;
  category: RecommendationCategory;
  status: RecommendationStatus;
  title: string;
  description: string | null;
  rationale: string | null;
  confidence_score: number;
  expected_impact: string | null;
  implementation_cost: number;
  expected_savings: number;
  currency: string;
  priority: number;
  expiry_date: string | null;
  depot_id: string | null;
  generated_by_model: string | null;
  approved_by: string | null;
  approved_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface RecommendationListResponse {
  items: Recommendation[];
  total: number;
  skip: number;
  limit: number;
}

// ─── Approval ───

export interface ApprovalRecord {
  id: string;
  entity_type: string;
  entity_id: string;
  requester_id: string;
  approver_id: string | null;
  status: ApprovalStatus;
  priority: number;
  reason: string | null;
  decision: string | null;
  decided_at: string | null;
  due_date: string | null;
  escalation_count: number;
  created_at: string;
  updated_at: string;
}

export interface ApprovalRecordListResponse {
  items: ApprovalRecord[];
  total: number;
  skip: number;
  limit: number;
}

// ─── Audit ───

export interface AuditLog {
  id: string;
  user_id: string | null;
  action: AuditAction;
  entity_type: string;
  entity_id: string | null;
  timestamp: string;
  ip_address: string | null;
  user_agent: string | null;
  changes: string | null;
  metadata: string | null;
}

export interface AuditLogListResponse {
  items: AuditLog[];
  total: number;
  skip: number;
  limit: number;
}

// ─── User & Role ───

export interface Role {
  id: string;
  name: string;
  description: string | null;
  permissions: string | null;
  is_system: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_verified: boolean;
  last_login_at: string | null;
  preferred_timezone: string | null;
  preferred_language: string | null;
  roles: Role[];
  created_at: string;
  updated_at: string;
}

export interface UserCreate {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  preferred_timezone?: string;
  preferred_language?: string;
}

export interface UserListResponse {
  items: User[];
  total: number;
  skip: number;
  limit: number;
}
