# Recommendations Module - Quick Start Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Backend and frontend running

## 1. Setup Backend

### Install Dependencies

```bash
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
```

### Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and ensure database is configured:
```bash
DATABASE_URL=postgresql+asyncpg://sangam:sangam@localhost:5432/sangam
```

### Start Database

```bash
# Using Docker
docker-compose -f infra/docker/docker-compose.yml up -d postgres

# Or use existing PostgreSQL
```

### Seed Database

```bash
python -m sangam_api.scripts.seed
```

### Start API Server

```bash
uvicorn sangam_api.main:app --reload --port 8000
```

API will be available at: http://localhost:8000

## 2. Setup Frontend

```bash
# From project root
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

## 3. Access Recommendations

### Login

Open http://localhost:3000 in your browser.

**Demo Credentials:**
- Email: `admin@sangam.dev`
- Password: `admin123!`

### Navigate to Recommendations

After login, navigate to: http://localhost:3000/recommendations

Or click "Recommendations" in the navigation menu.

## 4. Generate Recommendations

### Via UI

1. Go to Recommendations page
2. Click "Generate Recommendations" button
3. Wait for generation to complete (5-15 seconds)
4. View generated recommendations

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/recommendations/generate \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 5. Review Recommendations

### View List

- See all recommendations in the left panel
- Filter by status (Pending, Approved, Rejected, Completed)
- Filter by type (Stock Transfer, Replenishment, etc.)
- View statistics at the top

### View Details

1. Click on a recommendation in the list
2. View full details in the right panel:
   - Title and description
   - Rationale (why this recommendation was made)
   - Suggested action
   - Supporting data
   - Assumptions
   - Estimated impact
   - Confidence score

## 6. Approve Recommendations

### Via UI

1. Select a pending recommendation
2. Click "Approve" button
3. Add optional notes
4. Recommendation status changes to "Approved"

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/recommendations/{id}/approve \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Approved for immediate execution"}'
```

## 7. Reject Recommendations

### Via UI

1. Select a pending recommendation
2. Click "Reject" button
3. Enter rejection reason (required)
4. Click "Reject" to confirm
5. Recommendation status changes to "Rejected"

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/recommendations/{id}/reject \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Not feasible due to budget constraints"}'
```

## 8. Execute Recommendations

### Via UI

1. Select an approved recommendation
2. Click "Execute" button
3. Recommendation status changes to "Completed"
4. View execution result (simulated)

### Via API

```bash
curl -X POST http://localhost:8000/api/v1/recommendations/{id}/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Executed via API"}'
```

## 9. View Statistics

### Dashboard

The statistics section shows:
- Total recommendations
- Pending count
- Approved count
- Completed count
- Status distribution (pie chart)
- Priority distribution (bar chart)
- Average confidence score

### Via API

```bash
curl http://localhost:8000/api/v1/recommendations/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 10. View Audit Logs

### Via API

```bash
curl http://localhost:8000/api/v1/recommendations/{id}/audit-logs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "items": [
    {
      "id": "uuid",
      "action": "approved",
      "previous_status": "pending",
      "new_status": "approved",
      "user_name": "John Doe",
      "notes": "Approved for immediate execution",
      "created_at": "2024-01-15T11:00:00Z"
    }
  ],
  "total": 3
}
```

## 11. Common Workflows

### Workflow 1: Stock Transfer

1. **Generate**: System detects low stock at Mumbai, excess at Delhi
2. **Review**: "Transfer 500 units from Delhi to Mumbai"
3. **Approve**: Manager approves the transfer
4. **Execute**: System simulates creating shipment
5. **Result**: Stock transfer initiated (simulated)

### Workflow 2: Replenishment

1. **Generate**: System detects stock approaching reorder point
2. **Review**: "Order 300 units of Laptops"
3. **Approve**: Procurement manager approves
4. **Execute**: System simulates placing purchase order
5. **Result**: Purchase order created (simulated)

### Workflow 3: Route Change

1. **Generate**: System detects delayed shipment
2. **Review**: "Reroute via faster alternative"
3. **Approve**: Logistics manager approves
4. **Execute**: System simulates reassigning route
5. **Result**: Route changed (simulated)

