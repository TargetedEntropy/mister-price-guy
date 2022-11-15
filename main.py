from sqlalchemy.event import listen
import db.config as config
from db.config import session
import asyncio
import argparse
import requests
import json
import time

from db.tables.recipe_table import recipe
from db.schema.recipe_scema import Recipe
from db.tables.item_table import item
from db.schema.item_schema import Item


from os import environ, path
from dotenv import load_dotenv

# Load configuration values from the .env file
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

api_key = environ.get("API_KEY")

parser = argparse.ArgumentParser()
parser.add_argument("--update_recipe", help="Update the recipe database", action="store_true")
parser.add_argument("--player_materials", help="Update player material list", action="store_true")

args = parser.parse_args()
parser.parse_args()



async def startup():
    await config.database.connect()

async def check_if_recipe_exists(id: str) -> bool:
    return session.query(Recipe).filter(Recipe.id == id).first()

async def check_if_item_exists(id: str) -> bool:
    return session.query(Item).filter(Item.id == id).all()

async def insert_recipe(recipe: str) -> None:
    recipe_data = Recipe(
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
    session.add(recipe_data)
    session.commit()

async def insert_item(item: str) -> None:
    item_data = Item(
        id = item['id'],
        description = item['description'],
        type = item['type'],
        level = item['level'],
        rarity = item['rarity'],
        vendor_value = item['vendor_value'],
        game_types = json.dumps(item['game_types']),
        flags = json.dumps(item['flags']),
        restrictions = json.dumps(item['restrictions']),
        chat_link = item['chat_link'],
        icon = item['icon']

    )
    session.add(item_data)
    session.commit()


async def update_recipes():
    # recipe_ids = await get_all_recipes()
    recipe_ids = await get_gw_api("recipes")
    for recipe_id in recipe_ids:
        recipe_data = await check_if_recipe_exists(recipe_id)
        
        
        if recipe_data == None:
            recipe_data = await get_gw_api_item("recipes", recipe_id)
            await insert_recipe(recipe_data)

    
            output_item_id = recipe_data['output_item_id']
            
        else:
            output_item_id = recipe_data.output_item_id
        
            
            
        
        item_data = await check_if_item_exists(output_item_id)


        if item_data == []:
            item_data = await get_gw_api_item("items", output_item_id)

            if 'text' in item_data:
                print(f"Failed, recipe_id: {recipe_id}, recipe_data: {recipe_data}")
            else:
                # print(f"Adding item: {item_data}")
                await insert_item(item_data)
            
        # time.sleep(0.5)
        # break


async def update_player_materials():
    player_materials = await get_gw_api("account/materials", api_key)
    player_info = await get_gw_api("account", api_key)
    print(player_info)
    #print(player_materials)


async def get_gw_api(endpoint, api_key = None):
    if api_key:
        headers = {"Authorization": f"Bearer {api_key}"}
    else:
        headers = None
   
    try:
        response = requests.get(f"https://api.guildwars2.com/v2/{endpoint}", headers=headers)
    except Exception as error:
        print(f"Failed to get gw_api, error: {error}")
        
    return response.json()

async def get_gw_api_item(endpoint:str, id: str):
    try:
        response = requests.get(f"https://api.guildwars2.com/v2/{endpoint}/{id}")
    except Exception as error:
        print(f"Failed to get get_api_item, {id}, error: {error}")
        
    return response.json()




async def main():
    # Connect to DB
    await startup()
    
    if args.update_recipe:
        print("Updating Recipes")    
        await update_recipes()
        
    if args.player_materials:
        print("Updating Player Materials")    
        await update_player_materials()        
    
    print("done")



loop = asyncio.get_event_loop()
asyncio.ensure_future(main())
loop.run_forever()
loop.close()


if __name__ == '__main__':
    main()