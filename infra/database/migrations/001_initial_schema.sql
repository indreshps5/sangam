-- SANGAM Canonical Database Schema
-- PostgreSQL 15+ with UUID support
-- All timestamps use UTC (TIMESTAMPTZ)
-- All primary keys are UUID v4

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ═══════════════════════════════════════════════════════════════
-- ROLES & USERS
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description VARCHAR(500),
    permissions VARCHAR(2000),  -- JSON array of permission strings
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMPTZ,
    preferred_timezone VARCHAR(50) DEFAULT 'UTC',
    preferred_language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Many-to-many: users <-> roles
CREATE TABLE IF NOT EXISTS user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

-- ═══════════════════════════════════════════════════════════════
-- DEPOTS
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS depots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE,
    depot_type VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    region VARCHAR(100) NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    capacity_units INTEGER NOT NULL,
    current_utilization DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    address TEXT,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_depots_capacity_positive CHECK (capacity_units > 0),
    CONSTRAINT ck_depots_utilization_range CHECK (current_utilization >= 0.0 AND current_utilization <= 1.0),
    CONSTRAINT ck_depots_latitude_range CHECK (latitude >= -90.0 AND latitude <= 90.0),
    CONSTRAINT ck_depots_longitude_range CHECK (longitude >= -180.0 AND longitude <= 180.0)
);

CREATE INDEX IF NOT EXISTS idx_depots_code ON depots(code);
CREATE INDEX IF NOT EXISTS idx_depots_status ON depots(status);
CREATE INDEX IF NOT EXISTS idx_depots_region ON depots(region);
CREATE INDEX IF NOT EXISTS idx_depots_type ON depots(depot_type);

-- ═══════════════════════════════════════════════════════════════
-- INVENTORY
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS inventory_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    depot_id UUID NOT NULL REFERENCES depots(id) ON DELETE CASCADE,
    sku VARCHAR(100) NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'unit',
    quantity_on_hand DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    quantity_reserved DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    min_stock_level DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    max_stock_level DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    unit_cost DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    location_code VARCHAR(50),
    batch_number VARCHAR(100),
    expiry_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_inventory_on_hand_non_negative CHECK (quantity_on_hand >= 0),
    CONSTRAINT ck_inventory_reserved_non_negative CHECK (quantity_reserved >= 0),
    CONSTRAINT ck_inventory_min_stock_non_negative CHECK (min_stock_level >= 0),
    CONSTRAINT ck_inventory_max_stock_non_negative CHECK (max_stock_level >= 0),
    CONSTRAINT ck_inventory_unit_cost_non_negative CHECK (unit_cost >= 0)
);

CREATE INDEX IF NOT EXISTS idx_inventory_depot ON inventory_items(depot_id);
CREATE INDEX IF NOT EXISTS idx_inventory_sku ON inventory_items(sku);
CREATE INDEX IF NOT EXISTS idx_inventory_category ON inventory_items(category);

CREATE TABLE IF NOT EXISTS inventory_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inventory_item_id UUID NOT NULL REFERENCES inventory_items(id) ON DELETE CASCADE,
    depot_id UUID NOT NULL REFERENCES depots(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50) NOT NULL,
    quantity DOUBLE PRECISION NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'unit',
    reference_id UUID,
    reference_type VARCHAR(50),
    notes TEXT,
    performed_by UUID REFERENCES users(id) ON DELETE SET NULL,
    performed_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_inv_transaction_quantity_non_zero CHECK (quantity != 0)
);

CREATE INDEX IF NOT EXISTS idx_inv_trans_item ON inventory_transactions(inventory_item_id);
CREATE INDEX IF NOT EXISTS idx_inv_trans_depot ON inventory_transactions(depot_id);
CREATE INDEX IF NOT EXISTS idx_inv_trans_type ON inventory_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_inv_trans_performed_at ON inventory_transactions(performed_at DESC);

