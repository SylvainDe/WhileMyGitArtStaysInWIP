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
  * gomoku.game.php
  *
  * This is the main file for your game logic.
  *
  * In this PHP file, you are going to defines the rules of the game.
  *
  */  

require_once( APP_GAMEMODULE_PATH.'module/table/table.game.php' );

// Local constants
define( "VARIANT_GOMOKU_STANDARD", 1 );
define( "VARIANT_GOMOKU_PLUS", 2 );

define( "OPENING_GOMOKU_STANDARD", 1 );
define( "OPENING_GOMOKU_TOURNAMENT", 2 );

class Gomoku extends Table
{
	function __construct( )
	{
        	
 
        // Your global variables labels:
        //  Here, you can assign labels to global variables you are using for this game.
        //  You can use any number of global variables with IDs between 10 and 99.
        //  If your game has options (variants), you also have to associate here a label to
        //  the corresponding ID in gameoptions.inc.php.
        // Note: afterwards, you can get/set the global variables with getGameStateValue/setGameStateInitialValue/setGameStateValue
        parent::__construct();self::initGameStateLabels( array(
                  "end_of_game" => 10,
            //    "my_first_global_variable" => 10,
            //    "my_second_global_variable" => 11,
            //      ...
                  "game_variant" => 100,
                  "game_opening" => 101,
            //    "my_second_game_variant" => 101,
            //      ...
        ) );
	}
	
    protected function getGameName( )
    {
        return "gomoku";
    }	

    /*
        setupNewGame:
        
        This method is called 1 time when a new game is launched.
        In this method, you must setup the game according to game rules, in order
        the game is ready to be played.    
    
    */
    protected function setupNewGame( $players, $options = array() )
    {    
        $sql = "DELETE FROM player WHERE 1 ";
        self::DbQuery( $sql );

        // Set the colors of the players with HTML color code
        // The default is red/green/blue/yellow
        // The number of colors defined here must correspond to the maximum number of players allowed for the game
        $default_colors = array( "000000", "ffffff", );
 
        // Create players
        // Note: if you added some extra field on "player" table in the database (dbmodel.sql), you can initialize it there.
        $sql = "INSERT INTO player (player_id, player_color, player_canal, player_name, player_avatar) VALUES ";
        $values = array();
        foreach( $players as $player_id => $player )
        {
            $color = array_shift( $default_colors );
            $values[] = "('".$player_id."','$color','".$player['player_canal']."','".addslashes( $player['player_name'] )."','".addslashes( $player['player_avatar'] )."')";
        }
        $sql .= implode( $values, ',' );
        self::DbQuery( $sql );
        self::reloadPlayersBasicInfos();
        
        /************ Start the game initialization *****/

        // Init global values with their initial values
        // Example:
        // self::setGameStateInitialValue( 'my_first_global_variable', 0 );
        self::setGameStateInitialValue( 'end_of_game', 0 );
        
        // Init game statistics
        // (note: statistics used in this file must be defined in your stats.inc.php file)
        // Examples:
        //self::initStat( 'table', 'table_teststat1', 0 );    // Init a table statistics
        //self::initStat( 'player', 'player_teststat1', 0 );  // Init a player statistics (for all players)

        self::initStat( 'table', 'turns_number', 0 );
        self::initStat( 'player', 'turns_number', 0 );
      
        // Insert (empty) intersections into database
        $sql = "INSERT INTO intersection (coord_x, coord_y) VALUES ";
        $values = array();
        for ($x = 0; $x < 19; $x++) {
            for ($y = 0; $y < 19; $y++) {
        	
            	$values[] = "($x, $y)";   	
            }
        }
        $sql .= implode( $values, ',' );
        self::DbQuery( $sql );

        // Active first player (which is in general a good idea :) )

        // Black plays first
        $sql = "SELECT player_id, player_name FROM player WHERE player_color = '000000' ";
        $black_player = self::getNonEmptyObjectFromDb( $sql );

        $this->gamestate->changeActivePlayer( $black_player['player_id'] );


        /************ End of the game initialization *****/
    }

    /*
        getAllDatas: 
        
        Gather all informations about current game situation (visible by the current player).
        
        The method is called each time the game interface is displayed to a player, ie:
        _ when the game starts
        _ when a player refreshes the game page (F5)
    */
    protected function getAllDatas()
    {
        $result = array( 'players' => array() );
        
        $current_player_id = self::getCurrentPlayerId();    // !! We must only return informations visible by this player !!
    
        // Get information about players
        // Note: you can retrieve some extra fields you added for "player" table in "dbmodel.sql" if you need them.
        $sql = "SELECT player_id id, player_score score FROM player ";
        $result['players'] = self::getCollectionFromDb( $sql );
  
        // Gather all informations about current game situation (visible by player $current_player_id).

        // Intersections
        $sql = "SELECT id, coord_x, coord_y, stone_color FROM intersection ";
        $result['intersections'] = self::getCollectionFromDb( $sql );

        // Constants
        $result['constants'] = $this->gameConstants;

        // Counters
        $result['counters'] = $this->getGameCounters($current_player_id);
  
        return $result;
    }

