"""
Tests for AI Employee data models.

Validates serialization, deserialization, and business logic
for ActionItem, ApprovalRequest, Plan, and other models.

Usage:
    python -m pytest tests/test_models.py -v
    python tests/test_models.py  # standalone
"""

import sys
from pathlib import Path
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.action_item import ActionItem
from models.approval_request import ApprovalRequest
from models.plan import Plan, PlanStep
from models.log_entry import LogEntry, AuditEntry
from models.service_state import ServiceState, ServiceStatus


class TestActionItem:
    """Tests for ActionItem model."""

    def test_create_action_item(self):
        item = ActionItem(
            filepath=Path('/tmp/test.md'),
            item_type='email',
            priority='high',
            metadata={'from': 'test@example.com'},
            body='Test email body',
            source='gmail'
        )
        assert item.item_type == 'email'
        assert item.priority == 'high'
        assert item.source == 'gmail'
        assert item.status == 'pending'

    def test_sensitive_detection_financial(self):
        item = ActionItem(
            filepath=Path('/tmp/invoice.md'),
            item_type='file_drop',
            priority='medium',
            body='Please process this invoice for $5000'
        )
        assert item.is_sensitive() is True

    def test_sensitive_detection_payment(self):
        item = ActionItem(
            filepath=Path('/tmp/payment.md'),
            item_type='payment',
            priority='high',
            body='Payment request'
        )
        assert item.is_sensitive() is True

    def test_not_sensitive(self):
        item = ActionItem(
            filepath=Path('/tmp/info.md'),
            item_type='general',
            priority='low',
            body='Just an informational message'
        )
        assert item.is_sensitive() is False

    def test_serialization_roundtrip(self):
        item = ActionItem(
            filepath=Path('/tmp/test.md'),
            item_type='email',
            priority='high',
            metadata={'subject': 'Test'},
            body='Test body',
            source='gmail'
        )
        data = item.to_dict()
        restored = ActionItem.from_dict(data)
        assert restored.item_type == item.item_type
        assert restored.priority == item.priority
        assert str(restored.filepath) == str(item.filepath)

    def test_filename_property(self):
        item = ActionItem(
            filepath=Path('/vault/Needs_Action/EMAIL_20260208.md'),
            item_type='email',
            priority='medium'
        )
        assert item.filename == 'EMAIL_20260208.md'


class TestApprovalRequest:
    """Tests for ApprovalRequest model."""

    def test_create_request(self):
        req = ApprovalRequest(
            request_id='APR-001',
            action_type='send_email',
            description='Reply to client inquiry',
            parameters={'to': 'client@example.com', 'subject': 'Re: Inquiry'},
            risk_level='medium'
        )
        assert req.status == 'pending'
        assert req.risk_level == 'medium'

    def test_to_markdown(self):
        req = ApprovalRequest(
            request_id='APR-002',
            action_type='create_invoice',
            description='Create invoice for Acme Corp',
            parameters={'customer': 'Acme Corp', 'amount': '$1500'},
            risk_level='high',
            estimated_cost=1500.0
        )
        md = req.to_markdown()
        assert '# Approval Request:' in md
        assert 'create_invoice' in md
        assert 'Acme Corp' in md
        assert '$1500.00' in md
        assert 'Move this file to `/Approved/`' in md


