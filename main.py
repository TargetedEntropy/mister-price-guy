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

from db.tables.materials_table import material
from db.schema.material_schema import Material

from db.schema.known_recipe_schema import KnownRecipe
from db.tables.known_recipe_table import known_recipe

from os import environ, path
from dotenv import load_dotenv

# Load configuration values from the .env file
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

api_key = environ.get("API_KEY")

parser = argparse.ArgumentParser()
parser.add_argument(
    "--update_recipe",
    help="Update the recipe database",
    action="store_true")
parser.add_argument(
    "--player_materials",
    help="Update player material list",
    action="store_true")
parser.add_argument(
    "--check_recipes",
    help="Check what Recipes we can make",
    action="store_true")


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
        id=recipe['id'],
        type=recipe['type'],
        output_item_id=recipe['output_item_id'],
        output_item_count=recipe['output_item_count'],
        time_to_craft_ms=recipe['time_to_craft_ms'],
        disciplines=json.dumps(recipe['disciplines']),
        min_rating=recipe['min_rating'],
        flags=json.dumps(recipe['flags']),
        ingredients=json.dumps(recipe['ingredients']),
        chat_link=recipe['chat_link'],
        guild_ingredients=json.dumps(recipe['guild_ingredients'])
    )
    session.add(recipe_data)
   # session.commit()


async def insert_item(item: str) -> None:
    
    try:
        
        if hasattr(item, 'description'):
            desc = item['description']
        else:
            desc = None
        
        item_data = Item(
            id=item['id'],
            description=desc,
            type=item['type'],
            level=item['level'],
            rarity=item['rarity'],
            vendor_value=item['vendor_value'],
            game_types=json.dumps(item['game_types']),
            flags=json.dumps(item['flags']),
            restrictions=json.dumps(item['restrictions']),
            chat_link=item['chat_link'],
            icon=item['icon']

        )
        session.add(item_data)
       # session.commit()        
    except Exception as error:
        print(f"Unable to create Item object, error: {error}")
        



async def update_recipes():
    # recipe_ids = await get_all_recipes()
    recipe_ids = await get_gw_api("recipes")
    
    count = 0
    for recipe_id in recipe_ids:
        recipe_data = await check_if_recipe_exists(recipe_id)

        if recipe_data is None:
            recipe_data = await get_gw_api_item("recipes", recipe_id)
            await insert_recipe(recipe_data)

            output_item_id = recipe_data['output_item_id']

        else:
            output_item_id = recipe_data.output_item_id

        item_data = await check_if_item_exists(output_item_id)

        if item_data == []:
            item_data = await get_gw_api_item("items", output_item_id)

            if 'text' in item_data:
                print(
                    f"Failed, recipe_id: {recipe_id}, recipe_data: {recipe_data}")
            else:
                await insert_item(item_data)

        count = count + 1
        if count == 100:
            session.commit()
            count = 0

async def update_player_materials():
    player_materials = await get_gw_api("account/materials", api_key)
    player_info = await get_gw_api("account", api_key)
    session.query(Material).filter(
        Material.player_id == player_info['id']).delete()
    session.commit()
    
    for player_material in player_materials:
        material = Material(
            item_id = player_material['id'],
            player_id = player_info['id'],
            category = player_material['category'],
            count = player_material['count']
        )
        session.add(material)
    session.commit()

    print("Player materials updated")
    
async def update_known_recipes():
    known_recipes = await get_gw_api("account/recipes", api_key)
    player_info = await get_gw_api("account", api_key)
    session.query(KnownRecipe).filter(
        KnownRecipe.player_id == player_info['id']).delete()
    session.commit()
    
    for known_recipe in known_recipes:
        recipe = KnownRecipe(
            item_id = known_recipe,
            player_id = player_info['id'],
        )
        session.add(recipe)
    session.commit()

    print("Player Known recipes updated")    

async def get_gw_api(endpoint, api_key=None):
    if api_key:
        headers = {"Authorization": f"Bearer {api_key}"}
    else:
        headers = None

    try:
        response = requests.get(
            f"https://api.guildwars2.com/v2/{endpoint}",
            headers=headers)
    except Exception as error:
        print(f"Failed to get gw_api, error: {error}")

    return response.json()


async def get_gw_api_item(endpoint: str, id: str):
    try:
        response = requests.get(
            f"https://api.guildwars2.com/v2/{endpoint}/{id}")
    except Exception as error:
        print(f"Failed to get get_api_item, {id}, error: {error}")


    return response.json()

async def get_player_materials(player_id: str):
    item_list = []
    player_materials = session.query(Material).filter(Material.player_id == '').all()
    for player_material in player_materials:
        item_list.append(player_material.item_id)
    return item_list

async def get_item_name(item_id: int):
    req = requests.get(f"https://api.guildwars2.com/v2/items/{item_id}")
    return req.json()['name']
    

async def get_item_price(item_id: int):
    req = requests.get(f"https://api.guildwars2.com/v2/commerce/prices/{item_id}")
    return req.json()

top_price = 0
top_price_item = 0

from pprint import pprint
async def check_recipes():
    recipes = session.query(Recipe).all()
    player_materials = await get_player_materials('')
    print(f"count:{len(recipes)}")
    for recipe in recipes:
        if 'Chef' in recipe.disciplines: # and recipe.flags == ["AutoLearned"]:
            ingredient_len = len(json.loads(recipe.ingredients))
            ingredient_check = 0
            for ingredient in json.loads(recipe.ingredients):
                if ingredient['item_id'] in player_materials:
                    ingredient_check = ingredient_check + 1
            if ingredient_len == ingredient_check:
                item_price = await get_item_price(recipe.output_item_id)

                try:
                    real_price = item_price['buys']['unit_price']
                    print(f"{real_price} {recipe.output_item_id}") 
                    if real_price > top_price:
                        top_price_item = recipe.output_item_id
                except Exception as error:
                    pass
            #break
    
    item_name = await get_item_name(top_price_item)
    print(f"Top Price Item: {item_name} / {top_price_item}")
#            break
        
        # 
        
async def main():
    # Connect to DB
    await startup()

    if args.update_recipe:
        print("Updating Recipes")
        await update_recipes()

    if args.player_materials:
        print("Updating Player Materials")
        await update_player_materials()
        await update_known_recipes()
        
    if args.check_recipes:
        print("Magic")
        await check_recipes()

    print("done")


loop = asyncio.get_event_loop()
asyncio.ensure_future(main())
loop.run_forever()
loop.close()


if __name__ == '__main__':
    main()
