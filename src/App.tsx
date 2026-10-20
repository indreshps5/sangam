import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  FolderTree,
  Server,
  Database,
  Brain,
  FileText,
  TestTube,
  Settings,
  ChevronRight,
  CheckCircle2,
  Circle,
  AlertTriangle,
  ExternalLink,
  GitBranch,
  Shield,
  Zap,
  Globe,
  Box,
  Layers,
  ArrowRight,
} from 'lucide-react';

type TabId = 'overview' | 'structure' | 'backend' | 'database' | 'ml' | 'docs' | 'tests' | 'deploy';

interface Tab {
  id: TabId;
  label: string;
  icon: React.ReactNode;
}

const tabs: Tab[] = [
  { id: 'overview', label: 'Overview', icon: <LayoutDashboard size={18} /> },
  { id: 'structure', label: 'Structure', icon: <FolderTree size={18} /> },
  { id: 'backend', label: 'Backend', icon: <Server size={18} /> },
  { id: 'database', label: 'Database', icon: <Database size={18} /> },
  { id: 'ml', label: 'ML', icon: <Brain size={18} /> },
  { id: 'docs', label: 'Docs', icon: <FileText size={18} /> },
  { id: 'tests', label: 'Tests', icon: <TestTube size={18} /> },
  { id: 'deploy', label: 'Deploy', icon: <Globe size={18} /> },
];

const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.08, delayChildren: 0.1 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 15 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export default function App() {
  const [activeTab, setActiveTab] = useState<TabId>('overview');

  return (
    <div className="min-h-screen bg-sangam-900 text-sangam-200">
      {/* Header */}
      <header className="border-b border-sangam-700/50 bg-sangam-900/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-accent-blue to-accent-cyan flex items-center justify-center">
                <Layers size={20} className="text-white" />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white tracking-tight">SANGAM</h1>
                <p className="text-xs text-sangam-400 -mt-0.5">Predictive Logistics & Supply Chain</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-accent-emerald/10 text-accent-emerald border border-accent-emerald/20">
                <span className="inline-block w-1.5 h-1.5 rounded-full bg-accent-emerald mr-1.5 animate-pulse"></span>
                Foundation Ready
              </span>
              <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-sangam-700/50 text-sangam-300">
                v0.1.0
              </span>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Tab Navigation */}
        <nav className="flex gap-1 mb-8 overflow-x-auto pb-2 scrollbar-thin">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium whitespace-nowrap transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-accent-blue/10 text-accent-blue border border-accent-blue/30'
                  : 'text-sangam-400 hover:text-sangam-200 hover:bg-sangam-800/50'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
          >
            {activeTab === 'overview' && <OverviewPanel />}
            {activeTab === 'structure' && <StructurePanel />}
            {activeTab === 'backend' && <BackendPanel />}
            {activeTab === 'database' && <DatabasePanel />}
            {activeTab === 'ml' && <MLPanel />}
            {activeTab === 'docs' && <DocsPanel />}
            {activeTab === 'tests' && <TestsPanel />}
            {activeTab === 'deploy' && <DeployPanel />}
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}

