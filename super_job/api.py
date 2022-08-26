import functools
import urllib.parse
from itertools import count
from typing import Dict, List

import requests

import settings
from salary_utils import predict_rub_salary


def load_all_vacancies(url: str, params: Dict, headers: Dict):
    for page in count(start=1, step=1):
        params['page'] = page

        resp = requests.get(url, params=params, headers=headers)
        resp.raise_for_status()

        sj_vacancies = resp.json()

        yield from sj_vacancies['objects']
        if not sj_vacancies['more']:
            break


def retrieve_vacancies_statistic_by_language(programming_language: str,
                                             town: str = '4',
                                             catalogues: str = '48',
                                             where2search: str = '1') -> Dict:
    """
    :param programming_language: language for which statistic will be collect
    :param town: where to find vacations
    :param catalogues: type of vacancies
    :param where2search: 1 -job title, 2 - company name, 3 - official duties
    :return: vist of vacations
    """
    keywords: List[Dict[str, str]] = [{'srws': where2search},
                                      {'keys': programming_language}]

    headers = {'X-Api-App-Id': settings.SJ_SECRET_KEY}
    params = {'town': town,
              'catalogues': catalogues,
              }
    for pk, param in enumerate(keywords):
        for key, value in param.items():
            params[f'keywords[{pk}][{key}]'] = value
    base_url = settings.SJ_BASE_URL
    url = urllib.parse.urljoin(base_url, 'vacancies')

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()

    sj_vacancies = resp.json()
    found_vacancies = sj_vacancies['total']

    predicted_salaries = list(
        map(functools.partial(predict_rub_salary, vacation_type='super_job'),
            sj_vacancies['objects']))
    predicted_salary = sum(predicted_salaries)
    processed_vacancies = sum(map(lambda x: not x, predicted_salaries))

    vacancies = load_all_vacancies(url, params=params, headers=headers)

    for vacancy in vacancies:
        salary = predict_rub_salary(vacation=vacancy,
                                    vacation_type='super_job')
        if salary:
            predicted_salary += salary
            processed_vacancies += 1

    avg_salary = int(
        predicted_salary / processed_vacancies
    ) if processed_vacancies else 0

    language_statistic = {programming_language: {
        'vacancies_found': found_vacancies,
        'vacancies_processed': processed_vacancies},
        'average_salary': avg_salary
    }

    return language_statistic


if __name__ == '__main__':
    for language in settings.PROGRAM_LANGUAGES:
        language_statistic = retrieve_vacancies_statistic_by_language(
            programming_language=language)
        print(language_statistic)
