class PenaltyAttributes:
    def __init__(self, assignment_penalty_coefficient, delivery_penalty_coefficient, customer_importance_penalty_coefficient):
        self.apc = assignment_penalty_coefficient
        self.dpc = delivery_penalty_coefficient
        self.cipc = customer_importance_penalty_coefficient

    @staticmethod
    def variant_1():
        return PenaltyAttributes(1, 2, 1)

    @staticmethod
    def variant_2():
        return PenaltyAttributes(3, 4, 2)