/* ─── Overview Panel ─── */
function OverviewPanel() {
  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      {/* Hero */}
      <motion.div variants={itemVariants} className="mb-8">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-sangam-800 to-sangam-900 border border-sangam-700/50 p-8">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_rgba(59,130,246,0.1),_transparent_50%)]"></div>
          <div className="relative">
            <h2 className="text-3xl font-bold text-white mb-3">
              Project Foundation <span className="text-accent-blue">Established</span>
            </h2>
            <p className="text-sangam-400 max-w-2xl leading-relaxed">
              SANGAM is a predictive logistics platform built with a modular monorepo architecture.
              The foundation includes React + TypeScript frontend, FastAPI backend with SOLID principles,
              PostgreSQL persistence, ML forecasting module, and comprehensive documentation.
            </p>
          </div>
        </div>
      </motion.div>

      {/* Architecture Diagram */}
      <motion.div variants={itemVariants} className="mb-8">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Layers size={20} className="text-accent-cyan" />
          System Architecture
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ArchBlock
            title="Frontend"
            subtitle="Vercel Deployment"
            tech={['React 18', 'TypeScript', 'Tailwind CSS', 'Vite']}
            color="blue"
            icon={<Globe size={20} />}
          />
          <ArchBlock
            title="API"
            subtitle="Railway / Fly.io"
            tech={['FastAPI', 'SQLAlchemy', 'Pydantic', 'structlog']}
            color="emerald"
            icon={<Server size={20} />}
          />
          <ArchBlock
            title="Data & ML"
            subtitle="Managed PostgreSQL"
            tech={['PostgreSQL 15', 'Alembic', 'XGBoost', 'Prophet']}
            color="violet"
            icon={<Brain size={20} />}
          />
        </div>
        {/* Flow arrows */}
        <div className="flex items-center justify-center gap-2 mt-4 text-sangam-500">
          <div className="h-px flex-1 bg-sangam-700/50"></div>
          <span className="text-xs px-3 py-1 rounded-full bg-sangam-800 border border-sangam-700/50">
            REST API • JSON • OpenAPI 3.1
          </span>
          <div className="h-px flex-1 bg-sangam-700/50"></div>
        </div>
      </motion.div>

      {/* Status Cards */}
      <motion.div variants={itemVariants} className="mb-8">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <CheckCircle2 size={20} className="text-accent-emerald" />
          Implementation Status
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <StatusCard title="Frontend (apps/web)" status="complete" items={['Vite + React + TS', 'Tailwind CSS 4', 'Dashboard UI', 'Vercel config']} />
          <StatusCard title="Backend (apps/api)" status="complete" items={['FastAPI app factory', 'SOLID architecture', 'Repository pattern', 'Health endpoints']} />
          <StatusCard title="Database (infra)" status="complete" items={['PostgreSQL schema', 'Docker Compose', 'Alembic config', 'Migration files']} />
          <StatusCard title="ML Module" status="complete" items={['Forecasting interface', 'Evaluation metrics', 'Model abstractions', 'Requirements']} />
          <StatusCard title="Contracts" status="complete" items={['TypeScript types', 'Shared enums', 'API constants', 'OpenAPI ready']} />
          <StatusCard title="Testing" status="complete" items={['Unit tests', 'Integration tests', 'Schema validation', 'Metric tests']} />
          <StatusCard title="Documentation" status="complete" items={['Architecture doc', 'Setup guide', 'Deployment guide', 'README files']} />
          <StatusCard title="Config" status="complete" items={['.editorconfig (CRLF)', '.gitattributes', '.gitignore', 'vercel.json']} />
        </div>
      </motion.div>

      {/* Key Principles */}
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Shield size={20} className="text-accent-amber" />
          Design Principles
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <PrincipleCard
            icon={<Layers size={18} />}
            title="SOLID Backend"
            description="Router → Service → Repository Interface → Repository Implementation. Business logic separated from HTTP concerns."
          />
          <PrincipleCard
            icon={<GitBranch size={18} />}
            title="Dependency Injection"
            description="Services depend on repository interfaces, not implementations. Easy to test and swap data sources."
          />
          <PrincipleCard
            icon={<Box size={18} />}
            title="Modular Monorepo"
            description="Clear module boundaries: apps, packages, ml, infra, docs, tests. Each module independently understandable."
          />
          <PrincipleCard
            icon={<Zap size={18} />}
            title="CRLF Consistency"
            description=".editorconfig + .gitattributes enforce CRLF line endings across all text source files."
          />
        </div>
      </motion.div>
    </motion.div>
  );
}

/* ─── Structure Panel ─── */
function StructurePanel() {
  const tree = [
    { name: 'sangam/', type: 'root', children: [
      { name: 'src/', type: 'dir', desc: 'Frontend source (apps/web)', children: [
        { name: 'App.tsx', type: 'file', desc: 'Main application component' },
        { name: 'main.tsx', type: 'file', desc: 'React entry point' },
        { name: 'index.css', type: 'file', desc: 'Tailwind CSS imports' },
      ]},
      { name: 'apps/', type: 'dir', desc: 'Application modules', children: [
        { name: 'api/', type: 'dir', desc: 'FastAPI backend', children: [
          { name: 'src/sangam_api/', type: 'dir', desc: 'Python package', children: [
            { name: 'main.py', type: 'file', desc: 'Application factory' },
            { name: 'config.py', type: 'file', desc: 'Pydantic settings' },
            { name: 'api/', type: 'dir', desc: 'HTTP layer (routes, schemas, middleware)' },
            { name: 'services/', type: 'dir', desc: 'Business logic' },
            { name: 'repositories/', type: 'dir', desc: 'Data access (interface + impl)' },
            { name: 'models/', type: 'dir', desc: 'SQLAlchemy ORM' },
            { name: 'core/', type: 'dir', desc: 'Cross-cutting (db, logging, exceptions)' },
          ]},
          { name: 'pyproject.toml', type: 'file', desc: 'Python project config' },
        ]},
      ]},
      { name: 'packages/', type: 'dir', desc: 'Shared packages', children: [
        { name: 'contracts/', type: 'dir', desc: 'API types & specs', children: [
          { name: 'src/types/', type: 'dir', desc: 'TypeScript type definitions' },
          { name: 'src/constants.ts', type: 'file', desc: 'Shared enums & constants' },
        ]},
      ]},
      { name: 'ml/', type: 'dir', desc: 'ML forecasting module', children: [
        { name: 'src/forecasting/', type: 'dir', desc: 'Demand forecasting models' },
        { name: 'src/evaluation/', type: 'dir', desc: 'Model evaluation metrics' },
        { name: 'requirements.txt', type: 'file', desc: 'ML dependencies' },
      ]},
      { name: 'infra/', type: 'dir', desc: 'Infrastructure configs', children: [
        { name: 'database/', type: 'dir', desc: 'SQL migrations & Alembic' },
        { name: 'docker/', type: 'dir', desc: 'Dockerfile & Compose' },
      ]},
      { name: 'docs/', type: 'dir', desc: 'Documentation', children: [
        { name: 'ARCHITECTURE.md', type: 'file', desc: 'System architecture' },
        { name: 'SETUP.md', type: 'file', desc: 'Setup instructions' },
        { name: 'DEPLOYMENT.md', type: 'file', desc: 'Deployment guide' },
      ]},
      { name: 'tests/', type: 'dir', desc: 'Test suites', children: [
        { name: 'unit/', type: 'dir', desc: 'Unit tests' },
        { name: 'integration/', type: 'dir', desc: 'Integration tests' },
      ]},
      { name: '.editorconfig', type: 'file', desc: 'CRLF enforcement' },
      { name: '.gitattributes', type: 'file', desc: 'Line ending normalization' },
      { name: 'vercel.json', type: 'file', desc: 'Vercel deployment config' },
    ]},
  ];

  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <FolderTree size={20} className="text-accent-cyan" />
          Monorepo Structure
        </h3>
        <p className="text-sangam-400 text-sm mb-6">
          Complete project tree with module descriptions. The root serves as <code className="text-accent-blue bg-sangam-800 px-1.5 py-0.5 rounded">apps/web</code> for the Vite frontend.
        </p>
      </motion.div>
      <motion.div variants={itemVariants} className="bg-sangam-800/50 rounded-xl border border-sangam-700/50 p-6 font-mono text-sm overflow-x-auto">
        <TreeNode nodes={tree} depth={0} />
      </motion.div>
    </motion.div>
  );
}

