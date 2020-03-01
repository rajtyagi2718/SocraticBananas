
from fractions import Fraction
import locale
locale.setlocale(locale.LC_NUMERIC, 'en_US.utf8')
import unicodedata

def ner_model(ingred):
    """Return (quant, unit, name, comment) from trained model."""
    return None

## Quant ##

QUANT = set()

CAST = {float: ValueError, Fraction: ValueError,
        unicodedata.numeric: TypeError, locale.atof: ValueError}

def is_quant(word):
    for cast, error in CAST.items():
        try:
            cast(word)
            return True
        except error:
            pass
    if len(word) > 1:  # '1½'
        try:
            unicodedata.numeric(word)
            return is_quant(word[:-1])
        except CAST[unicodedata.numeric]:
            pass
    return word in QUANT

## Unit ##

UNIT = set()

METRIC = ['gram', 'kilogram', 'milligram', 'liter', 'milliliter']
IMPERIAL = ['pound', 'ounce', 'cup', 'pint', 'quart', 'gallon', 'fluid_ounce',
            'tablespoon', 'teaspoon',]
SIZE = ['extra_small', 'small', 'medium', 'large', 'extra_large']
PORTION = ['part', 'whole']

LINKS = {'gram': ['grams', 'g'], 'kilogram': ['kilograms', 'kg', 'kgs'],
         'milligram': ['milligrams', 'mg', 'mgs'], 'liter': ['liters', 'l', 'litre', 'litres'], 'milliliter': ['']}



def unit_hist(word):
    return int(word in unit_hist)

def unit_metric(word):
    pass