-- ═══════════════════════════════════════════════════════════════
-- DEMAND & FORECASTING
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS demand_observations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    depot_id UUID NOT NULL REFERENCES depots(id) ON DELETE CASCADE,
    product_category VARCHAR(100) NOT NULL,
    sku VARCHAR(100),
    observation_date DATE NOT NULL,
    demand_quantity DOUBLE PRECISION NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL DEFAULT 'unit',
    source VARCHAR(50) NOT NULL DEFAULT 'manual',
    is_outlier BOOLEAN NOT NULL DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_demand_quantity_non_negative CHECK (demand_quantity >= 0)
);

CREATE INDEX IF NOT EXISTS idx_demand_depot ON demand_observations(depot_id);
CREATE INDEX IF NOT EXISTS idx_demand_category ON demand_observations(product_category);
CREATE INDEX IF NOT EXISTS idx_demand_date ON demand_observations(observation_date);
CREATE INDEX IF NOT EXISTS idx_demand_source ON demand_observations(source);

CREATE TABLE IF NOT EXISTS forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    depot_id UUID NOT NULL REFERENCES depots(id) ON DELETE CASCADE,
    product_category VARCHAR(100),
    model_type VARCHAR(50) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    forecast_horizon_days INTEGER NOT NULL,
    confidence_level DOUBLE PRECISION NOT NULL DEFAULT 0.95,
    accuracy_score DOUBLE PRECISION,
    training_data_end_date DATE,
    parameters TEXT,  -- JSON model hyperparameters
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_forecasts_horizon_positive CHECK (forecast_horizon_days > 0),
    CONSTRAINT ck_forecasts_confidence_range CHECK (confidence_level >= 0.5 AND confidence_level <= 0.99),
    CONSTRAINT ck_forecasts_accuracy_non_negative CHECK (accuracy_score >= 0)
);

CREATE INDEX IF NOT EXISTS idx_forecasts_depot ON forecasts(depot_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_model_type ON forecasts(model_type);
CREATE INDEX IF NOT EXISTS idx_forecasts_status ON forecasts(status);

CREATE TABLE IF NOT EXISTS forecast_data_points (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    forecast_id UUID NOT NULL REFERENCES forecasts(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    predicted_demand DOUBLE PRECISION NOT NULL,
    lower_bound DOUBLE PRECISION NOT NULL,
    upper_bound DOUBLE PRECISION NOT NULL,
    CONSTRAINT ck_fdp_predicted_non_negative CHECK (predicted_demand >= 0),
    CONSTRAINT ck_fdp_bounds_order CHECK (lower_bound <= upper_bound)
);

CREATE INDEX IF NOT EXISTS idx_fdp_forecast ON forecast_data_points(forecast_id);
CREATE INDEX IF NOT EXISTS idx_fdp_date ON forecast_data_points(forecast_date);

-- ═══════════════════════════════════════════════════════════════
-- ROUTES & SHIPMENTS
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS routes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    code VARCHAR(30) NOT NULL UNIQUE,
    origin_depot_id UUID NOT NULL REFERENCES depots(id) ON DELETE CASCADE,
    destination_depot_id UUID NOT NULL REFERENCES depots(id) ON DELETE CASCADE,
    status VARCHAR(30) NOT NULL DEFAULT 'planned',
    distance_km DOUBLE PRECISION NOT NULL,
    estimated_duration_hours DOUBLE PRECISION NOT NULL,
    optimization_objective VARCHAR(50) NOT NULL DEFAULT 'balanced',
    waypoint_data TEXT,  -- JSON array of waypoints
    vehicle_type VARCHAR(50),
    max_weight_kg DOUBLE PRECISION NOT NULL DEFAULT 10000.0,
    max_volume_m3 DOUBLE PRECISION NOT NULL DEFAULT 50.0,
    cost_per_km DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    carbon_emission_factor DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_routes_distance_positive CHECK (distance_km > 0),
    CONSTRAINT ck_routes_duration_positive CHECK (estimated_duration_hours > 0),
    CONSTRAINT ck_routes_max_weight_positive CHECK (max_weight_kg > 0),
    CONSTRAINT ck_routes_max_volume_positive CHECK (max_volume_m3 > 0),
    CONSTRAINT ck_routes_cost_non_negative CHECK (cost_per_km >= 0),
    CONSTRAINT ck_routes_emission_non_negative CHECK (carbon_emission_factor >= 0)
);

CREATE INDEX IF NOT EXISTS idx_routes_code ON routes(code);
CREATE INDEX IF NOT EXISTS idx_routes_status ON routes(status);
CREATE INDEX IF NOT EXISTS idx_routes_origin ON routes(origin_depot_id);
CREATE INDEX IF NOT EXISTS idx_routes_destination ON routes(destination_depot_id);

CREATE TABLE IF NOT EXISTS shipments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    origin_depot_id UUID NOT NULL REFERENCES depots(id) ON DELETE CASCADE,
    destination_depot_id UUID NOT NULL REFERENCES depots(id) ON DELETE CASCADE,
    route_id UUID REFERENCES routes(id) ON DELETE SET NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    weight_kg DOUBLE PRECISION NOT NULL,
    volume_m3 DOUBLE PRECISION NOT NULL,
    priority INTEGER NOT NULL DEFAULT 3,
    shipment_type VARCHAR(50) NOT NULL DEFAULT 'standard',
    carrier_name VARCHAR(200),
    tracking_number VARCHAR(100) UNIQUE,
    estimated_departure TIMESTAMPTZ,
    actual_departure TIMESTAMPTZ,
    estimated_arrival TIMESTAMPTZ,
    actual_arrival TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_shipments_weight_positive CHECK (weight_kg > 0),
    CONSTRAINT ck_shipments_volume_positive CHECK (volume_m3 > 0),
    CONSTRAINT ck_shipments_priority_range CHECK (priority >= 1 AND priority <= 5)
);