## 12. Testing Scenarios

### Scenario 1: High-Priority Recommendation

```bash
# Generate recommendations
curl -X POST http://localhost:8000/api/v1/recommendations/generate \
  -H "Authorization: Bearer YOUR_TOKEN"

# List pending recommendations
curl "http://localhost:8000/api/v1/recommendations/pending?priority_threshold=2" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Approve high-priority recommendation
curl -X POST http://localhost:8000/api/v1/recommendations/{id}/approve \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Urgent approval"}'
```

### Scenario 2: Reject with Reason

```bash
# Reject a recommendation
curl -X POST http://localhost:8000/api/v1/recommendations/{id}/reject \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Budget not available this quarter"}'
```

### Scenario 3: Execute and Verify

```bash
# Execute approved recommendation
curl -X POST http://localhost:8000/api/v1/recommendations/{id}/execute \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Executed successfully"}'

# Verify status changed to completed
curl http://localhost:8000/api/v1/recommendations/{id} \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check audit logs
curl http://localhost:8000/api/v1/recommendations/{id}/audit-logs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 13. Filtering Examples

### Filter by Status

```bash
# Get only pending recommendations
curl "http://localhost:8000/api/v1/recommendations?status=pending" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get only approved recommendations
curl "http://localhost:8000/api/v1/recommendations?status=approved" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Type

```bash
# Get only stock transfer recommendations
curl "http://localhost:8000/api/v1/recommendations?recommendation_type=stock_transfer" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get only replenishment recommendations
curl "http://localhost:8000/api/v1/recommendations?recommendation_type=replenishment" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Priority

```bash
# Get only critical priority (1) recommendations
curl "http://localhost:8000/api/v1/recommendations?priority=1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get high and critical priority (1-2)
curl "http://localhost:8000/api/v1/recommendations/pending?priority_threshold=2" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Filter by Depot

```bash
# Get recommendations for specific depot
curl "http://localhost:8000/api/v1/recommendations?affected_depot_id={depot_uuid}" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 14. Maintenance Operations

### Cleanup Expired Recommendations

```bash
curl -X POST http://localhost:8000/api/v1/recommendations/maintenance/cleanup-expired \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### List Available Strategies

```bash
curl http://localhost:8000/api/v1/recommendations/strategies \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 15. Troubleshooting

### No Recommendations Generated

**Check:**
- Services are initialized (inventory, forecast, shipment, route)
- Data exists in the system
- Check API logs for errors
- Verify strategies are registered

### Approval Fails

**Check:**
- Recommendation is in 'pending' status
- Recommendation is not expired
- User has proper permissions
- Check API response for error details

### Execution Fails

**Check:**
- Recommendation is in 'approved' status
- User has execute permissions
- Check API response for error details

### UI Not Loading

**Check:**
- Frontend is running (`npm run dev`)
- API is accessible
- Browser console for errors
- Network tab for failed requests

## 16. Best Practices

### For Reviewers

1. **Read Rationale**: Understand why the recommendation was made
2. **Check Data**: Verify supporting data is accurate
3. **Review Assumptions**: Ensure assumptions are valid
4. **Consider Impact**: Evaluate estimated impact
5. **Document Decision**: Add clear notes for approval/rejection

### For Executors

1. **Verify Approval**: Ensure recommendation is approved
2. **Review Details**: Understand the suggested action
3. **Add Notes**: Document execution details
4. **Track Results**: Update with actual outcomes

### For Administrators

1. **Monitor Metrics**: Track approval rates and execution times
2. **Review Rejections**: Understand why recommendations are rejected
3. **Clean Up**: Regularly cleanup expired recommendations
4. **Audit Logs**: Review audit trail for compliance

## 17. API Documentation

Full API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 18. Additional Resources

- **Full Documentation**: `docs/RECOMMENDATIONS_MODULE.md`
- **Implementation Details**: `RECOMMENDATIONS_IMPLEMENTATION.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Tests**: `apps/api/tests/unit/test_recommendations.py`

---

**You're all set!** 🎉

The Recommendations system is ready to use with AI-driven suggestions, approval workflows, and comprehensive tracking.
