import pytest
from gyomu.configurator import Configurator
from gyomu.milestone import MilestoneAccess
from datetime import date


class TestMilestoneAccess:
    def test_milestone(self, status_handler_setup):
        config: Configurator = status_handler_setup
        today = date.today()
        milestone_id = "TEST_MILESTONE"
        assert not MilestoneAccess.exists(milestone_id, target_date=today)
        assert not MilestoneAccess.wait(milestone_id, target_date=today, timeout_minutes=1)
        MilestoneAccess.register(milestone_id, target_date=today)
        assert MilestoneAccess.exists(milestone_id, target_date=today)
        assert MilestoneAccess.wait(milestone_id, target_date=today, timeout_minutes=1)
        MilestoneAccess.unregister(milestone_id, target_date=today)
        assert not MilestoneAccess.exists(milestone_id, target_date=today)

    def test_monthly_milestone(self,status_handler_setup):
        config: Configurator = status_handler_setup
        today = date.today()
        milestone_id = "MONTHLY_TEST_MILESTONE"
        assert not MilestoneAccess.exists(milestone_id, target_date=today, is_monthly=True)
        MilestoneAccess.register(milestone_id, target_date=today, is_monthly=True)
        assert MilestoneAccess.exists(milestone_id, target_date=today, is_monthly=True)
        MilestoneAccess.unregister(milestone_id, target_date=today, is_monthly=True)
        assert not MilestoneAccess.exists(milestone_id, target_date=today, is_monthly=True)
