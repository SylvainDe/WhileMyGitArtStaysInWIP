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
 * gameoptions.inc.php
 *
 * Gomoku game options description
 * 
 * In this file, you can define your game options (= game variants).
 *   
 * Note: If your game has no variant, you don't have to modify this file.
 *
 * Note²: All options defined in this file should have a corresponding "game state labels"
 *        with the same ID (see "initGameStateLabels" in emptygame.game.php)
 *
 * !! It is not a good idea to modify this file when a game is running !!
 *
 */

$game_options = array(

    100 => array(
                'name' => _('Variant'),
                'values' => array(
                            1 => array( 'name' => totranslate( 'Standard' ), 'tmdisplay' => totranslate( 'Standard' ) ),
                            2 => array( 'name' => totranslate( 'Gomoku+ (Caro)' ), 'tmdisplay' => totranslate( 'Gomoku+ (Caro)' ) ),
                        )
            ),

    101 => array(
                'name' => _('Opening'),
                'values' => array(
                            1 => array( 'name' => totranslate( 'Freestyle' ), 'tmdisplay' => totranslate( 'Freestyle' ) ),
                            2 => array( 'name' => totranslate( 'Tournament' ), 'tmdisplay' => totranslate( 'Tournament' ) ),
                        ),
                'default' => 2
            ),

    /* Example of game variant:
    
    
    // note: game variant ID should start at 100 (ie: 100, 101, 102, ...)
    100 => array(
                'name' => totranslate('my game option'),    
                'values' => array(

                            // A simple value for this option:
                            1 => array( 'name' => totranslate('option 1') )

                            // A simple value for this option.
                            // If this value is chosen, the value of "tmdisplay" is displayed in the game lobby
                            2 => array( 'name' => totranslate('option 2'), tmdisplay' => totranslate('option 2') ),

                            // Another value, with other options:
                            //  beta=true => this option is in beta version right now.
                            //  nobeginner=true  =>  this option is not recommended for beginners
                            3 => array( 'name' => totranslate('option 3',  'beta' => true, 'nobeginner' => true ),) )
                        )
            )

    */

);


