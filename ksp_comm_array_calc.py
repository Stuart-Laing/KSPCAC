import argparse
import math
import json
import re
import sympy
from sys import argv
from typing import Optional
from copy import copy
import textwrap


GAME_DATA_FILE_PATH = "gamedata.json"
GRAVITATIONAL_CONSTANT = 6.6743e-11


class CelestialBody:
    def __init__(self, name: str, body_data: dict):
        self.name: str = name

        self.radius: int = body_data["radius"]
        self.mass: int = body_data["mass"]
        self.sphere_of_influence: int = body_data["sphere of influence"]
        self.parent_body: str = body_data["parent body"]
        self.standard_grav_const: float = self.mass * GRAVITATIONAL_CONSTANT

    def __repr__(self):
        return f"CelestialBody({self.name=}, {self.radius=}, {self.mass=}, " \
               f"{self.sphere_of_influence=}, {self.parent_body=}, {self.standard_grav_const=})"

    def calculate_orbital_period(self, periapsis: int, apoapsis: int) -> int:
        avg_radius = (periapsis + apoapsis + self.radius * 2) / 2
        return int(round(2 * math.pi * math.sqrt(math.pow(avg_radius, 3) / self.standard_grav_const)))

    def calculate_periapsis_with_apoapsis_and_period(self, apoapsis, period: int):
        avg_radius = int(round(math.pow((period * math.sqrt(self.standard_grav_const)) /
                                        (2 * math.pi), 0.666666666666)))
        return (2 * avg_radius) - apoapsis - self.radius * 2

    def calculate_orbit_radius_with_period(self, period: int):
        return int(round(math.pow((period * math.sqrt(self.standard_grav_const)) /
                                  (2 * math.pi), 0.666666666666))) - self.radius

    def calculate_delta_v_for_hohmann_transfer(self, start_radius: int, end_radius: int) -> int:
        r1 = start_radius + self.radius
        r2 = end_radius + self.radius

        return int(round(math.sqrt(self.standard_grav_const / r1) * (math.sqrt((2 * r2) / (r1 + r2)) - 1)))


class CommPart:
    def __init__(self, full_name: str, part_data: dict, quantity: int = None):
        self.full_name: str = full_name

        self.alias: str = part_data["alias"]
        self.power: int = part_data["power"]
        self.combinable: bool = part_data["combinable"]
        self.combinability_exponent: float = part_data["combinability exponent"]
        self.relay: bool = part_data["relay"]
        self.quantity: Optional[int] = quantity

    def add_quantity(self, quantity: int):
        self.quantity = quantity

    def __repr__(self):
        return f"CommPart({self.full_name=}, {self.alias=}, {self.power=}," \
               f" {self.combinable=}, {self.combinability_exponent=}, {self.relay=}, {self.quantity=})"


class GameData:
    def __init__(self, game_data_dict: dict):
        self.bodies: dict[str, CelestialBody] = {body: CelestialBody(body, data)
                                                 for body, data in game_data_dict["bodies"].items()}

        self.comm_parts: dict[str, CommPart] = {part: CommPart(part, data)
                                                for part, data in game_data_dict["communication parts"].items()}

    def __repr__(self):
        return f"GameData({self.bodies=}, {self.comm_parts=})"

    def verify_body(self, body: str) -> bool:
        return body.lower() in map(lambda x: x.lower(), self.bodies.keys())

    def verify_comm_part(self, part_alias: str) -> bool:
        return part_alias in map(lambda part: part.alias, self.comm_parts.values())

    def get_part_name_from_alias(self, alias: str) -> str:
        for part_name, part_data in self.comm_parts.items():
            if part_data.alias == alias:
                return part_name

    def get_comm_part(self, part_name: str) -> CommPart:
        return copy(self.comm_parts[part_name])

    def get_celestial_body(self, body_name: str) -> CelestialBody:
        lower_bodies = {k.lower(): v for k, v in self.bodies.items()}

        return copy(lower_bodies[body_name.lower()])


