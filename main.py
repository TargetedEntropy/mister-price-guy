from sqlalchemy.event import listen
import db.config as config
from db.config import session
import asyncio
import argparse
import requests
import json

parser = argparse.ArgumentParser()
parser.add_argument("--update_recipe", help="Update the recipe database", action="store_true")
args = parser.parse_args()



parser.parse_args()


from db.tables.recipe_table import recipe
from db.schema.recipe_scema import Recipe
from db.tables.item_table import item
from db.schema.item_schema import Item


async def startup():
    await config.database.connect()

async def check_if_recipe_exists(id: str) -> bool:
    result = session.query(Recipe).filter(Recipe.id == id).all()
    if result == []:
        return False
    else:
        return True
    

async def check_if_item_exists(id: str) -> bool:
    result = session.query(Item).filter(Item.id == id).all()
    if result == []:
        return False
    else:
        return True    

async def insert_recipe(recipe: str) -> None:
    recipe = Recipe(
        id = recipe['id'],
        type = recipe['type'],
        output_item_id = recipe['output_item_id'],
        output_item_count = recipe['output_item_count'],
        time_to_craft_ms = recipe['time_to_craft_ms'],
        disciplines = json.dumps(recipe['disciplines']),
        min_rating = recipe['min_rating'],
        flags = json.dumps(recipe['flags']),
        ingredients = json.dumps(recipe['ingredients']),
        chat_link = recipe['chat_link'],
        guild_ingredients = json.dumps(recipe['guild_ingredients'])
    )
    session.add(recipe)
    session.commit()


async def update_recipes():
    recipe_ids = await get_all_recipes()
    for recipe_id in recipe_ids:
        check = await check_if_recipe_exists(recipe_id)
        if not check:
            recipe_data = await get_recipe(recipe_id)
            await insert_recipe(recipe_data)
        

async def get_all_recipes():
    try:
        total_recipes_req = requests.get("https://api.guildwars2.com/v2/recipes")
    except Exception as error:
        print(f"Failed to get Recipes")
        
    return total_recipes_req.json()

async def get_recipe(id: str):
    try:
        total_recipes_req = requests.get(f"https://api.guildwars2.com/v2/recipes/{id}")
    except Exception as error:
        print(f"Failed to get Recipe, {id}, error: {error}")
        
    return total_recipes_req.json()


async def main():
    # Connect to DB
    await startup()
    
    if args.update_recipe:
        print("Updating Recipes")    
        await update_recipes()
    
    print("running")



loop = asyncio.get_event_loop()
asyncio.ensure_future(main())
loop.run_forever()
loop.close()


if __name__ == '__main__':
    main()