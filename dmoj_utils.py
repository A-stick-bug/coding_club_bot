def balance(questions, ac):
    """applies formula to points based on question values"""
    bal = sorted(questions.values(), reverse=True)  # sort by point worth
    P = sum((0.95 ** i) * bal[i] for i in range(0, min(100, len(bal))))
    B = 150 * (1 - 0.997 ** len(ac))
    return P + B


def balance_full_acs(questions):
    """
    Applies formula to points based on question values.
    Only considers full ACs"""
    bal = sorted(questions, reverse=True)  # sort by point worth
    P = sum((0.95 ** i) * bal[i] for i in range(0, min(100, len(bal))))
    return P