CREATE INDEX IF NOT EXISTS idx_shipments_status ON shipments(status);
CREATE INDEX IF NOT EXISTS idx_shipments_origin ON shipments(origin_depot_id);
CREATE INDEX IF NOT EXISTS idx_shipments_destination ON shipments(destination_depot_id);
CREATE INDEX IF NOT EXISTS idx_shipments_route ON shipments(route_id);
CREATE INDEX IF NOT EXISTS idx_shipments_tracking ON shipments(tracking_number);
CREATE INDEX IF NOT EXISTS idx_shipments_created_at ON shipments(created_at DESC);

-- ═══════════════════════════════════════════════════════════════
-- SENSORS & ALERTS
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS sensor_readings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_id VARCHAR(100) NOT NULL,
    depot_id UUID REFERENCES depots(id) ON DELETE SET NULL,
    shipment_id UUID REFERENCES shipments(id) ON DELETE SET NULL,
    sensor_type VARCHAR(50) NOT NULL,
    reading_value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20) NOT NULL,
    reading_timestamp TIMESTAMPTZ NOT NULL,
    quality_flag VARCHAR(20) NOT NULL DEFAULT 'good',
    raw_payload TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_sensor_device ON sensor_readings(device_id);
CREATE INDEX IF NOT EXISTS idx_sensor_type ON sensor_readings(sensor_type);
CREATE INDEX IF NOT EXISTS idx_sensor_depot ON sensor_readings(depot_id);
CREATE INDEX IF NOT EXISTS idx_sensor_timestamp ON sensor_readings(reading_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_quality ON sensor_readings(quality_flag);

CREATE TABLE IF NOT EXISTS alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'triggered',
    source_type VARCHAR(50) NOT NULL,
    source_id UUID,
    depot_id UUID REFERENCES depots(id) ON DELETE SET NULL,
    shipment_id UUID REFERENCES shipments(id) ON DELETE SET NULL,
    triggered_by UUID REFERENCES users(id) ON DELETE SET NULL,
    acknowledged_by UUID REFERENCES users(id) ON DELETE SET NULL,
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_source_type ON alerts(source_type);
CREATE INDEX IF NOT EXISTS idx_alerts_depot ON alerts(depot_id);
CREATE INDEX IF NOT EXISTS idx_alerts_shipment ON alerts(shipment_id);

-- ═══════════════════════════════════════════════════════════════
-- SIMULATION, RECOMMENDATIONS & APPROVALS
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS simulation_scenarios (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
    scenario_type VARCHAR(50) NOT NULL,
    parameters TEXT,  -- JSON simulation parameters
    input_data_snapshot TEXT,  -- JSON input data
    results TEXT,  -- JSON simulation results
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    duration_seconds DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_simulation_duration_non_negative CHECK (duration_seconds >= 0)
);

CREATE INDEX IF NOT EXISTS idx_simulation_status ON simulation_scenarios(status);
CREATE INDEX IF NOT EXISTS idx_simulation_type ON simulation_scenarios(scenario_type);

CREATE TABLE IF NOT EXISTS recommendations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category VARCHAR(50) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'generated',
    title VARCHAR(300) NOT NULL,
    description TEXT,
    rationale TEXT,
    confidence_score DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    expected_impact TEXT,  -- JSON expected impact
    implementation_cost DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    expected_savings DOUBLE PRECISION NOT NULL DEFAULT 0.0,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    priority INTEGER NOT NULL DEFAULT 3,
    expiry_date TIMESTAMPTZ,
    depot_id UUID REFERENCES depots(id) ON DELETE SET NULL,
    generated_by_model VARCHAR(100),
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    approved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_recommendations_confidence_range CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    CONSTRAINT ck_recommendations_priority_range CHECK (priority >= 1 AND priority <= 5),
    CONSTRAINT ck_recommendations_cost_non_negative CHECK (implementation_cost >= 0),
    CONSTRAINT ck_recommendations_savings_non_negative CHECK (expected_savings >= 0)
);

