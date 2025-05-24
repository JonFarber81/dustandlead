# Dust & Lead

A tactical turn-based gunfight game set in the Wild West, built with Python and tcod. Face off against bandits in procedurally generated desert landscapes

This is mostly intended as a place for me to hone up on my Python skills and play around with the TCOD library. It also gives me a chance to incorporate my love of the western genre into my development journey!

## Game Overview

Step into the boots of a gunslinger in the American frontier. Each duel is a deadly dance of positioning, timing, and marksmanship. Choose your fighting style, select your weapon, and prove you're the fastest gun in the West.

### Key Features

- **Turn-based tactical combat** - Plan your moves carefully
- **Realistic ballistics** - Bullets travel and can hit cover
- **Character bonuses** - 6 unique gunslinger archetypes to choose from
- **Multiple weapons** - Pistols, rifles, and shotguns with different stats
- **Dynamic terrain** - Rivers, rocks, cacti, trees, and building ruins provide cover
- **Animated combat** - Watch bullets fly

## How to Play

### Controls
- **Arrow Keys** - Move your character
- **F** - Fire at the enemy
- **R** - Restart game (when game over)
- **ESC** - Quit game
- **1-6** - Select bonuses and weapons during setup


## Character Bonuses

Choose your fighting style with these unique bonuses:

| Bonus | Description | Effects |
|-------|-------------|---------|
| **TOUGH** | Years of hard living made you resilient | +20 Health Points |
| **LONG SHOT** | Make shots others wouldn't dare attempt | +50% shooting range, -30% long-range accuracy |
| **QUICKDRAW** | Lightning fast on the draw | +10 damage to all shots |
| **EAGLE EYE** | Legendary aim across the frontier | +20% accuracy at all ranges |
| **GUNSLINGER** | Sometimes luck favors the bold | 15% chance for critical hits (2x damage) |
| **DESPERADO** | Nothing left to lose | +40% damage dealt, +50% damage taken |

## Weapons

Each weapon has distinct tactical advantages:

### Pistol
- **Range:** 12 tiles
- **Accuracy:** Good (40% minimum)
- **Damage:** 20-35
- **Best for:** Balanced combat and mobility

### Rifle
- **Range:** 20 tiles  
- **Accuracy:** Excellent (60% minimum)
- **Damage:** 35-50
- **Best for:** Long-range precision shooting

### Shotgun
- **Range:** 8 tiles
- **Accuracy:** Outstanding (80% minimum)
- **Damage:** 40-60
- **Best for:** Close-quarters devastation

## Terrain & Tactics

The procedurally generated Wild West landscapes include:

- **🌊 Water** - Rivers and ponds block movement and bullets
- **🌲 Trees** - Provide cover from gunfire
- **🗿 Rocks** - Stone formations offer solid protection  
- **🏚️ Building Ruins** - Crumbling structures create tactical positions
- **🌵 Cacti** - Block movement but bullets can pass through
- **🧱 Walls** - Solid cover that stops everything

Use terrain strategically! Position yourself behind cover, force enemies into the open, and control the battlefield.

## Combat Mechanics

### Accuracy System
- Accuracy decreases with distance
- Each weapon has different accuracy profiles
- Bonuses can modify your hit chances
- Cover blocks bullets completely

### Damage System
- Random damage within weapon ranges
- Critical hits deal double damage
- Bonuses can increase damage output
- No armor - every hit counts

### Line of Sight
- Bullets travel in straight lines
- Terrain blocks shots realistically
- You can see bullet trails and impacts
- Plan shots around obstacles

---

*Saddle up, partner. The frontier awaits, and only the fastest gun survives.* 