# JackGames Multicart

A collection of games for the Jack Games Multicart.

# Notes

Font sizes: Upheaval looks best when using a multiple of 20.

To build on Windows for Windows, use `build-win.bat`.

To build on Windows for web browsers use `build-web.bat`.

# TODOs

## General / Misc

* Controller and local multiplayer interface
* Recreate roy carnassus? via galactica started. maybe scrap it for a pirate ship game? jackpirates?
* 4jacks: convert board to numpy, improve minimax algorithm. make a simplified mode that doesn't have piece ejection.

# Raycaster

* Change the naive draw_walls implementation to use a quadrant based cross section of the
possible tile path.
* Change the raycaster to load walls from an image file into a 2d array.

# Console

* Instead of just the scene under the console having its callbacks added to the console, instead add the callbacks of every scene to the console so long as it does not conflict with the name of a callback in the scene above it. This way, the console can be used to control any active scene via callbacks.

# QuadBlocks Game Server

Game server is currently being tested on railway ~~and fly.io~~

Looks like railway has a free tier that will work for now with a postgres instance for the leaderboard.

# Jack Ninjas

An adaption and implementation of the the public domain game from YouTuber
[DaFluffyPotato](https://www.youtube.com/@DaFluffyPotato) for my nephew Jack.

<https://www.youtube.com/watch?v=2gABYM5M0ww>

## Todos

~~- Finish DaFluffyPotato's course~~

* Finish pallet swap
* Joystick input
* Alucard style movement trails
* Port to web with [pygbag](https://pypi.org/project/pygbag/)
* ~~Implement the new fall animation.~~

## Adjustments & Additions

* 16:9 aspect ratio
* Metroid Style Space Jump
* fall animation

## Palette Swap

New Colors

* 0x0000dd ninja robe
* 0x00008e ninja robe dark

# Swappy

My simple PNG/CSV based color palette swapper

1. Create a CSV list of all RGBA values encountered in a folder of PNGs.

```
python .\swappy.py assets\jackninjas\images\tiles\grass palette.csv`
```

2. Modify the CSV and adjust the target RGBA values.

3. Supply the CSV and source folder along with a destination folder to
perform the palette swap.

```
python .\swappy.py assets\jackninjas\images\tiles\grass palette.csv assets\jackninjas\images\tiles\snow
```

# Credits

## DaFluffyPotato

JackNinjas code & art

## Kenney.nl

Various assets

## itch.io

2D Dungeon Asset Pack - Purchased by jwd83

Bat Animation: Free for commercial use and to modify by Caz
<https://caz-creates-games.itch.io/bat>

Pixel Medieval Chandelier by nyknck
<https://nyknck.itch.io/pixel-medieval-chandelier>

## OpenGameArt

### Toad Monster by HorrorMovieRei
https://opengameart.org/content/toad-monster

Various assets

## OpenAI, Dall-E & ChatGPT

AI generated images and text

## bsfxr & jsfxr

Various sound effects

## Game Controller DB

Source: <https://github.com/gabomdq/SDL_GameControllerDB>

## GregorQuendel

Free Music - Korobeiniki
<https://pixabay.com/music/search/korobeiniki/>

## Udio.com

Various music tracks potentially.

## floraphonic

<https://pixabay.com/users/floraphonic-38928062/>
level up bonus and cute level up sounds

## PIXBAY ALIENIGHTMARE

dying-guy

## PIXBAY moodmode

potential music

## PIXBAY freesound_community

knife throw

## My own assets
Various...
pointer.png
pointer-outlined.png
pointer-outlined-small.png
icon-ammo.png