function TreeNode({ nodes, depth }: { nodes: any[]; depth: number }) {
  return (
    <div>
      {nodes.map((node, i) => (
        <div key={i}>
          <div className="flex items-center gap-2 py-1" style={{ paddingLeft: depth * 20 }}>
            <span className={
              node.type === 'root' ? 'text-accent-amber' :
              node.type === 'dir' ? 'text-accent-blue' :
              'text-sangam-400'
            }>
              {node.type === 'dir' || node.type === 'root' ? '📁 ' : '📄 '}
            </span>
            <span className={
              node.type === 'root' ? 'text-white font-bold' :
              node.type === 'dir' ? 'text-accent-blue font-medium' :
              'text-sangam-300'
            }>
              {node.name}
            </span>
            {node.desc && (
              <span className="text-sangam-500 text-xs ml-2">— {node.desc}</span>
            )}
          </div>
          {node.children && <TreeNode nodes={node.children} depth={depth + 1} />}
        </div>
      ))}
    </div>
  );
}

/* ─── Backend Panel ─── */
function BackendPanel() {
  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <Server size={20} className="text-accent-emerald" />
          Backend Architecture — FastAPI + SOLID
        </h3>
        <p className="text-sangam-400 text-sm mb-6">
          The backend follows strict SOLID principles with clear separation of concerns.
          Business logic is isolated from HTTP handling and data access.
        </p>
      </motion.div>

      {/* Request Flow */}
      <motion.div variants={itemVariants} className="mb-8">
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider">Request Flow</h4>
        <div className="flex flex-wrap items-center gap-2">
          {['HTTP Request', 'Router (thin)', 'Application Service', 'Repository Interface', 'Repository Impl', 'PostgreSQL'].map((step, i) => (
            <div key={i} className="flex items-center gap-2">
              <div className={`px-3 py-2 rounded-lg text-xs font-medium border ${
                i === 0 ? 'bg-sangam-800 border-sangam-600 text-sangam-300' :
                i === 1 ? 'bg-accent-blue/10 border-accent-blue/30 text-accent-blue' :
                i === 2 ? 'bg-accent-emerald/10 border-accent-emerald/30 text-accent-emerald' :
                i === 3 ? 'bg-accent-violet/10 border-accent-violet/30 text-accent-violet' :
                i === 4 ? 'bg-accent-amber/10 border-accent-amber/30 text-accent-amber' :
                'bg-accent-cyan/10 border-accent-cyan/30 text-accent-cyan'
              }`}>
                {step}
              </div>
              {i < 5 && <ArrowRight size={14} className="text-sangam-600" />}
            </div>
          ))}
        </div>
      </motion.div>

      {/* Layer Details */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <LayerCard
          title="Router Layer"
          color="blue"
          items={[
            'Thin controllers — no business logic',
            'HTTP concerns only (parsing, status codes)',
            'Dependency injection via FastAPI Depends',
            'Request validation via Pydantic schemas',
          ]}
          files={['api/routes/shipments.py', 'api/routes/warehouses.py', 'api/routes/forecasts.py']}
        />
        <LayerCard
          title="Service Layer"
          color="emerald"
          items={[
            'Contains all business logic & orchestration',
            'Depends on repository interfaces (DIP)',
            'Validation, transformation, error handling',
            'Testable without database',
          ]}
          files={['services/shipment_service.py', 'services/warehouse_service.py', 'services/forecast_service.py']}
        />
        <LayerCard
          title="Repository Interface"
          color="violet"
          items={[
            'Abstract base classes (ABC)',
            'Defines data access contracts',
            'No implementation details',
            'Enables mock testing',
          ]}
          files={['repositories/interfaces.py']}
        />
        <LayerCard
          title="Repository Implementation"
          color="amber"
          items={[
            'SQLAlchemy async session management',
            'Query building & execution',
            'Model ↔ Schema mapping',
            'Transaction handling',
          ]}
          files={['repositories/shipments.py']}
        />
      </motion.div>

      {/* Error Handling */}
      <motion.div variants={itemVariants} className="mb-8">
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider">Error Handling (RFC 7807)</h4>
        <div className="bg-sangam-800/50 rounded-xl border border-sangam-700/50 p-4">
          <pre className="text-xs text-sangam-300 overflow-x-auto">
{`{
  "type": "https://sangam.io/errors/NOT_FOUND",
  "title": "NOT_FOUND",
  "status": 404,
  "detail": "Shipment with identifier 'abc-123' not found",
  "instance": "/api/v1/shipments/abc-123",
  "resource": "Shipment",
  "identifier": "abc-123"
}`}
          </pre>
        </div>
      </motion.div>

      {/* Health Endpoints */}
      <motion.div variants={itemVariants}>
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider">Health Endpoints</h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <EndpointCard path="/api/v1/health" method="GET" desc="Basic liveness check" />
          <EndpointCard path="/api/v1/health/ready" method="GET" desc="DB connectivity check" />
          <EndpointCard path="/api/v1/health/live" method="GET" desc="Container probe" />
        </div>
      </motion.div>
    </motion.div>
  );
}

