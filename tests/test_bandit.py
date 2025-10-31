from backend.services.exec.bandit import ContextualBandit


def test_bandit_prefers_best_arm():
    bandit = ContextualBandit([0.03, 0.05], [1.0], [10], epsilon=0.0)
    arm = bandit.arms[0]
    arm.successes = 10
    arm.trials = 11
    choice = bandit.select()
    assert choice is arm
