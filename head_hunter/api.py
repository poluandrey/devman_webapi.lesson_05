import urllib.parse
from itertools import count
from typing import Dict, Union

import requests

import settings


def calculate_vacancies_processed(vacation: Dict) -> int:
    salary = vacation['salary']
    if not salary:
        return 0
    if any([salary['from'], salary['to']]):
        return 1


def predict_rub_salary(vacation: Dict) -> int:
    salary = vacation['salary']
    if not salary:
        return 0
    salary_from, salary_to = salary['from'], salary['to']

    if all([salary_from, salary_to]):
        return (salary_from + salary_to) / 2
    elif not salary_from:
        return salary_to * 0.8
    elif not salary_to:
        return salary_from * 1.2


def load_all_vacations(url, params: Dict[str, Union[str, int]]):
    for page in count(start=1, step=1):
        params['page'] = page
        resp = requests.get(url, params=params)
        resp.raise_for_status()

        json_object = resp.json()

        if page == json_object['pages']:
            break

        yield from json_object['items']


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

    json_object = resp.json()

    vacancies_found = json_object['found']
    all_vacancies = load_all_vacations(url,
                                       params=params)
    vacancies_processed = sum(
        list(map(calculate_vacancies_processed,  json_object['items'])))
    predicted_salary = sum(
        list(map(predict_rub_salary,  json_object['items'])))
    for vacation in all_vacancies:
        vacancies_processed += calculate_vacancies_processed(vacation)
        predicted_salary += predict_rub_salary(vacation)
    if vacancies_processed == 0:
        vacancies_processed = 1
    avg_salary = int(predicted_salary /
                     vacancies_processed) if vacancies_processed != 0 else 0
    return {
        programming_language:
            {'vacancies_found': vacancies_found,
             'vacancies_processed': vacancies_processed,
             # zero division check
             'average_salary': avg_salary}}


if __name__ == '__main__':
    for language in settings.PROGRAM_LANGUAGES:
        job_info = retrieve_vacancies_statistic_by_language(
            programming_language=language)
        print(job_info)
