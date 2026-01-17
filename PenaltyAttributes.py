from __future__ import annotations


class PenaltyAttributes:
    def __init__(self, assignment_penalty_coefficient: int, delivery_penalty_coefficient: int, customer_importance_penalty_coefficient: int):
        self.apc = assignment_penalty_coefficient
        self.dpc = delivery_penalty_coefficient
        self.cipc = customer_importance_penalty_coefficient

    @staticmethod
    def variant_1() -> PenaltyAttributes:
        return PenaltyAttributes(1, 2, 1)

    @staticmethod
    def variant_2() -> PenaltyAttributes:
        return PenaltyAttributes(3, 4, 2)
