from typing import Callable, List

from terminaltables import AsciiTable

import settings
from head_hunter import api as hh_api
from super_job import api as sj_api


def create_table(languages: List, func: Callable, title: str):
    table = [
        ['language',
         'vacations found',
         'vacations processed',
         'average salary'],
    ]

    for language in languages:
        vacations = func(language)
        data_by_language = vacations[language]
        row = [language,
               data_by_language['vacancies_found'],
               data_by_language['vacancies_processed'],
               data_by_language['average_salary']]
        table.append(row)
    table = AsciiTable(table, title=title)
    return table


def main():
    languages = settings.PROGRAM_LANGUAGES
    sj_table = create_table(languages=languages,
                            func=sj_api.retrieve_vacations_by_language,
                            title='SuperJob')
    print(sj_table.table)
    hh_table = create_table(languages=languages,
                            func=hh_api.retrieve_vacation_info_by_language,
                            title='HeadHunter')
    print(hh_table.table)


if __name__ == '__main__':
    main()
