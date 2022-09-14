# Kerbal Space Program Comm Array Calculator
KSPCAC is a command line tool for calculating the optimal orbits for 3 equidistant relay satellites. 
You provide the body you plan to orbit and the communication parts on each satellite then it provides a number 
of possible orbits that you can choose from. It also provides the phase orbits to allow for easy deployment.

# Theory
These two YouTube videos by Mike Aben do a great job of explaining the math and reasons for this approach.
- [The math of why specific orbits are best](https://youtu.be/gpQmvwU1x8c)
- [How to actually deploy the satellites](https://youtu.be/l9oPvLp7YlQ)


# Installation
To install just clone the repo and install the requirements
```commandline
Python 3.10.x

git clone https://github.com/Stuart-Laing/KSPCAC
py -m pip install -r ksp_comm_array_calculator/requirements.txt
```

# Usage
To get a list of all the options use:
```
py ksp_comm_array_calc.py -h
```

```
usage: ksp_comm_array_calc.py [-h] [-so] -tb TARGET_BODY -cp COMM_PARTS [-ms MIN_STRENGTH] [-ns NUM_SUGGESTIONS] [-mq MAX_QUANTITY]

options:
  -h, --help            show this help message and exit
  -so, --show-options   show all of the body and communication options and exit
  -tb TARGET_BODY, --target-body TARGET_BODY
                        the celestial body that the array will be orbiting
  -cp COMM_PARTS, --comm-parts COMM_PARTS
                        this is the quantity and model of comm parts that will be on each satellite. formatted as "[num]:[alias]".
                        multiple parts should be in a comma separated list.
  -ms MIN_STRENGTH, --min-strength MIN_STRENGTH
                        the minimum signal strength for anything inside the relays SOI expressed as an integer percentage. default is 80%
  -ns NUM_SUGGESTIONS, --num-suggestions NUM_SUGGESTIONS
                        the number of suggested orbits to return. default is 5
  -mq MAX_QUANTITY, --max-quantity MAX_QUANTITY
                        the number of comm parts that will be calculated up to. default is 5

Note: Only include the communication parts that will be used for relaying signals.
      Additional parts for the vessel itself to communicate should not be included.

examples:
  ksp_comm_array_calc.py -tb Mun -cp 2:HG5
  ksp_comm_array_calc.py -tb Gilly -cp 2:HG5,3:RA2 -ms 55%
  ksp_comm_array_calc.py -tb Sun -cp 1:HG5,5:RA15 -ms 62 -ns 7 -mq 5
```

The flag `-so` will show the available bodies and communication parts that can be selected from.
```
Available celestial bodies:
  Sun
    Dres
    Duna
      Ike
    Eeloo
    Eve
      Gilly
    Jool
      Bop
      Laythe
      Pol
      Tylo
      Vall
    Kerbin
      Minmus
      Mun
    Moho

Available communication parts:
  | Full Part Name         | Alias |
  ----------------------------------
  | Communotron 16         | C16   |
  | Communotron 16-S       | C16S  |
  | HG-5 High Gain Antenna | HG5   |
  | RA-2 Relay Antenna     | RA2   |
```

So if I wish to get information about the following situation:
- Building a relay network around the Mun
- Each satellite will be equipped with 2 HG-5 High Gain Antennas
- Any vessel within the networks orbit should always have a strength of 80% minimum
- Only show up to 3 comm parts
- Suggest 3 orbits
```
py ksp_comm_array_calc.py -tb Mun -cp 2:HG5 -ms 80% -mq 3 -ns 3

  Target body: Mun
  Target radius: 200 km
  Target sphere of influence: 2.429559 Mm
  Each satellite equipped with:
      2 HG-5 High Gain Antennas

  Minimum signal strength for vessels inside relay SOI: 80%
  Combined power of all antennas on satellite: 8.408964 Mm
  Minimum viable orbit: 200 km

  Maximum distance for 80% signal strength with a given quantity of the part.
  | Communication Part     | Quantity 1 | Quantity 2 | Quantity 3 |
  -----------------------------------------------------------------
  | Communotron 16         | 588.777 km | 832.657 km | 1.02 Mm    |
  | Communotron 16-S       | 588.777 km | N/A        | N/A        |
  | Communotron DTS-M1     | 37.238 Mm  | 48.291 Mm  | 56.221 Mm  |
  | Communotron HG-55      | 101.979 Mm | 132.251 Mm | 153.969 Mm |
  | Communotron 88-88      | 263.309 Mm | 341.47 Mm  | 397.545 Mm |
  | HG-5 High Gain Antenna | 1.862 Mm   | 2.415 Mm   | 2.811 Mm   |
  | RA-2 Relay Antenna     | 37.238 Mm  | 48.291 Mm  | 56.221 Mm  |
  | RA-15 Relay Antenna    | 101.979 Mm | 132.251 Mm | 153.969 Mm |
  | RA-100 Relay Antenna   | 263.309 Mm | 341.47 Mm  | 397.545 Mm |

  These values can be considered the maximum orbits for a given use case.
  When using these values as orbits remember to factor in the radius of the target body.

  ============================================ Suggested Orbits ===========================================
  | Satellite Radius | Satellite Period    | Phase Periapsis | Phase Period        | Delta-V for Transfer |
  ---------------------------------------------------------------------------------------------------------
  | 377.36 km        | 3 hrs 0 mins 0 secs | 103.856 km      | 2 hrs 0 mins 0 secs | 67 m/s               |
  | 716.501 km       | 6 hrs 0 mins 0 secs | 282.341 km      | 4 hrs 0 mins 0 secs | 53 m/s               |
  | 1.000956 Mm      | 9 hrs 0 mins 0 secs | 432.046 km      | 6 hrs 0 mins 0 secs | 46 m/s               |
```

### Communication Table
The communication part table might be a little difficult to parse.  
The idea is that if your satellite with its 2 HG-5 High Gain Antennas wants to communicate with a vessel with a 
single Communotron 16 then the maximum distance they can be while retaining that strength is 588.777 km  
This is important because if we were to choose the second suggested orbit at 716.501 km it would be too high to maintain 80% strength.

The table allows you to pick the best orbit for your use case depending on what equipment your vessels are likely to be using.

### Suggested Orbits
The first value is the radius of the circular orbit that your satellites will be doing once deployed, this is followed 
by that orbits period.

The "Phase Periapsis" is what you will need to lower the periapsis to in order to phase in and out of the higher orbit, your apoapsis will remain the first value.

The final column is the delta-v required for the hohmann transfer between the circular and eliptical orbits.

# Mods
For modded planets and parts you can add their details to the gamedata.json file. This information should 
be on the mod page or can be found in game.

Adding to the json should be easy enough but there are some things to keep in mind.
- `radius`, `sphere of influence`, and `power` are all measured in meters
- `mass` is measured in kgs
- The `parent body` is only used in `--show-options` so that it can nest moons and planets. If you don't care about that then leave it as an empty string.
- The `alias` must match the regex `[\w\d\-_]+`
- The `compatibility exponent` for almost all KSP parts is 0.75