
import requests

RECIPE_URLS = [
'https://www.allrecipes.com/recipe/21014/good-old-fashioned-pancakes/?internalSource=hub%20recipe&referringId=78&referringContentType=Recipe%20Hub',
'https://www.allrecipes.com/recipe/7985/blueberry-buckle/?internalSource=previously%20viewed&referringContentType=Homepage',
'https://www.allrecipes.com/recipe/222342/sweet-and-sour-pork-tenderloin/?internalSource=streams&referringId=695&referringContentType=Recipe%20Hub&clickId=st_recipes_mades',
'https://www.allrecipes.com/recipe/277917/slow-cooker-cheesy-cauliflower-casserole/?internalSource=streams&referringId=253&referringContentType=Recipe%20Hub&clickId=st_recipes_mades']

def get_responses():
    """Return response object for urls in RECIPE_URLS."""
    for url in RECIPE_URLS:
        response = requests.get(url)
        if response.status_code == 200:  # page was downloaded
            yield response
