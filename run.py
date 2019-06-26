from measurements import Measurements
from languagetools import LanguageTools
from tester import Tester


tester = Tester()
run = True
while run:
    random_recipe = tester.get_random_recipe()
    if random_recipe:
        if 'ingredients' in random_recipe:
            if len(random_recipe['ingredients']) > 0:
                for ingredient in random_recipe['ingredients']:
                    print(ingredient)
                    tagged = LanguageTools.tag_words(ingredient)
                    extracted = Measurements.extract_measurements(tagged)
                    print('tagged: ', tagged)
                    print('extracted', extracted)
                    print('done')
                user_input = input("press 1 to contiune or 0 to break... ")
                if user_input == 0:
                    run = False
                    break


