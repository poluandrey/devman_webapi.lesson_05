from terminaltables import AsciiTable

import settings
from head_hunter import api as hh_api
from super_job import api as sj_api


def main():
    sj_table = [
        ['language', 'vacations found', 'vacations processed', 'average salary'],
    ]
    for language in settings.PROGRAM_LANGUAGES:
        sj_vacations_info = sj_api.retrieve_vacation_info_by_language(language=language)
        info = sj_vacations_info[language]
        sj_row = [language,
                  info['vacancies_found'],
                  info['vacancies_processed'],
                  info['average_salary']]
        sj_table.append(sj_row)
    table = AsciiTable(sj_table, title='SuperJob')
    print(table.table)

    hh_table = [
        ['language', 'vacations found', 'vacations processed', 'average salary'],
    ]
    for language in settings.PROGRAM_LANGUAGES:
        sj_vacations_info = hh_api.retrieve_vacation_info_by_language(language=language)
        info = sj_vacations_info[language]
        sj_row = [language,
                  info['vacancies_found'],
                  info['vacancies_processed'],
                  info['average_salary']]
        hh_table.append(sj_row)
    table = AsciiTable(hh_table, title='SuperJob')
    print(table.table)


if __name__ == '__main__':
    main()
