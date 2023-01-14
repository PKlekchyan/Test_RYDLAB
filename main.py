from odoo_client import OdooClient
from character_source import CharacterSourceImpl
from logger import Logger
from tqdm import tqdm
import configparser
import argparse


def main(path):
    print('----------')
    print('Main was started....')
    print('----------')

    # Получение данных конфига
    config = configparser.ConfigParser()
    config.read(path)

    url_odoo = config.get('Setting', 'url_odoo')
    db = config.get('Setting', 'db')
    username = config.get('Setting', 'username')
    password = config.get('Setting', 'password')

    # 1 Получаем все планеты
    character_source = CharacterSourceImpl()
    planets = character_source.get_planets()

    # 2 Получаем всех персонажей
    characters = character_source.get_characters()

    # # 3 Загружаем все планеты в Odoo
    print('POST Planets....')
    client = OdooClient(url_odoo, db, username, password)
    planets_id = {}
    for planet in tqdm(planets):
        params = [{'name': planet.name, 'diameter': planet.diameter, 'population': planet.population, 'rotation_period': planet.rotation_period, 'orbital_period': planet.orbital_period}]
        planet_odoo_id = client.create_record('res.planet', params)
        planets_id[planet.name] = planet_odoo_id
        if planet_odoo_id is not None:
            Logger().log_success('res.planet', planet.name, planet.id, planet_odoo_id)
    print('POST Planets -- DONE')

    # 4 Загружаем всех персонажей в Odoo
    print('POST Characters....')
    for character in tqdm(characters):
        params = {'name': character.name}
        if character.image != "":
            params['image_1920'] = character.image
        if character.planet_name != "":
            params['planet'] = planets_id[character.planet_name]

        character_id_odoo = client.create_record('res.partner', [params])

        if character_id_odoo is not None:
            Logger().log_success('res.partner', character.name, character.id, character_id_odoo)

    print('POST Characters -- DONE')
    print('----------')
    print('Main was DONE')


def create_parser():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('path', nargs='?')
    return arg_parser


if __name__ == '__main__':
    parser = create_parser()
    namespace = parser.parse_args()

    if namespace.path:
        main(namespace.path)
    else:
        print('Path is obligatory param to start program')