/* ─── Database Panel ─── */
function DatabasePanel() {
  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <Database size={20} className="text-accent-cyan" />
          Database — PostgreSQL 15
        </h3>
        <p className="text-sangam-400 text-sm mb-6">
          Relational data store with async SQLAlchemy access, Alembic migrations, and Docker Compose for local development.
        </p>
      </motion.div>

      {/* Schema */}
      <motion.div variants={itemVariants} className="mb-8">
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider">Schema Tables</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <TableCard
            name="warehouses"
            columns={[
              { name: 'id', type: 'UUID PK' },
              { name: 'name', type: 'VARCHAR(200)' },
              { name: 'code', type: 'VARCHAR(20) UNIQUE' },
              { name: 'region', type: 'VARCHAR(100)' },
              { name: 'latitude', type: 'DOUBLE' },
              { name: 'longitude', type: 'DOUBLE' },
              { name: 'capacity_units', type: 'INTEGER' },
              { name: 'current_utilization', type: 'DOUBLE' },
            ]}
          />
          <TableCard
            name="shipments"
            columns={[
              { name: 'id', type: 'UUID PK' },
              { name: 'origin_warehouse_id', type: 'UUID FK' },
              { name: 'destination_warehouse_id', type: 'UUID FK' },
              { name: 'status', type: 'VARCHAR(50)' },
              { name: 'weight_kg', type: 'DOUBLE' },
              { name: 'volume_m3', type: 'DOUBLE' },
              { name: 'priority', type: 'INTEGER' },
              { name: 'estimated_arrival', type: 'TIMESTAMPTZ' },
            ]}
          />
          <TableCard
            name="forecasts"
            columns={[
              { name: 'id', type: 'UUID PK' },
              { name: 'warehouse_id', type: 'UUID FK' },
              { name: 'product_category', type: 'VARCHAR(100)' },
              { name: 'forecast_horizon_days', type: 'INTEGER' },
              { name: 'confidence_level', type: 'DOUBLE' },
              { name: 'model_version', type: 'VARCHAR(50)' },
              { name: 'accuracy_score', type: 'DOUBLE' },
              { name: 'created_at', type: 'TIMESTAMPTZ' },
            ]}
          />
        </div>
      </motion.div>

      {/* Connection Management */}
      <motion.div variants={itemVariants} className="mb-8">
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider">Connection Management</h4>
        <div className="bg-sangam-800/50 rounded-xl border border-sangam-700/50 p-4">
          <pre className="text-xs text-sangam-300 overflow-x-auto">
{`# Async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    pool_size=20,           # Persistent connections
    max_overflow=10,        # Burst capacity
    echo=settings.debug,    # SQL logging in dev
)

# Session factory with auto-commit/rollback
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency injection for routes
async def get_db_session() -> AsyncSession:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise`}
          </pre>
        </div>
      </motion.div>

      {/* Migration Strategy */}
      <motion.div variants={itemVariants}>
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider">Migration Strategy</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div className="bg-sangam-800/50 rounded-lg border border-sangam-700/50 p-4">
            <p className="text-xs text-accent-emerald font-medium mb-2">Development</p>
            <p className="text-xs text-sangam-400">Auto-create tables on startup via <code className="text-sangam-300">Base.metadata.create_all</code></p>
          </div>
          <div className="bg-sangam-800/50 rounded-lg border border-sangam-700/50 p-4">
            <p className="text-xs text-accent-amber font-medium mb-2">Production</p>
            <p className="text-xs text-sangam-400">Alembic migrations: <code className="text-sangam-300">alembic upgrade head</code></p>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

/* ─── ML Panel ─── */
function MLPanel() {
  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <Brain size={20} className="text-accent-violet" />
          ML Module — Forecasting & Evaluation
        </h3>
        <p className="text-sangam-400 text-sm mb-6">
          Machine learning module for demand forecasting, model evaluation, and supply chain optimization.
          Designed as a separate service for deployment flexibility.
        </p>
      </motion.div>

      {/* Models */}
      <motion.div variants={itemVariants} className="mb-8">
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider">Forecasting Models</h4>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          <ModelCard name="ARIMA/SARIMA" desc="Statistical time-series baseline" status="planned" />
          <ModelCard name="Prophet" desc="Seasonal decomposition" status="planned" />
          <ModelCard name="XGBoost" desc="Feature-based gradient boosting" status="planned" />
          <ModelCard name="LSTM" desc="Deep learning sequences" status="planned" />
        </div>
      </motion.div>

      {/* Evaluation Metrics */}
      <motion.div variants={itemVariants} className="mb-8">
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider">Evaluation Metrics</h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <MetricCard name="MAPE" full="Mean Absolute Percentage Error" formula="mean(|actual - predicted| / actual) × 100" />
          <MetricCard name="RMSE" full="Root Mean Squared Error" formula="√mean((actual - predicted)²)" />
          <MetricCard name="MAE" full="Mean Absolute Error" formula="mean(|actual - predicted|)" />
        </div>
      </motion.div>

      {/* Interface */}
      <motion.div variants={itemVariants}>
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider">Abstract Interface</h4>
        <div className="bg-sangam-800/50 rounded-xl border border-sangam-700/50 p-4">
          <pre className="text-xs text-sangam-300 overflow-x-auto">
{`class ForecastingModel(ABC):
    """Abstract base for all forecasting models."""

    @abstractmethod
    def fit(self, data: pd.DataFrame, target: str) -> None:
        """Train on historical data."""

    @abstractmethod
    def predict(self, horizon: int) -> pd.DataFrame:
        """Generate predictions for N days."""

    @abstractmethod
    def evaluate(self, test_data: pd.DataFrame) -> dict:
        """Return performance metrics."""


class DemandForecaster:
    """Unified interface delegating to specific models."""

    def __init__(self, model_type: str = "xgboost"):
        self.model_type = model_type
        self._model: Optional[ForecastingModel] = None

    def fit(self, data, target="demand") -> None: ...
    def predict(self, horizon_days=30) -> pd.DataFrame: ...
    def get_metrics(self) -> dict: ...`}
          </pre>
        </div>
      </motion.div>
    </motion.div>
  );
}

