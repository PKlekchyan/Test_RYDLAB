from abc import ABC, abstractmethod
import requests
from logger import Logger
from models import *
from threading import Thread
import base64
from time import time
from tqdm import tqdm


class CharacterSource(ABC):
    @abstractmethod
    def get_characters(self):
        pass

    @abstractmethod
    def get_planets(self):
        pass


class CharacterSourceImpl(CharacterSource):
    swapi_base_url = "https://swapi.dev/api/"
    swapi_people_endpoint = swapi_base_url + "people/"
    swapi_planet_endpoint = swapi_base_url + "planets/"
    star_wars_visual_guide_characters_endpoint = "https://starwars-visualguide.com/assets/img/characters/"

    def get_characters(self):
        print('GET Characters....')
        page = 1
        json_characters = []
        next_exist = True
        try:
            while next_exist:
                start = time()
                params = {"page": page}
                characters_response = requests.get(self.swapi_people_endpoint, params)
                if characters_response.status_code != 200:
                    error_message = " | ".join([str(characters_response.url), str(characters_response.status_code)])
                    Logger().log_error(str(self.__class__.__name__), 'get_characters', error_message)
                else:
                    json_characters += characters_response.json()["results"]
                    next_exist = characters_response.json()["next"] is not None
                print(page, 'page finished. Time: ', round(time()-start, 2), "sec")
                page += 1

        except requests.RequestException as ex:
            Logger().log_error(str(self.__class__.__name__), 'get_characters', str(ex))
        except KeyError as ex:
            Logger().log_error(str(self.__class__.__name__), 'get_characters', str(ex))

        characters = []

        def append_characters(json_character):
            character = self.__get_character(json_character)
            if character is not None:
                characters.append(character)

        self.__split_on_threads(append_characters, json_characters)
        print('GET Characters -- DONE')
        return characters

    def get_planets(self):
        print('GET Planets....')
        page = 1
        json_planets = []
        next_exist = True
        try:
            while next_exist:
                start = time()
                params = {"page": page}
                planets_response = requests.get(self.swapi_planet_endpoint, params)
                if planets_response.status_code != 200:
                    error_message = " | ".join([str(planets_response.url), str(planets_response.status_code)])
                    Logger().log_error(str(self.__class__.__name__), 'get_planets', error_message)
                else:
                    json_planets += planets_response.json()["results"]
                    next_exist = planets_response.json()["next"] is not None
                print(page, 'page finished. Time:', round(time()-start, 2), "sec")
                page += 1

        except requests.RequestException as ex:
            Logger().log_error(str(self.__class__.__name__), 'get_planets', str(ex))
        except KeyError as ex:
            Logger().log_error(str(self.__class__.__name__), 'get_planets', str(ex))

        planets = []

        def append_planets(json_planet):
            try:
                planet_name = self.__smart_cast(json_planet['name'], str)
                planet_rotation_period = self.__smart_cast(json_planet['rotation_period'], int)
                planet_orbital_period = self.__smart_cast(json_planet['orbital_period'], int)
                planet_diameter = self.__smart_cast(json_planet['diameter'], int)
                planet_population = self.__smart_cast(json_planet['population'], str)
                planet_id = json_planet['url'].strip(' /').split('/')[-1]

                planets.append(Planet(planet_id, planet_name, planet_diameter, planet_population,
                                      planet_rotation_period, planet_orbital_period))
            except KeyError as ex:
                Logger().log_error(str(self.__class__.__name__), 'append_planets', str(ex))

        self.__split_on_threads(append_planets, json_planets)
        print('GET Planets -- DONE')
        return planets

    def __get_character(self, json_character) -> Character | None:
        try:
            character_name = json_character["name"]
            planet_url = json_character["homeworld"]
            character_url_str = str(json_character["url"])
            character_id = character_url_str.strip(' /').split('/')[-1]
            planet_name = self.__get_planet_name(planet_url)
            image_code = self.__get_image(character_id)
            return Character(character_id, character_name, planet_name, image_code)
        except KeyError as ex:
            Logger().log_error(str(self.__class__.__name__), '__get_character', str(ex))
            return None

    def __get_planet_name(self, url) -> str:
        try:
            planet_response = requests.get(url)
            if planet_response.status_code != 200:
                error_message = " | ".join([str(planet_response.url), str(planet_response.status_code)])
                Logger().log_error(str(self.__class__.__name__), '__get_planet_name', error_message)
                return ""
            else:
                return planet_response.json()["name"]
        except requests.RequestException as ex:
            Logger().log_error(str(self.__class__.__name__), '__get_planet_name', str(ex))
            return ""

    def __get_image(self, character_id) -> str:
        try:
            pictures_response = requests.get(
                self.star_wars_visual_guide_characters_endpoint + str(character_id) + ".jpg")
            if pictures_response.status_code != 200:
                error_message = " | ".join([str(pictures_response.url), str(pictures_response.status_code)])
                Logger().log_error(str(self.__class__.__name__), '__get_image', error_message)
                return ""
            else:
                image = str(base64.b64encode(pictures_response.content))[2:]
                return image
        except requests.RequestException as ex:
            Logger().log_error(str(self.__class__.__name__), '__get_image', str(ex))
            return ""

    def __split_on_threads(self, func, data_list):
        idx = 0
        pbar = tqdm(total=len(data_list))
        while idx < len(data_list):
            part_of_data = data_list[idx:idx + 4]
            idx += 4
            threads = []
            for item in part_of_data:
                thread = Thread(target=func, args=(item,))
                thread.start()
                threads.append(thread)
            for thread in threads:
                thread.join()
            pbar.update(len(threads))
        pbar.close()

    def __smart_cast(self, value, type) -> type:
        try:
            return type(value)
        except ValueError:
            return type()
        except TypeError:
            return type()
