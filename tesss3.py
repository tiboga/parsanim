year = int(input())
dict_of_year = {2000: 'Дракон', 2001: 'Змея', 2002: 'Лошадь', 2003: 'Коза', 2004: 'Обезьяна', 2005: 'Петух',
                2006: 'Собака', 2007: 'Свинья', 2008: 'Крыса', 2009: 'Бык', 2010: 'Тигр', 2011: 'Кролик'}
if year > 2011:
    k = round((year - 2000) / 12)
    print(dict_of_year[year - 12 * k])
elif year < 2000:
    k = round((2000 - year) / 12) + 1
    print(dict_of_year[year + 12 * k])
else:
    print(dict_of_year[year])