/* ─── Docs Panel ─── */
function DocsPanel() {
  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <FileText size={20} className="text-accent-amber" />
          Documentation
        </h3>
        <p className="text-sangam-400 text-sm mb-6">
          Comprehensive documentation covering architecture, setup, and deployment.
        </p>
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <DocCard
          title="Architecture"
          file="docs/ARCHITECTURE.md"
          desc="System architecture diagram, monorepo structure, backend SOLID design, and data flow."
          topics={['Architecture diagram', 'Module boundaries', 'Request flow', 'Design principles']}
        />
        <DocCard
          title="Setup Guide"
          file="docs/SETUP.md"
          desc="Step-by-step instructions for local development environment setup."
          topics={['Prerequisites', 'Quick start', 'Database setup', 'CRLF configuration']}
        />
        <DocCard
          title="Deployment"
          file="docs/DEPLOYMENT.md"
          desc="Deployment strategies for frontend (Vercel) and API (Railway/Fly.io)."
          topics={['Vercel config', 'Docker deployment', 'Database providers', 'Limitations']}
        />
        <DocCard
          title="API Contracts"
          file="packages/contracts/README.md"
          desc="Shared TypeScript types matching backend Pydantic schemas."
          topics={['Type definitions', 'OpenAPI specs', 'Shared constants', 'Versioning']}
        />
      </motion.div>

      {/* Setup Commands */}
      <motion.div variants={itemVariants}>
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider">Quick Setup Commands</h4>
        <div className="bg-sangam-800/50 rounded-xl border border-sangam-700/50 p-4 space-y-3">
          <CommandBlock label="Install frontend" cmd="npm install" />
          <CommandBlock label="Start database" cmd="docker-compose -f infra/docker/docker-compose.yml up -d" />
          <CommandBlock label="Start API" cmd="cd apps/api && pip install -e '.[dev]' && uvicorn sangam_api.main:app --reload" />
          <CommandBlock label="Start frontend" cmd="npm run dev" />
          <CommandBlock label="Run tests" cmd="pytest tests/ && npm run typecheck" />
        </div>
      </motion.div>
    </motion.div>
  );
}

