import functools
import urllib.parse
from itertools import count
from typing import Dict, Union

import requests

import settings
from salary_utils import predict_rub_salary


def calculate_vacancies_processed(vacation: Dict) -> int:
    salary = vacation['salary']
    if not salary:
        return 0
    if any([salary['from'], salary['to']]):
        return 1


def load_all_vacations(url, params: Dict[str, Union[str, int]]):
    for page in count(start=1, step=1):
        params['page'] = page
        resp = requests.get(url, params=params)
        resp.raise_for_status()

        hh_vacancies = resp.json()

        yield from hh_vacancies['items']
        if page == hh_vacancies['pages']:
            break


def retrieve_vacancies_statistic_by_language(
        programming_language: str,
        area: str = '2',
        currency: str = 'RUR',
        only_with_salary: bool = False) -> Dict[str, Dict]:
    url = urllib.parse.urljoin(settings.HH_BASE_URL, 'vacancies')
    params = {
        'area': area,
        'currency': currency,
        'only_with_salary': only_with_salary,
        'text': programming_language,
    }
    resp = requests.get(url, params=params)

    resp.raise_for_status()

    hh_vacancies = resp.json()

    found_vacancies = hh_vacancies['found']
    all_vacancies = load_all_vacations(url,
                                       params=params)
    processed_vacancies = sum(
        list(map(calculate_vacancies_processed, hh_vacancies['items'])))
    predicted_salary = sum(
        list(map(
            functools.partial(predict_rub_salary, vacation_type='head_hunter'),
            hh_vacancies['items'])))
    for vacation in all_vacancies:
        processed_vacancies += calculate_vacancies_processed(vacation)
        predicted_salary += predict_rub_salary(vacation,
                                               vacation_type='head_hunter')

    avg_salary = int(predicted_salary /
                     processed_vacancies) if processed_vacancies else 0
    return {
        programming_language:
            {'vacancies_found': found_vacancies,
             'vacancies_processed': processed_vacancies,
             'average_salary': avg_salary}}


if __name__ == '__main__':
    for language in settings.PROGRAM_LANGUAGES:
        job_info = retrieve_vacancies_statistic_by_language(
            programming_language=language)
        print(job_info)
