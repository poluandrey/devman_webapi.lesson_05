import urllib.parse
from itertools import count
from typing import Dict, List

import requests

import settings


def predict_rub_salary(vacation: Dict):
    payment_from = vacation['payment_from']
    payment_to = vacation['payment_to']

    if all([payment_from, payment_to]):
        return (payment_from + payment_to) / 2
    elif payment_to:
        return payment_to * 1.2
    elif payment_from:
        return payment_from * 0.8
    return None


def load_all_vacations(url: str, params: Dict, headers: Dict):
    for page in count(start=0, step=1):
        params['page'] = page

        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()

        json_object = resp.json()
        if not json_object['more']:
            break

        yield from json_object['objects']


def retrieve_vacations_by_language(programming_language: str,
                                   town: str = '4',
                                   catalogues: str = '48',
                                   where2search: str = '1') -> Dict:
    """
    :param programming_language:
    :param town:
    :param catalogues:
    :param where2search: 1 -job title, 2 - company name, 3 - official duties
    :return: vist of vacations
    """
    keywords: List[Dict[str, str]] = [{'srws': where2search},
                                      {'keys': programming_language}]

    headers = {'X-Api-App-Id': settings.SJ_SECRET_KEY}
    params = {'town': town,
              'catalogues': catalogues,
              }
    for id, param in enumerate(keywords):
        for key, value in param.items():
            params[f'keywords[{id}][{key}]'] = value
    base_url = settings.SJ_BASE_URL
    url = urllib.parse.urljoin(base_url, 'vacancies')

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()

    vacancies_found = resp.json()['total']
    vacancies = load_all_vacations(url, params=params, headers=headers)
    average_salary = 0
    vacancies_processed = 0
    for vacation in vacancies:
        salary = predict_rub_salary(vacation)
        if salary:
            average_salary += salary
            vacancies_processed += 1

    language_info = {programming_language: {
        'vacancies_found': vacancies_found,
        'vacancies_processed': vacancies_processed}}
    language_info[programming_language]['average_salary'] = int(
        average_salary / vacancies_processed
    ) if vacancies_processed != 0 else 0
    return language_info


if __name__ == '__main__':
    for language in settings.PROGRAM_LANGUAGES:
        language_info = retrieve_vacations_by_language(programming_language=language)
        print(language_info)