class TestPlan:
    """Tests for Plan model."""

    def test_create_plan_with_steps(self):
        plan = Plan(
            plan_id='PLAN-001',
            title='Process client email',
            source_item='EMAIL_20260208.md',
            item_type='email',
            summary='Reply to client with requested info',
            steps=[
                PlanStep(step_number=1, description='Draft reply', action_type='auto', tool='draft_email'),
                PlanStep(step_number=2, description='Send email', action_type='approval_required', tool='send_email'),
            ]
        )
        assert len(plan.steps) == 2
        assert plan.completion_percentage == 0.0

    def test_completion_tracking(self):
        plan = Plan(
            plan_id='PLAN-002',
            title='Test plan',
            source_item='test.md',
            item_type='general',
            steps=[
                PlanStep(step_number=1, description='Step 1', action_type='auto', completed=True),
                PlanStep(step_number=2, description='Step 2', action_type='auto', completed=False),
            ]
        )
        assert plan.completion_percentage == 50.0

    def test_to_markdown(self):
        plan = Plan(
            plan_id='PLAN-003',
            title='Test plan',
            source_item='test.md',
            item_type='general',
            summary='A test plan',
            steps=[
                PlanStep(step_number=1, description='Do thing', action_type='auto', tool='send_email'),
            ]
        )
        md = plan.to_markdown()
        assert '# Plan: Test plan' in md
        assert 'send_email' in md


class TestAuditEntry:
    """Tests for AuditEntry model."""

    def test_create_and_serialize(self):
        entry = AuditEntry(
            action_type='email_send',
            actor='claude_code',
            domain='gmail',
            target='client@example.com',
            parameters={'subject': 'Invoice'},
            approval_status='approved',
            approved_by='human',
            result='success'
        )
        data = entry.to_dict()
        assert data['action_type'] == 'email_send'
        assert data['actor'] == 'claude_code'
        assert 'error' not in data

    def test_error_included_when_present(self):
        entry = AuditEntry(
            action_type='email_send',
            actor='claude_code',
            result='failure',
            error_detail='Connection timeout'
        )
        data = entry.to_dict()
        assert data['error'] == 'Connection timeout'

    def test_roundtrip(self):
        entry = AuditEntry(
            action_type='payment',
            actor='orchestrator',
            domain='odoo',
            target='INV-001',
            result='success'
        )
        data = entry.to_dict()
        restored = AuditEntry.from_dict(data)
        assert restored.action_type == entry.action_type
        assert restored.domain == entry.domain


class TestServiceState:
    """Tests for ServiceState model."""

    def test_initial_healthy(self):
        state = ServiceState(name='gmail')
        assert state.status == ServiceStatus.HEALTHY
        assert state.is_available is True

    def test_degradation_on_failures(self):
        state = ServiceState(name='gmail', degraded_threshold=2, unavailable_threshold=5)
        state.record_failure('timeout')
        assert state.status == ServiceStatus.HEALTHY
        state.record_failure('timeout')
        assert state.status == ServiceStatus.DEGRADED
        assert state.is_available is True

    def test_unavailable_on_many_failures(self):
        state = ServiceState(name='gmail', degraded_threshold=2, unavailable_threshold=3)
        state.record_failure('err1')
        state.record_failure('err2')
        state.record_failure('err3')
        assert state.status == ServiceStatus.UNAVAILABLE
        assert state.is_available is False

    def test_recovery_on_success(self):
        state = ServiceState(name='gmail', degraded_threshold=2, unavailable_threshold=5)
        state.record_failure('err1')
        state.record_failure('err2')
        assert state.status == ServiceStatus.DEGRADED
        state.record_success()
        assert state.status == ServiceStatus.HEALTHY


# Standalone runner
if __name__ == '__main__':
    import traceback

    test_classes = [
        TestActionItem, TestApprovalRequest, TestPlan,
        TestAuditEntry, TestServiceState
    ]

    total = 0
    passed = 0
    failed = 0

    for cls in test_classes:
        instance = cls()
        methods = [m for m in dir(instance) if m.startswith('test_')]
        for method_name in methods:
            total += 1
            try:
                getattr(instance, method_name)()
                passed += 1
                print(f"  [PASS] {cls.__name__}.{method_name}")
            except Exception as e:
                failed += 1
                print(f"  [FAIL] {cls.__name__}.{method_name}: {e}")
                traceback.print_exc()

    print(f"\nResults: {passed}/{total} passed, {failed} failed")
    sys.exit(1 if failed > 0 else 0)
