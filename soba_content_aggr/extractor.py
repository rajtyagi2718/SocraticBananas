
## define UNITS
## ascii mixed fraction instead of float for unit
## special unit for
##     2 12-inch tortillas
##     2 12-ounce cans soup

## Preamble ##

import re
from fractions import Fraction
import locale
locale.setlocale(locale.LC_NUMERIC, 'en_US.utf8')
import unicodedata

from ner_model.ner_model import ner_model

## Ingredient ##

def extract_ingredient(ingred):
    """Return quantity, unit, food name, food comment from ingredient str."""
    try:
        quant, unit, name, comment = ner_rb(ingred)
    except TypeError:  # failed rule-based extraction
        try:
            quant, unit, name, comment = ner_model(ingred)
        except TypeError:  # failed statistical model extraction
            return None

def ner_rb(ingred):
    try:
        quant, unit, food = split_ingredients(ingred)
        quant = clean_quant(quant)
        unit = clean_unit(unit)
        name, comment = ner_rb_food(food)
    except TypeError:
        try:
            quant, unit, name, comment = ner_model_ingredient(ingred)
        except TypeError:
            return (None,)*4
    return quant, unit, name, comment

def tokenize_ingredient(ingred):
    pass

RE_LETTERS = re.compile('[a-zA-Z]')

def split_ingredients(ingred):
    """Return triplet of strs (quantity, unit, food phrase)."""
    match = RE_LETTERS.search(ingred)
    if match is None:
        return None  # failed, no letters in str
    i = match.start()
    quant, ingred = ingred[:i], ingred[i:]

    try:
        unit, food = ingred.split(maxsplit=1)
    except ValueError:  # single word
        unit = ''
        food = ingred

    # compound units: 3 (1/2 pound fillets)  ->  3 (1/2, pound, fillets)
    #                 3 1/2-pound fillets  ->  3 1/2-, pound, fillets
    if unit and quant:
        if quant[-1] == '-':
            try:  # 3 1/2-
                num, unit1 = quant.split(maxsplit=1)
                unit = unit1 + unit
            except TypeError:  # 3-pound fillet
                quant = '1'
        elif '(' in quant:
            num, unit1 =  quant.split('(')
            if unit1[-1] != '-':
                unit1 += '-'
            unit = unit1 + unit
        
    return (x.strip() for x in (quant, unit, food))


## Quantity ##

RE_SUBNUMBERS = re.compile('^[\(]*|[\)\.]*$')

def clean_quant(quant):
    """Return float %.3f from quantity str.

    cases: '' '½' '1½' '1 ½' '1/2' '1 1/2' '1,200'
    """
    quant = re.sub(RE_SUBNUMBERS, '', quant)
    splt = quant.split(maxsplit=1)
    if len(splt) == 2:
        if splt[1][0] == '(':
            # 1 (10, ounce), can of soup
            # 3 6 inch corn tortillas
            # 2	Six inch sprigs of basil (leaves attached)
            return clean_quant(splt[0]) * clean_quant(splt[1][1:])
        return clean_quant(splt[0]) + clean_quant(splt[1])  # 1 1/2
    # if len(qu)

    try:
        num = float(quant)
    except ValueError:
        try:
            num = locale.atof(quant)  # '1,200'
        except ValueError:
            try:
                num = float(Fraction(quant))  # '1/2'
            except ValueError:
                if quant:
                    try:
                        num = unicodedata.numeric(quant[-1])  # '½'
                    except TypeError: # can't parse: unexpected
                        num = None
                    if len(quant) > 1 and num is not None:  # '1½'
                        num += clean_quant(quant[:-1])
                else:
                    num = None

    if num is None:
        print("quant not parsed -->%s<--" % quant)
    return round(num, 3)


## Unit ##

RE_SUBLETTERS = re.compile('^[^a-zA-Z]*|[^a-zA-Z]*$')

def clean_unit(unit):
    unit = re.sub(RE_SUBLETTERS, '', unit)
    unit = re.sub('s$', '', unit)
    return unit


## Name ##

def clean_food(food):
    return food

def clean_ingredients(ingred):
    q,u,f = split_ingredients(ingred)
    # if u not in UNITS:
    #     u = ''
    #     f = u + ' ' + f
    return (clean_quant(q), clean_unit(u), clean_food(f))