/* ─── Tests Panel ─── */
function TestsPanel() {
  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <TestTube size={20} className="text-accent-rose" />
          Testing Strategy
        </h3>
        <p className="text-sangam-400 text-sm mb-6">
          Multi-layer testing: unit tests for schemas and metrics, integration tests for API contracts.
        </p>
      </motion.div>

      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        <TestSuiteCard
          title="Unit Tests — Schemas"
          file="tests/unit/test_schemas.py"
          tests={[
            'Shipment status values validation',
            'Priority range (1-5) enforcement',
            'Weight/volume positive constraints',
            'Coordinate range validation',
            'Utilization range (0-1)',
            'Exception hierarchy status codes',
          ]}
        />
        <TestSuiteCard
          title="Unit Tests — ML Metrics"
          file="tests/unit/test_ml_evaluation.py"
          tests={[
            'MAPE zero error case',
            'MAPE percentage calculation',
            'RMSE zero error case',
            'RMSE calculation accuracy',
            'MAE zero error case',
            'Metrics handle various array sizes',
          ]}
        />
        <TestSuiteCard
          title="Integration — API Contract"
          file="tests/integration/test_api_contract.py"
          tests={[
            'Health endpoint response structure',
            'Readiness includes database status',
            'Liveness probe minimal response',
            'Shipment response field completeness',
            'Warehouse response field completeness',
            'Paginated response structure',
          ]}
        />
        <TestSuiteCard
          title="Frontend — TypeScript"
          file="npm run typecheck"
          tests={[
            'All components type-check correctly',
            'Contract types match backend schemas',
            'No implicit any types',
            'Strict mode enabled',
            'Import resolution verified',
            'Build succeeds without errors',
          ]}
        />
      </motion.div>

      {/* Test Commands */}
      <motion.div variants={itemVariants}>
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider">Test Commands</h4>
        <div className="bg-sangam-800/50 rounded-xl border border-sangam-700/50 p-4 space-y-3">
          <CommandBlock label="Frontend type check" cmd="npm run typecheck" />
          <CommandBlock label="Python unit tests" cmd="cd apps/api && pytest tests/unit/ -v" />
          <CommandBlock label="Integration tests" cmd="cd apps/api && pytest tests/integration/ -v" />
          <CommandBlock label="With coverage" cmd="cd apps/api && pytest --cov=sangam_api --cov-report=html" />
          <CommandBlock label="Full build" cmd="npm run build" />
        </div>
      </motion.div>
    </motion.div>
  );
}

