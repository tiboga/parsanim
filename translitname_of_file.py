dict_of_letters = {"а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo", "ж": "zh", "з": "z", "и": "i",
                   "й": "j", "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t",
                   "у": "u", "ф": "f", "х": "kh", "ц": "cz", "ч": "ch", "ш": "sh", "щ": "shh", "ы": "y", "э": "e",
                   "ю": "yu", "я": "ya"}


def translit(word):
    out = ''
    for elem in word:
        if elem.lower() in dict_of_letters.keys():
            out += dict_of_letters[elem.lower()]
        elif elem.isdigit() or elem in ['(', ')']:
            out += elem
        elif elem in [',', '.', '?', '!', ' ']:
            out += '_'
        elif elem.isalpha():
            out += elem

    return out.capitalize()