    /*
        getGameCounters:
        
        Gather all relevant counters about current game situation (visible by the current player).
    */
    function getGameCounters($player_id) {
    	$sql = "
    		SELECT
    			concat('stonecount_p', cast(p.player_id as char)) counter_name,
    			case when p.player_color = 'white' then 180 - count(id) else 181 - count(id) end counter_value
    		FROM (select player_id, case when player_color = 'ffffff' then 'white' else 'black' end player_color FROM player) p
    		LEFT JOIN intersection i on i.stone_color = p.player_color
    		GROUP BY p.player_color, p.player_id
    	";
    	if ($player_id != null) {
    		// Player private counters
    	}
    
    	return self::getNonEmptyCollectionFromDB( $sql );
    }

    /*
        getGameProgression:
        
        Compute and return the current game progression.
        The number returned must be an integer beween 0 (=the game just started) and
        100 (= the game is finished or almost finished).
    
        This method is called each time we are in a game state with "updateGameProgression" property (see states.inc.php)
    */
    function getGameProgression()
    {
        // Compute and return the game progression

        // Number of stones laid down on the goban over the total number of intersections * 100
        $sql = "
	    	SELECT round(100 * count(id) / (19*19) ) as value from intersection WHERE stone_color is not null
    	";
    	$counter = self::getNonEmptyObjectFromDB( $sql );

        return $counter['value'];
    }


//////////////////////////////////////////////////////////////////////////////
//////////// Utility functions
////////////    

    /*
        Here, you can put any utility methods useful for your game logic
    */




//////////////////////////////////////////////////////////////////////////////

//////////// Player actions
//////////// 

    /*
        Each time a player is doing some game action, one of the methods below is called.
        (note: each method below must match an input method in gomoku.action.php)
    */

    /*
    
    Example:

    function playCard( $card_id )
    {
        // Check that this is player's turn and that it is a "possible action" at this game state (see states.inc.php)
        self::checkAction( 'playCard' ); 
        
        $player_id = self::getActivePlayerId();
        
        // Add your game logic to play a card there 
        ...
        
        // Notify all players about the card played
        self::notifyAllPlayers( "cardPlayed", clienttranslate( '${player_name} played ${card_name}', array(
            'player_id' => $player_id,
            'player_name' => self::getActivePlayerName(),
            'card_name' => $card_name,
            'card_id' => $card_id
        ) );
          
    }
    
    */

