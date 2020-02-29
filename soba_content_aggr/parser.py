
from bs4 import BeautifulSoup

def get_soup(response):
    """Parse response for html content. Return BeautifulSoup object."""
    return BeautifulSoup(response.content, "html.parser")

INGRED_CLASSES = ("recipe-ingred_txt added", "ingredients-item-name")

def get_ingred(soup):
    """Return generator of ingredient strs from soup object."""
    for cls_ in INGRED_CLASSES:
        ingred = soup.find_all(class_=cls_)
        if not ingred:
            continue
        break
    return (ing.get_text() for ing in ingred)

def get_ingredients(response):
    """Return generator of ingredient strs from response object."""
    return get_ingred(get_soup(response))
