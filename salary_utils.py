from typing import Dict


def predict_rub_salary(vacation: Dict, vacation_type) -> int:
    salary_from = None
    salary_to = None
    if vacation_type == 'head_hunter':
        salary = vacation['salary']
        if not salary:
            return 0
        salary_from, salary_to = salary['from'], salary['to']
    elif vacation_type == 'super_job':
        salary_from = vacation['payment_from']
        salary_to = vacation['payment_to']
    if not salary_from and not salary_to:
        return 0
    elif all([salary_from, salary_to]):
        return (salary_from + salary_to) / 2
    elif not salary_from:
        return salary_to * 0.8
    elif not salary_to:
        return salary_from * 1.2
