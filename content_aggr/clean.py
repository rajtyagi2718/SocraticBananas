
## define UNITS
## ascii mixed fraction instead of float for unit
## special unit for
##     2 12-inch tortillas -> 24 inch tortillas
##     vs 2 12-ounce cans soup ->

import re
from numpy import NaN

import locale
locale.setlocale(locale.LC_NUMERIC, 'en_US.utf8')
from fractions import Fraction
import unicodedata

# UNITS =

RE_LETTERS = re.compile('[a-zA-Z]')

def split_ingredients(ingred):
    """Return triplet of strs (quantity, unit of measurement, food item)."""
    match = RE_LETTERS.search(ingred)
    if match is None:
        return None  # failed extraction, no letters in str
    i = match.start()
    quant, ingred = ingred[:i], ingred[i:]

    try:
        unit, food = ingred.split(maxsplit=1)
    except ValueError:  # single word
        unit = ''
        food = ingred

    return (x.strip() for x in (quant, unit, food))

RE_SUBNUMBERS = re.compile('^[\(]*|[\)\.]*$')

def strip_quant(quant):
    """Remove parentheses, trailing periods from quantity str."""
    if quant and quant[0] in ('(', '['):
        qaunt = quant[1:]
    if quant and quant[-1] in (')', ']', '.'):
        qaunt = quant[:-1]
    return quant

def clean_quant(quant):
    """Return float from quantity str.

    cases: '' '½' '1½' '1 1½' '1/2' '1 1/2' '1,200'
    """
    quant = re.sub(RE_SUBNUMBERS, '', quant)
    splt = quant.split(maxsplit=1)
    if len(splt) == 2:
        if splt[1][0] == '(':  # 1 (10, ounce), can of soup
            return clean_quant(splt[0]) * clean_quant(splt[1][1:])
        return clean_quant(splt[0]) + clean_quant(splt[1])  # 1 1/2

    try:
        num = float(quant)
    except ValueError:
        try:
            num = locale.atof(quant)  # '1,200'
        except ValueError:
            try:
                num = float(Fraction(quant))  # '1/2'
            except ValueError:
                try:
                    num = unicodedata.numeric(quant)  # '½'
                except TypeError: # can't parse: unexpected or ''
                    num = NaN

    if num is NaN:
        print("quant not parsed -->%s<--" % quant)
    return num

RE_SUBLETTERS = re.compile('^[^a-zA-Z]*|[^a-zA-Z]*$')

def clean_unit(unit):
    unit = re.sub(RE_SUBLETTERS, '', unit)
    unit = re.sub('s$', '', unit)
    return unit

def clean_food(food):
    return food

def clean_ingredients(ingred):
    q,u,f = split_ingredients(ingred)
    # if u not in UNITS:
    #     u = ''
    #     f = u + ' ' + f
    return (clean_quant(q), clean_unit(u), clean_food(f))