/* ─── Deploy Panel ─── */
function DeployPanel() {
  return (
    <motion.div variants={containerVariants} initial="hidden" animate="visible">
      <motion.div variants={itemVariants}>
        <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
          <Globe size={20} className="text-accent-blue" />
          Deployment Configuration
        </h3>
        <p className="text-sangam-400 text-sm mb-6">
          Vercel-compatible frontend with flexible backend deployment options.
        </p>
      </motion.div>

      {/* Deployment Targets */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <DeployCard
          title="Frontend"
          platform="Vercel"
          icon={<Globe size={24} />}
          color="blue"
          details={[
            'Static SPA deployment',
            'Auto-detected Vite config',
            'SPA rewrites configured',
            'Asset caching headers',
          ]}
        />
        <DeployCard
          title="API"
          platform="Railway / Fly.io"
          icon={<Server size={24} />}
          color="emerald"
          details={[
            'Docker container deployment',
            'Persistent server process',
            'Health check configured',
            'Auto-scaling capable',
          ]}
        />
        <DeployCard
          title="Database"
          platform="Neon / Supabase"
          icon={<Database size={24} />}
          color="violet"
          details={[
            'Managed PostgreSQL 15',
            'Connection pooling built-in',
            'Serverless-compatible',
            'Auto-backups enabled',
          ]}
        />
      </motion.div>

      {/* Vercel Config */}
      <motion.div variants={itemVariants} className="mb-8">
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider">vercel.json</h4>
        <div className="bg-sangam-800/50 rounded-xl border border-sangam-700/50 p-4">
          <pre className="text-xs text-sangam-300 overflow-x-auto">
{`{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ],
  "headers": [{
    "source": "/assets/(.*)",
    "headers": [{
      "key": "Cache-Control",
      "value": "public, max-age=31536000, immutable"
    }]
  }]
}`}
          </pre>
        </div>
      </motion.div>

      {/* Limitations */}
      <motion.div variants={itemVariants}>
        <h4 className="text-sm font-semibold text-sangam-300 mb-3 uppercase tracking-wider flex items-center gap-2">
          <AlertTriangle size={16} className="text-accent-amber" />
          Deployment Limitations
        </h4>
        <div className="space-y-3">
          <LimitationCard
            title="Vercel Serverless Timeouts"
            desc="10s (Hobby) / 60s (Pro). Long-running ML jobs must use a separate service."
          />
          <LimitationCard
            title="No Persistent Filesystem"
            desc="Cannot store model artifacts on Vercel. Use object storage (S3/GCS) for ML models."
          />
          <LimitationCard
            title="Background Processes"
            desc="Serverless cannot run background workers. Use cron services or dedicated workers."
          />
          <LimitationCard
            title="Database Connections"
            desc="Each serverless invocation creates new connections. Use connection pooling (Neon/PgBouncer)."
          />
        </div>
      </motion.div>
    </motion.div>
  );
}

/* ─── Reusable Components ─── */

function ArchBlock({ title, subtitle, tech, color, icon }: {
  title: string; subtitle: string; tech: string[]; color: string; icon: React.ReactNode;
}) {
  const colorMap: Record<string, string> = {
    blue: 'border-accent-blue/30 bg-accent-blue/5',
    emerald: 'border-accent-emerald/30 bg-accent-emerald/5',
    violet: 'border-accent-violet/30 bg-accent-violet/5',
  };
  const iconColor: Record<string, string> = {
    blue: 'text-accent-blue',
    emerald: 'text-accent-emerald',
    violet: 'text-accent-violet',
  };
  return (
    <div className={`rounded-xl border p-5 ${colorMap[color]}`}>
      <div className={`${iconColor[color]} mb-3`}>{icon}</div>
      <h4 className="text-white font-semibold text-sm">{title}</h4>
      <p className="text-sangam-500 text-xs mb-3">{subtitle}</p>
      <div className="flex flex-wrap gap-1.5">
        {tech.map((t) => (
          <span key={t} className="px-2 py-0.5 rounded text-xs bg-sangam-800 text-sangam-400 border border-sangam-700/50">
            {t}
          </span>
        ))}
      </div>
    </div>
  );
}

function StatusCard({ title, status, items }: {
  title: string; status: 'complete' | 'partial' | 'planned'; items: string[];
}) {
  const statusConfig = {
    complete: { icon: <CheckCircle2 size={14} />, color: 'text-accent-emerald', bg: 'bg-accent-emerald/10' },
    partial: { icon: <AlertTriangle size={14} />, color: 'text-accent-amber', bg: 'bg-accent-amber/10' },
    planned: { icon: <Circle size={14} />, color: 'text-sangam-500', bg: 'bg-sangam-800' },
  };
  const cfg = statusConfig[status];
  return (
    <div className="rounded-xl border border-sangam-700/50 bg-sangam-800/30 p-4">
      <div className="flex items-center gap-2 mb-3">
        <span className={`${cfg.color} ${cfg.bg} p-1 rounded`}>{cfg.icon}</span>
        <h4 className="text-white text-sm font-medium">{title}</h4>
      </div>
      <ul className="space-y-1.5">
        {items.map((item) => (
          <li key={item} className="flex items-center gap-2 text-xs text-sangam-400">
            <CheckCircle2 size={12} className="text-accent-emerald/60 shrink-0" />
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function PrincipleCard({ icon, title, description }: {
  icon: React.ReactNode; title: string; description: string;
}) {
  return (
    <div className="flex gap-3 p-4 rounded-xl border border-sangam-700/50 bg-sangam-800/30">
      <div className="text-accent-amber shrink-0 mt-0.5">{icon}</div>
      <div>
        <h4 className="text-white text-sm font-medium mb-1">{title}</h4>
        <p className="text-sangam-400 text-xs leading-relaxed">{description}</p>
      </div>
    </div>
  );
}

function LayerCard({ title, color, items, files }: {
  title: string; color: string; items: string[]; files: string[];
}) {
  const colorMap: Record<string, string> = {
    blue: 'border-accent-blue/30',
    emerald: 'border-accent-emerald/30',
    violet: 'border-accent-violet/30',
    amber: 'border-accent-amber/30',
  };
  const titleColor: Record<string, string> = {
    blue: 'text-accent-blue',
    emerald: 'text-accent-emerald',
    violet: 'text-accent-violet',
    amber: 'text-accent-amber',
  };
  return (
    <div className={`rounded-xl border ${colorMap[color]} bg-sangam-800/30 p-4`}>
      <h4 className={`${titleColor[color]} text-sm font-semibold mb-3`}>{title}</h4>
      <ul className="space-y-1.5 mb-3">
        {items.map((item) => (
          <li key={item} className="flex items-start gap-2 text-xs text-sangam-300">
            <ChevronRight size={12} className="shrink-0 mt-0.5 text-sangam-500" />
            {item}
          </li>
        ))}
      </ul>
      <div className="pt-2 border-t border-sangam-700/30">
        {files.map((f) => (
          <p key={f} className="text-xs text-sangam-500 font-mono">{f}</p>
        ))}
      </div>
    </div>
  );
}

function EndpointCard({ path, method, desc }: { path: string; method: string; desc: string }) {
  return (
    <div className="bg-sangam-800/50 rounded-lg border border-sangam-700/50 p-3">
      <div className="flex items-center gap-2 mb-1">
        <span className="px-1.5 py-0.5 rounded text-xs font-mono bg-accent-emerald/10 text-accent-emerald">{method}</span>
        <code className="text-xs text-sangam-300 font-mono">{path}</code>
      </div>
      <p className="text-xs text-sangam-500">{desc}</p>
    </div>
  );
}

function TableCard({ name, columns }: { name: string; columns: { name: string; type: string }[] }) {
  return (
    <div className="bg-sangam-800/50 rounded-xl border border-sangam-700/50 overflow-hidden">
      <div className="px-4 py-2.5 bg-sangam-800 border-b border-sangam-700/50">
        <h5 className="text-sm font-mono text-accent-cyan font-semibold">{name}</h5>
      </div>
      <div className="p-3 space-y-1">
        {columns.map((col) => (
          <div key={col.name} className="flex justify-between text-xs">
            <span className="text-sangam-300 font-mono">{col.name}</span>
            <span className="text-sangam-500 font-mono">{col.type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function ModelCard({ name, desc, status }: { name: string; desc: string; status: string }) {
  return (
    <div className="bg-sangam-800/50 rounded-lg border border-sangam-700/50 p-4">
      <h5 className="text-sm font-semibold text-white mb-1">{name}</h5>
      <p className="text-xs text-sangam-400 mb-2">{desc}</p>
      <span className="px-2 py-0.5 rounded text-xs bg-accent-violet/10 text-accent-violet border border-accent-violet/20">
        {status}
      </span>
    </div>
  );
}

function MetricCard({ name, full, formula }: { name: string; full: string; formula: string }) {
  return (
    <div className="bg-sangam-800/50 rounded-lg border border-sangam-700/50 p-4">
      <h5 className="text-sm font-bold text-accent-violet mb-1">{name}</h5>
      <p className="text-xs text-sangam-400 mb-2">{full}</p>
      <code className="text-xs text-sangam-300 font-mono bg-sangam-900 px-2 py-1 rounded block">{formula}</code>
    </div>
  );
}

function DocCard({ title, file, desc, topics }: { title: string; file: string; desc: string; topics: string[] }) {
  return (
    <div className="bg-sangam-800/50 rounded-xl border border-sangam-700/50 p-5">
      <div className="flex items-start justify-between mb-2">
        <h4 className="text-white font-semibold text-sm">{title}</h4>
        <ExternalLink size={14} className="text-sangam-500 shrink-0" />
      </div>
      <p className="text-xs text-sangam-500 font-mono mb-2">{file}</p>
      <p className="text-xs text-sangam-400 mb-3">{desc}</p>
      <div className="flex flex-wrap gap-1.5">
        {topics.map((t) => (
          <span key={t} className="px-2 py-0.5 rounded text-xs bg-sangam-800 text-sangam-400 border border-sangam-700/50">
            {t}
          </span>
        ))}
      </div>
    </div>
  );
}

function CommandBlock({ label, cmd }: { label: string; cmd: string }) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-xs text-sangam-500 w-36 shrink-0">{label}</span>
      <code className="flex-1 text-xs text-accent-cyan font-mono bg-sangam-900 px-3 py-2 rounded-lg border border-sangam-700/30">
        $ {cmd}
      </code>
    </div>
  );
}

function TestSuiteCard({ title, file, tests }: { title: string; file: string; tests: string[] }) {
  return (
    <div className="bg-sangam-800/50 rounded-xl border border-sangam-700/50 p-4">
      <h4 className="text-white text-sm font-semibold mb-1">{title}</h4>
      <p className="text-xs text-sangam-500 font-mono mb-3">{file}</p>
      <ul className="space-y-1.5">
        {tests.map((t) => (
          <li key={t} className="flex items-center gap-2 text-xs text-sangam-400">
            <div className="w-4 h-4 rounded border border-accent-emerald/30 flex items-center justify-center">
              <CheckCircle2 size={10} className="text-accent-emerald" />
            </div>
            {t}
          </li>
        ))}
      </ul>
    </div>
  );
}

function DeployCard({ title, platform, icon, color, details }: {
  title: string; platform: string; icon: React.ReactNode; color: string; details: string[];
}) {
  const colorMap: Record<string, string> = {
    blue: 'border-accent-blue/30',
    emerald: 'border-accent-emerald/30',
    violet: 'border-accent-violet/30',
  };
  const iconColor: Record<string, string> = {
    blue: 'text-accent-blue',
    emerald: 'text-accent-emerald',
    violet: 'text-accent-violet',
  };
  return (
    <div className={`rounded-xl border ${colorMap[color]} bg-sangam-800/30 p-5`}>
      <div className={`${iconColor[color]} mb-3`}>{icon}</div>
      <h4 className="text-white font-semibold text-sm">{title}</h4>
      <p className="text-sangam-500 text-xs mb-3">{platform}</p>
      <ul className="space-y-1.5">
        {details.map((d) => (
          <li key={d} className="flex items-center gap-2 text-xs text-sangam-400">
            <CheckCircle2 size={12} className="text-accent-emerald/60" />
            {d}
          </li>
        ))}
      </ul>
    </div>
  );
}

function LimitationCard({ title, desc }: { title: string; desc: string }) {
  return (
    <div className="flex gap-3 p-3 rounded-lg border border-accent-amber/20 bg-accent-amber/5">
      <AlertTriangle size={16} className="text-accent-amber shrink-0 mt-0.5" />
      <div>
        <h5 className="text-sm font-medium text-sangam-200">{title}</h5>
        <p className="text-xs text-sangam-400">{desc}</p>
      </div>
    </div>
  );
}
