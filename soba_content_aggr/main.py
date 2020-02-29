
import spacy
nlp = spacy.load('en')

from scrape import get_responses
from parse import get_ingredients
from clean import clean_ingredients

def main():
    for response in get_responses():
        print(response.url)
        for ingred in get_ingredients(response):
            print(repr(ingred))
            doc = nlp(ingred.strip())
            ent = [(i,i.label_,i.label) for i in doc.ents]
            print(ent)
            ingred_data = clean_ingredients(ingred)
            print(ingred_data)
            print()
        print('\n'*2)


if __name__ == '__main__':
    main()