class ShowOptions(argparse.Action):
    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, help=None):
        argparse.Action.__init__(self, option_strings=option_strings, dest=dest, default=default, nargs=0, help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        game_data = read_game_data(GAME_DATA_FILE_PATH)
        print("Available celestial bodies:")
        sorted_body_list: list[tuple[str, CelestialBody]] = \
            sorted(game_data.bodies.items(), key=lambda x: (x[1].parent_body, x[1].name))

        system_map = {body[1].name: ["", 0, body[1].parent_body] for body in sorted_body_list}
        for index, part in enumerate(sorted_body_list):
            new_root = part[1].parent_body
            indent = "  "
            while True:
                if new_root == "":
                    break
                system_map[new_root][1] += 1
                indent += "  "
                new_root = game_data.bodies[new_root].parent_body

            system_map[part[1].name][0] = indent

        new_system_map = self.recursive_system_sorter("", 0, len(system_map) - 1, system_map)

        for row in new_system_map:
            print(row)

        print("\nAvailable communication parts:")
        available_comm_part_matrix = [["Full Part Name", "Alias"]]
        sorted_comm_list: list[tuple[str, CommPart]] = \
            sorted(game_data.comm_parts.items(), key=lambda x: (x[1].relay, x[1].power))

        for part in sorted_comm_list:
            available_comm_part_matrix.append([part[1].full_name, part[1].alias])
        print(pretty_table(available_comm_part_matrix, "  ", True))

        print(f"\nFor modded items or bodies add them to the {GAME_DATA_FILE_PATH} file")
        parser.exit()

    def recursive_system_sorter(self, parent_body, start_index, end_index, system_map):
        if start_index > end_index:
            return []

        new_system_map = ["" for _ in range(start_index, end_index + 1)]
        current_index = 0
        for body, data in system_map.items():
            if data[2] == parent_body:
                new_system_map[current_index] = data[0] + body

                for index, body_string in enumerate(
                        self.recursive_system_sorter(body, current_index + 1, current_index + data[1], system_map)):
                    new_system_map[current_index + 1 + index] = body_string

                current_index += data[1] + 1

        return new_system_map


def read_game_data(file_path: str) -> GameData:
    with open(file_path) as f:
        data = json.load(f)

    return GameData(data)


def valid_comm_parts(arg_value: str) -> dict[str, int]:
    match = re.fullmatch(r"^\d+:[\w\d\-_]+(,\d+:[\w\d\-_]+)*,?$", arg_value)
    if match is None:
        raise TypeError

    if match.string[-1] == ",":
        comm_parts_list = match.string[:-1].split(",")
    else:
        comm_parts_list = match.string.split(",")

    comm_parts = {item.split(":")[1]: int(item.split(":")[0]) for item in comm_parts_list}

    # This checks if the user has entered something like 1:HG5,2:HG5
    if len(comm_parts) != len(comm_parts_list):
        raise TypeError

    for quantity in comm_parts.values():
        if quantity < 1:
            raise TypeError

    return comm_parts


def valid_percent(arg_value: str) -> float:
    match = re.fullmatch(r"\d{1,3}%|\d{1,3}", arg_value)
    if match is None:
        raise TypeError

    if match.string[-1] == "%":
        percent = int(match.string[:-1])/100
    else:
        percent = int(match.string)/100

    if percent > 1.0:
        raise TypeError

    return percent


def pretty_distance(distance: int, round_to: int = None) -> str:
    if distance < 1000:
        return f"{distance } m"

    elif 1_000 <= distance < 1_000_000:
        new_distance = distance / 1000
        new_distance = round(new_distance, round_to) if round_to is not None else new_distance

        if new_distance.is_integer():
            new_distance = int(new_distance)

        return f"{new_distance} km"

    elif 1_000_000 <= distance < 1_000_000_000:
        new_distance = distance / 1000000
        new_distance = round(new_distance, round_to) if round_to is not None else new_distance
        if new_distance.is_integer():
            new_distance = int(new_distance)

        return f"{new_distance} Mm"

    elif 1_000_000_000 <= distance < 1_000_000_000_000:
        new_distance = distance / 1000000000
        new_distance = round(new_distance, round_to) if round_to is not None else new_distance
        if new_distance.is_integer():
            new_distance = int(new_distance)

        return f"{new_distance} Gm"

    else:
        new_distance = round(distance / 1000000000000, 12)
        new_distance = round(new_distance, round_to) if round_to is not None else new_distance
        if new_distance.is_integer():
            new_distance = int(new_distance)

        return f"{new_distance} Tm"


def pretty_time(time: int) -> str:
    if time < 60:
        return f"{time} sec{'' if time == 1 else 's'}"
    elif 60 <= time < 3600:
        seconds = time % 60
        minutes = (time - seconds) // 60

        return f"{minutes} min{'' if minutes == 1 else 's'} {seconds} sec{'' if seconds == 1 else 's'}"
    else:
        seconds = time % 60
        minutes = (time % 3600) // 60
        hours = (time - seconds - (minutes * 60)) // 3600

        return f"{hours} hr{'' if hours == 1 else 's'} " \
               f"{minutes} min{'' if minutes == 1 else 's'} " \
               f"{seconds} sec{'' if seconds == 1 else 's'}"


def pretty_table(matrix: list[list[str]], row_prefix: str, top_line_is_column_title: bool = False) -> str:
    max_length_for_each_column = [max([len(matrix[row][col]) for row in range(0, len(matrix))])
                                  for col in range(0, len(matrix[0]))]

    table = ""

    for r_index, row in enumerate(matrix):
        if r_index == 1 and top_line_is_column_title:
            table += f"{row_prefix}----" + "---" * (len(matrix[0]) - 1) + "-" * sum(max_length_for_each_column) + "\n"
            # 4 dashes is for the smallest possible 1*1, an additional 3 dashes per column, dashes to cover all entries

        table += f"{row_prefix}|"
        for c_index, col in enumerate(row):
            table += f" {col} " + (" " * (max_length_for_each_column[c_index] - len(col))) + "|"
        table += "\n"

    return table[:-1]


def pretty_speed(speed: int):
    if speed >= 1000:
        str_speed = str(speed)
        x = len(str_speed) % 3
        parts = [str_speed[:x]] + textwrap.wrap(str_speed[x:], 3)

        return f"{','.join(parts)} m/s"
    else:
        return f"{speed} m/s"


def calculate_combined_comm_power(comm_parts: list[CommPart]) -> int:
    # https://wiki.kerbalspaceprogram.com/wiki/CommNet#Combining_antennae

    highest_power = max(map(lambda x: x.power, comm_parts))
    sum_of_powers = sum(map(lambda x: x.power * x.quantity, comm_parts))

    sum_of_weighted_compatibility_exponents = sum(map(lambda x: x.power * x.combinability_exponent * x.quantity,
                                                      comm_parts))

    avg_compatibility_exponent = sum_of_weighted_compatibility_exponents / sum_of_powers

    return int(round(highest_power * math.pow((sum_of_powers/highest_power), avg_compatibility_exponent)))


def calculate_minimum_comm_distance(comm_power_1: int, comm_power_2: int, minimum_strength: float):
    # TODO Make sure this works in all cases
    max_comm_range = math.sqrt(comm_power_1 * comm_power_2)

    x = sympy.symbols("x")
    eq = sympy.Eq(-2*x**3 + 3*x**2, minimum_strength)
    sol = sympy.solve(eq, x)[1].args[0]

    return int(round(max_comm_range * (1 - sol)))


def create_comm_matrix(relay_power: int, minimum_strength: float, max_quantity: int, game_data: GameData):
    sorted_comm_list: list[tuple[str, CommPart]] = \
        sorted(game_data.comm_parts.items(), key=lambda x: (x[1].relay, x[1].power))

    comm_matrix = [["Communication Part", *[f"Quantity {x}" for x in range(1, max_quantity + 1)]]]
    for comm_part in sorted_comm_list:
        current_part = copy(comm_part[1])

        distances = []
        for i in range(1, max_quantity + 1):
            current_part.add_quantity(i)
            distances.append(pretty_distance(calculate_minimum_comm_distance(
                relay_power, calculate_combined_comm_power([current_part]), minimum_strength), 3))

        comm_matrix.append([comm_part[0], *distances])

    return comm_matrix


def create_orbit_suggestion_matrix(min_orbit: int, num_suggestions: int,
                                   target_body: CelestialBody) -> tuple[list[list[str]], bool]:
    start_orbit_period = 10800 * round(math.ceil(target_body.calculate_orbital_period(min_orbit, min_orbit)) / 10800)
    # Round orbital period up to the nearest multiple of 3 hours

    suggestions = [["Satellite Radius", "Satellite Period",
                    "Phase Periapsis", "Phase Period", "Delta-V for Transfer"]]
    i = 0
    while len(suggestions) - 1 < num_suggestions:
        possible_suggestion = target_body.calculate_orbit_radius_with_period(start_orbit_period + 10800 * i)

        if possible_suggestion > target_body.sphere_of_influence:
            break

        phase_orbit = target_body.calculate_periapsis_with_apoapsis_and_period(
            possible_suggestion, int(round((start_orbit_period + 10800 * i) * 0.666666666)))

        if phase_orbit <= 0:
            i += 1
            continue

        satellite_radius = pretty_distance(possible_suggestion)
        satellite_period = pretty_time(start_orbit_period + 10800 * i)
        phase_periapsis = pretty_distance(phase_orbit)
        phase_period = pretty_time(int(round((start_orbit_period + 10800 * i) * 0.666666666)))
        delta_v = pretty_speed(target_body.calculate_delta_v_for_hohmann_transfer(phase_orbit, possible_suggestion))

        suggestions.append([satellite_radius, satellite_period, phase_periapsis, phase_period, delta_v])
        i += 1

    if len(suggestions) - 1 < num_suggestions:
        return suggestions, False

    return suggestions, True


def main():
    # ================ Read Game Data ================

    try:
        game_data = read_game_data(GAME_DATA_FILE_PATH)

    except FileNotFoundError:
        print(f"The game data file {GAME_DATA_FILE_PATH} does not exist.\n")
        exit()

    except Exception:
        print()
        exit(f"Unexpected error in game data read.\nEnsure file {GAME_DATA_FILE_PATH} "
             f"exists and is of the correct format")

    # ================ Initialise argparse ================

    help_epilog = """Note: Only include the communication parts that will be used for relaying signals. 
    Additional parts for the vessel itself to communicate should not be included.

examples:
  ksp_comm_array_calc.py -tb Mun -cp 2:HG5
  ksp_comm_array_calc.py -tb Gilly -cp 2:HG5,3:RA2 -ms 55
  ksp_comm_array_calc.py -tb Duna -cp 1:HG5,5:RA15 -ms 62 -ns 7 -mq 5
    """

    parser = argparse.ArgumentParser(epilog=help_epilog, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-so", "--show-options", action=ShowOptions,
                        help="show all of the body and communication options and exit")
    parser.add_argument("-tb", "--target-body", dest="target_body", type=str, required=True,
                        help="the celestial body that the array will be orbiting")
    parser.add_argument("-cp", "--comm-parts", dest="comm_parts", type=valid_comm_parts, required=True,
                        help="this is the quantity and model of comm parts that will be on each satellite. "
                             "formatted as \"[num]:[alias]\". multiple parts should be in a comma separated list.")
    parser.add_argument("-ms", "--min-strength", dest="min_strength", type=valid_percent, default="80%",
                        help="the minimum signal strength for anything inside the relays SOI "
                             "expressed as an integer percentage. default is %(default)s")
    parser.add_argument("-ns", "--num-suggestions", dest="num_suggestions", type=int, default=5,
                        help="the number of suggested orbits to return. default is %(default)s")
    parser.add_argument("-mq", "--max-quantity", dest="max_quantity", type=int, default=5,
                        help="the number of comm parts that will be calculated up to. default is %(default)s")

    # ================ Main Execution ================

    if len(argv) == 1:
        parser.print_help()
        exit()

    args = parser.parse_args()

    # ================ Verifying Correct User Values ================

    if not game_data.verify_body(args.target_body.lower()):
        print(f"The target body: \"{args.target_body}\" does not exist. use -so for a full list.\n")
        exit()

    for comm_part in args.comm_parts:
        if not game_data.verify_comm_part(comm_part):
            print(f"The communication part: \"{comm_part}\" does not exist. use -so for a full list.\n"
                  f"Remember the -cp argument expects the alias of the part and not the full name.\n")
            exit()

    if args.num_suggestions <= 0:
        print(f"Program must return at least 1 suggestion :(\n")
        exit()

    if args.max_quantity <= 0:
        print(f"Program must display at least 1 quantity of parts.\n")
        exit()

    num_suggestions: int = args.num_suggestions
    max_quantity: int = args.max_quantity
    target_body: CelestialBody = game_data.get_celestial_body(args.target_body)
    min_strength: float = args.min_strength

    comm_parts: list[CommPart] = []
    for alias, quantity in args.comm_parts.items():
        cp = game_data.get_comm_part(game_data.get_part_name_from_alias(alias))
        cp.add_quantity(quantity)
        comm_parts.append(cp)

    for comm_part in comm_parts:
        if not comm_part.relay:
            print(f"The communication part: \"{comm_part.full_name}\" is not capable of relaying a signal"
                  f" and shouldn't be included in calculations.\n")
            exit()

    # ================ Output Relevant Information ================

    print(f"  Target body: {target_body.name}")
    print(f"  Target radius: {pretty_distance(target_body.radius)}")
    print(f"  Target sphere of influence: {pretty_distance(target_body.sphere_of_influence)}")
    print(f"  Each satellite equipped with:")
    for part in comm_parts:
        print(f"      {part.quantity} {part.full_name}{'s' if part.quantity > 1 else ''}")
    print()
    print(f"  Minimum signal strength for vessels inside relay SOI: {int(min_strength*100)}%")

    # ================ Calculations ================

    minimum_orbit = target_body.radius
    antenna_combined_power = calculate_combined_comm_power(comm_parts)

    matrix_of_comm_parts = create_comm_matrix(antenna_combined_power, min_strength, max_quantity, game_data)

    matrix_of_suggested_orbits, fulfilled_quota = create_orbit_suggestion_matrix(minimum_orbit, num_suggestions, target_body)

    # ================ Display Calculated Values ================
    print(f"  Combined power of all antennas on satellite: {pretty_distance(antenna_combined_power)}")
    print(f"  Minimum viable orbit: {pretty_distance(minimum_orbit)}")
    print()
    print(f"  Minimum distance for {int(min_strength*100)}% signal strength with a given quantity of the part.")
    print(pretty_table(matrix_of_comm_parts, "  ", True))
    print()
    print("  These values can be considered the maximum orbits for a given use case.")
    print("  When using these values as orbits remember to factor in the radius of the target body.")
    print()

    table_of_suggested_orbits = pretty_table(matrix_of_suggested_orbits, "  ", True)
    length_of_table = len(table_of_suggested_orbits.split("\n")[0])
    print("  " + "=" * (length_of_table // 2 - 9) + " Suggested Orbits " + "=" *
          (length_of_table // 2 - (9 if length_of_table % 2 == 0 else 10)))
    print(table_of_suggested_orbits)
    if not fulfilled_quota:
        print(f"\n  Only {len(matrix_of_suggested_orbits) - 1} of the {num_suggestions} "
              f"orbits were able to be calculated as higher orbits will exceed the targets SOI")
    print()


if __name__ == "__main__":
    main()
