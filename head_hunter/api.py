from typing import Dict

import requests
import settings
import urllib.parse

from itertools import count


def calculate_vacancies_processed(vacation: Dict):

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


def load_all_vacations(url, params: Dict[str, str]):
    for page in count(start=0, step=1):
        params['page'] = page
        resp = requests.get(url, params=params)
        resp.raise_for_status()

        json_object = resp.json()

        if page == json_object['pages']:
            break

        yield from json_object['items']


def retrieve_vacation_info_by_language(
        language: str,
        area: str = '2',
        currency: str = 'RUR',
        only_with_salary: bool = False) -> Dict[str, str]:
    url = urllib.parse.urljoin(settings.HH_BASE_URL, 'vacancies')
    params = {
        'area': area,
        'currency': currency,
        'only_with_salary': only_with_salary,
        'text': language,
    }
    resp = requests.get(url, params=params)

    resp.raise_for_status()

    json_object = resp.json()

    vacancies_found = json_object['found']
    all_vacancies = load_all_vacations('https://api.hh.ru/vacancies', params=params)
    vacancies_processed = 0
    average_salary = 0
    for vacation in all_vacancies:
        vacancies_processed += calculate_vacancies_processed(vacation)
        average_salary += predict_rub_salary(vacation)

    return {language: {'vacancies_found': vacancies_found,
            'vacancies_processed': vacancies_processed,
            'average_salary': int(average_salary / vacancies_processed)}}


if __name__ == '__main__':
    for language in settings.PROGRAM_LANGUAGE:
        job_info = retrieve_vacation_info_by_language(language=language)
        print(job_info)