    function playStone( $coord_x, $coord_y )
    {
        // Check that this is player's turn and that it is a "possible action" at this game state (see states.inc.php)
        self::checkAction( 'playStone' ); 
        
        $player_id = self::getActivePlayerId();
        
        // Check that this intersection is free
        $sql = "SELECT
                    id, coord_x, coord_y, stone_color
                FROM
                    intersection 
                WHERE 
                    coord_x = $coord_x 
                    AND coord_y = $coord_y
                    AND stone_color is null
               ";
        $intersection = self::getObjectFromDb( $sql );

        if ($intersection == null) {
            throw new BgaUserException( self::_("There is already a stone on this intersection, you can't play there") );
        }

        // Tournament opening (http://www.vcpr.cz/en/help-and-rules/gomoku-rules/): 
        //   - the first stone (black) has to be at the center of the board
        //   - the second stone (white) has to be adjacent to the first stone (black)
        //   - the third stone (black) has to be at least three squares away from the center of the board
        if (self::getGameStateValue('game_opening') == OPENING_GOMOKU_TOURNAMENT) {
            // Number of stones laid down on the goban
            $sql = "
	        	SELECT count(id) as value from intersection WHERE stone_color is not null
        	";
        	$counter = self::getNonEmptyObjectFromDB( $sql );

            if ($counter['value'] == 0) {
                if (! ($coord_x == 9 && $coord_y == 9) ) {
                    throw new BgaUserException( self::_("Tournament opening: the first stone (black) has to be at the center of the board") );
                }
            }

            if ($counter['value'] == 1) {
                if (! ($coord_x >= 8 && $coord_x <= 10 && $coord_y >= 8 && $coord_y <= 10) ) {
                    throw new BgaUserException( self::_("Tournament opening: the second stone (white) has to be adjacent to the first stone (black)") );
                }
            }

            if ($counter['value'] == 2) {
                if (! ($coord_x <= 6 || $coord_x >= 12 || $coord_y <= 6 || $coord_y >= 12) ) {
                    throw new BgaUserException( self::_("Tournament opening: the third stone (black) has to be at least three squares away from the center of the board") );
                }
            }
        }


        // Get player color
        $sql = "SELECT
                    player_id, player_color
                FROM
                    player 
                WHERE 
                    player_id = $player_id
               ";
        $player = self::getNonEmptyObjectFromDb( $sql );
        $color = ($player['player_color'] == 'ffffff' ? 'white' : 'black');

        // Update the intersection with a stone of the appropriate color
        $intersection_id = $intersection['id'];
        $sql = "UPDATE
                    intersection
                SET
                    stone_color = '$color'
                WHERE 
                    id = $intersection_id
               ";
        self::DbQuery($sql);
        
        // Notify all players
        self::notifyAllPlayers( "stonePlayed", clienttranslate( '${player_name} dropped a stone ${coordinates}' ), array(
            'player_id' => $player_id,
            'player_name' => self::getActivePlayerName(),
            'coordinates' => $this->getFormattedCoordinates($coord_x, $coord_y),
            'coord_x' => $coord_x,
            'coord_y' => $coord_y,
            'color' => $color,
            'counters' => $this->getGameCounters(self::getCurrentPlayerId())
        ) );

        // Check if end of game has been met
        if ($this->checkForWin( $coord_x, $coord_y, $color )) {

            // Set active player score to 1 (he is the winner)
            $sql = "UPDATE player SET player_score = 1 WHERE player_id = $player_id";
            self::DbQuery($sql);

            // Notify final score
            $this->notifyAllPlayers( "finalScore",
    					clienttranslate( '${player_name} wins the game!' ),
    					array(
    							"player_name" => self::getActivePlayerName(),
    							"player_id" => $player_id,
    							"score_delta" => 1,
    					)
   			);

            // Set global variable flag to pass on the information that the game has ended
            self::setGameStateValue('end_of_game', 1);

            // End of game message
            $this->notifyAllPlayers( "message",
    				clienttranslate('Thanks for playing!'),
    				array(
    				)
    		);

        }

        // Go to next game state
        $this->gamestate->nextState( "stonePlayed" );
    }

    function getFormattedCoordinates( $coord_x, $coord_y )
    {
        return "(" . chr(65 + $coord_x) . ", " . ($coord_y + 1) . ")";
    }

    function checkForWin( $coord_x, $coord_y, $color )
    {
        // Get intersections in the same row
        $sql = "SELECT
                    id, coord_x, coord_y, stone_color
                FROM
                    intersection
                WHERE 
                    coord_y = $coord_y
                ORDER BY
                    coord_x
               ";
        $intersections = self::getCollectionFromDb( $sql );

        if ( $this->checkFiveInARow( $intersections, $coord_x, $coord_y, $color ) ) {
            return true;
        }

        // Get intersections in the same column
        $sql = "SELECT
                    id, coord_x, coord_y, stone_color
                FROM
                    intersection
                WHERE 
                    coord_x = $coord_x
                ORDER BY
                    coord_y
               ";
        $intersections = self::getCollectionFromDb( $sql );

        if ( $this->checkFiveInARow( $intersections, $coord_x, $coord_y, $color ) ) {
            return true;
        }

        // Get intersections in the same top to bottom diagonal
        $sql = "SELECT
                    id, coord_x, coord_y, stone_color
                FROM
                    intersection
                WHERE 
                    ( cast(coord_x as signed ) - cast( coord_y as signed) ) = $coord_x - $coord_y
                ORDER BY
                    coord_x
               ";
        $intersections = self::getCollectionFromDb( $sql );

        if ( $this->checkFiveInARow( $intersections, $coord_x, $coord_y, $color ) ) {
            return true;
        }

        // Get intersections in the same bottom to top diagonal
        $sql = "SELECT
                    id, coord_x, coord_y, stone_color
                FROM
                    intersection
                WHERE 
                    coord_x + coord_y = $coord_x + $coord_y
                ORDER BY
                    coord_x
               ";
        $intersections = self::getCollectionFromDb( $sql );

        if ( $this->checkFiveInARow( $intersections, $coord_x, $coord_y, $color ) ) {
            return true;
        }

        return false;
    }

