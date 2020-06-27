<?php
/**
 *------
 * BGA framework: © Gregory Isabelli <gisabelli@boardgamearena.com> & Emmanuel Colin <ecolin@boardgamearena.com>
 * Gomoku implementation : © Emmanuel Colin <ecolin@boardgamearena.com>
 * 
 * This code has been produced on the BGA studio platform for use on http://boardgamearena.com.
 * See http://en.boardgamearena.com/#!doc/Studio for more information.
 * -----
 *
 * material.inc.php
 *
 * Gomoku game material description
 *
 * Here, you can describe the material of your game with PHP variables.
 *   
 * This file is loaded in your game logic class constructor, ie these variables
 * are available everywhere in your game logic code.
 *
 */


/*

Example:

$this->card_types = array(
    1 => array( "card_name" => ...,
                ...
              )
);

*/

$this->gameConstants = array(
		"INTERSECTION_WIDTH" => 30,
		"INTERSECTION_HEIGHT" => 30,		
		"INTERSECTION_X_SPACER" => 2.8, // Float
		"INTERSECTION_Y_SPACER" => 2.8, // Float
		"X_ORIGIN" => 25,
		"Y_ORIGIN" => 25,
);

