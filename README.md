Game_Of_Life
============

Game of Life Simulator used to demonstrate Automata Theory - Created for Automata Theory/Formal Languages
 - Demonstates John Conways Game of Life
 - Able to modify environment and cell attributes to simulate:
    - Migration
    - Survival
    - Group Survival
    - Logic Gates --> Complex Circuts

To Run:
============
 - Make sure to have python version 2.7.8 (Could work with Python 3 but is untested)
 - tkinter module is installed
 - Needs to be run from GUI based OS (tkinter requires gui but underlying sim can be ported and ran from terminal/cmd)

 * Only tested on Windows(8.1) but should be no issues with Linux (as long as above requirements are met)
 $> python GoLSim.py
          or
 - Right click and open with IDLE and then Run Module
 

Needed Improvements (12-28-14):
============
 - Previous State button
 - Environment Rule Priority -- Be able to change the order in which rules are applied
 - Individual environment cell attributes - Each cell can have its own environment(rough terrian, water, etc.)
 - Port to better GUI module - (PyGame, WxPython, maybe others?)
 - Create cmd/terminal version
 - Sim settings file import - Save/Load simulation rules/configuration
 - Sim state file save/load - Save/Load simulation states
 - Batch Simulation run - Load sim rules/configuration and starting state(or random) and run for N turns saving results
 - Simulation Algorithm import - Be able to import specific behaviors(algorithms) for cells