    function checkFiveInARow( $intersections, $coord_x, $coord_y, $color )
    {
        // If we find a consecutive set of exactly 5 stones of the same color including this one, it's done!
        // Gomoku+ (Caro) variant:  the set must not be blocked on either side.
        $set = array();
        $stoneInSet = false;
        $leftBlocked = false;
        $rightBlocked = false;
        foreach ($intersections as $intersection) {
            if ($intersection['stone_color'] == $color) {
                if ($set == null) {
                    // Create set
                    $set = array();
                }
                // Add to set
                $set[] = $intersection;
                // Set flag if current stone is in the set
                if ($intersection['coord_x'] == $coord_x && $intersection['coord_y'] == $coord_y) {
                    $stoneInSet = true;
                }
            } else {
                if (! $stoneInSet) {
                    $leftBlocked = ($intersection['stone_color'] != null);

                    // Reset set and go on looping
                    $set = null;
                } else {
                    $rightBlocked = ($intersection['stone_color'] != null);                    

                    // We have the complete set containing the current stone -> break
                    break;
                }
            }            
        }

        if ($stoneInSet && $set != null && count($set) == 5) {            
            if (self::getGameStateValue('game_variant') == VARIANT_GOMOKU_STANDARD) {
                return true;
            }
            if (self::getGameStateValue('game_variant') == VARIANT_GOMOKU_PLUS && ! $leftBlocked && ! $rightBlocked) {
                return true;
            }
        }

        return false;
    }

    
//////////////////////////////////////////////////////////////////////////////
//////////// Game state arguments
////////////

    /*
        Here, you can create methods defines as "game state arguments" (see "args" property in states.inc.php).
        These methods are returning some additional informations that are specific to the current
        game state.
    */

    /*
    
    Example for game state "MyGameState":
    
    function argMyGameState()
    {
        // Get some values from the current game situation in database...
    
        // return values:
        return array(
            'variable1' => $value1,
            'variable2' => $value2,
            ...
        );
    }    
    */

    function argPlayerTurn()
    {
        $sql = "
        	SELECT count(id) as value from intersection WHERE stone_color is not null
    	";
    	$counter = self::getNonEmptyObjectFromDB( $sql );

        return array(
            'numberOfStones' => $counter['value'],
            'tournamentOpening' => (self::getGameStateValue('game_opening') == OPENING_GOMOKU_TOURNAMENT)
        );
    }


//////////////////////////////////////////////////////////////////////////////
//////////// Game state actions
////////////

    /*
        Here, you can create methods defines as "game state actions" (see "action" property in states.inc.php).
        The action method of state X is called everytime the current game state is set to X.
    */
    
    /*
    
    Example for game state "MyGameState":

    function stMyGameState()
    {
        // Do some stuff ...
        
        // (very often) go to another gamestate
        $this->gamestate->nextState( 'some_gamestate_transition' );
    }    
    */

    function stCheckEndOfGame()
    {
        self::trace( "stCheckEndOfGame" );

        $transition = "notEndedYet";

        // If there is no more free intersections, the game ends
        $sql = "SELECT id, coord_x, coord_y, stone_color FROM intersection WHERE stone_color is null";
        $free = self::getCollectionFromDb( $sql );

        if (count($free) == 0) {
            $transition = "gameEnded";
        }        

        // If the 'end of game' flag has been set, end the game
        if (self::getGameStateValue('end_of_game') == 1) {
            $transition = "gameEnded";
        }
                
        $this->gamestate->nextState( $transition );
    }

    function stNextPlayer()
    {
    	self::trace( "stNextPlayer" );
    	 
    	// Go to next player
    	$active_player = self::activeNextPlayer();
    	self::giveExtraTime( $active_player );
    
    	// Turns played statistics
    	self::incStat( 1, 'turns_number' );
    	self::incStat( 1, 'turns_number', $active_player );
    	 
    	$this->gamestate->nextState();
    }

//////////////////////////////////////////////////////////////////////////////
//////////// Zombie
////////////

    /*
        zombieTurn:
        
        This method is called each time it is the turn of a player that quit the game (= "zombie" player).
        You can do whatever you want in order to make sure the turn of this player will end
        (ex: pass).
    */

    function zombieTurn( $state, $active_player )
    {
    	$statename = $state['name'];

        if (substr($statename, 0, 6) == "player") {
            switch ($statename) {               
                default:
                    $this->gamestate->nextState( "zombiePass" );
                break;
            }

            return;
        }

        if (substr($statename, 0, 11) == "multiplayer") {
            // Make sure player is in a non blocking status for role turn
            $sql = "
                UPDATE  player
                SET     player_is_multiactive = 0
                WHERE   player_id = $active_player
            ";
            self::DbQuery( $sql );

            $this->gamestate->updateMultiactiveOrNextState( '' );
            return;
        }

        throw new feException( "Zombie mode not supported at this game state: ".$statename );
    }
   
   
}
  

