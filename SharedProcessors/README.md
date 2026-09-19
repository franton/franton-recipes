# Shared Processors

This is a compendium of autopkg shared processors that I've found useful or have bodged together myself. The idea is if I find something useful, I make a copy of it and then run it from my own repo so everything is self contained.

Copyright remains with the original authors.

## DistributionPackageCreator.py
* Author: Rich Trouton
* Description: Converts a standard pkg file (as output from other processors) into a distribution format pkg.
* Link: https://derflounder.wordpress.com/2024/02/04/building-distribution-packages-using-autopkg/

## FileMode.py
* Author: Zack Thompson (MLBZ521)
* Description: Changes the chmod permissions on file or folder
* Link: https://github.com/autopkg/MLBZ521-recipes/blob/master/Shared%20Processors/FileMode.py

## IconGenerator.py
* Author: Richard Purves (but 80% is Greg Neagle / Per Olafson's code)
* Description: Takes an .app (even inside a dmg), processes it through SAP Icons cli tool to get app icons.

## PkgSigner.py
* Author: Rich Trouton
* Description: Applies code signing to an output pkg file
* Link: https://derflounder.wordpress.com/2021/07/30/signing-autopkg-built-packages-using-a-sign-recipe/

## TextSearcher.py
* Author: Anthony Reimer
* Description: Looks for regex patterns in autopkg variable outputs
* Link: https://maclabs.jazzace.ca/2022/08/17/text-searching-in-autopkg.html
