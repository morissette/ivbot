# ivbot
Pokemon Go Twitter Bot for 100IV

## About
Wanted to try out getting 100IV pokemon via you know; somewhat non legit methods.

## Bot.py
Scrapes twitter every 5 mins and posts message somewhere

## Config for Twitter
Set variables in a environment file
```bash
cp envfile_sample envfile
source envfile
python bot.py
```

## Config for Custom Pokemon
Maybe you only want certain 100IV pokemon. You can override the current list by
setting *POKEMON_FILE* in your environment with the path to a json file that 
contains a array of pokemon names.

### Example
```json
[
  "Bulbasaur",
  "Charmander"
]
```

## Example Output
This is for group me but should easily be modified for whatever communication
method you prefer.

![example output](img/sample.png)