CREATE INDEX IF NOT EXISTS idx_recommendations_category ON recommendations(category);
CREATE INDEX IF NOT EXISTS idx_recommendations_status ON recommendations(status);
CREATE INDEX IF NOT EXISTS idx_recommendations_depot ON recommendations(depot_id);

CREATE TABLE IF NOT EXISTS approval_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID NOT NULL,
    requester_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    approver_id UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    priority INTEGER NOT NULL DEFAULT 3,
    reason TEXT,
    decision TEXT,
    decided_at TIMESTAMPTZ,
    due_date TIMESTAMPTZ,
    escalation_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_approval_escalation_non_negative CHECK (escalation_count >= 0)
);

CREATE INDEX IF NOT EXISTS idx_approval_entity ON approval_records(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_approval_status ON approval_records(status);
CREATE INDEX IF NOT EXISTS idx_approval_requester ON approval_records(requester_id);
CREATE INDEX IF NOT EXISTS idx_approval_approver ON approval_records(approver_id);

-- ═══════════════════════════════════════════════════════════════
-- AUDIT LOG
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    timestamp TIMESTAMPTZ NOT NULL,
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    changes TEXT,  -- JSON diff of changes
    metadata TEXT  -- JSON additional context
);

CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp DESC);

-- ═══════════════════════════════════════════════════════════════
-- TRIGGERS: Auto-update updated_at
-- ═══════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT unnest(ARRAY[
            'roles', 'users', 'depots', 'inventory_items', 'inventory_transactions',
            'demand_observations', 'forecasts', 'routes', 'shipments',
            'sensor_readings', 'alerts', 'simulation_scenarios',
            'recommendations', 'approval_records'
        ])
    LOOP
        EXECUTE format(
            'CREATE TRIGGER update_%s_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION update_updated_at_column()',
            t, t
        );
    END LOOP;
END;
$$;
