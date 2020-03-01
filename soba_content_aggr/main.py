
import spacy
nlp = spacy.load('en')

from scraper import get_responses
from parser import get_ingredients
from extractor import extract_ingredient

def main():
    for response in get_responses():
        print(response.url)
        for ingred in get_ingredients(response):
            print(repr(ingred))
            # doc = nlp(ingred.strip())
            # ent = [(i,i.label_,i.label) for i in doc.ents]
            # print(ent)
            # ingred_data = extract_ingredient(ingred)
            # print(ingred_data)
            print()
        print('\n'*2)


if __name__ == '__main__':
    main()
