
from scrape import get_responses
from parse import get_ingredients
from clean import clean_ingredients

def main():
    for response in get_responses():
        print(response.url)
        for ingred in get_ingredients(response):
            ingred_data = clean_ingredients(ingred)
            print(ingred_data)
        print()


if __name__ == '__main__':
    main()
