{OVERALL_GAME_HEADER}

<!-- 
--------
-- BGA framework: © Gregory Isabelli <gisabelli@boardgamearena.com> & Emmanuel Colin <ecolin@boardgamearena.com>
-- Gomoku implementation : © Emmanuel Colin <ecolin@boardgamearena.com>
-- 
-- This code has been produced on the BGA studio platform for use on http://boardgamearena.com.
-- See http://en.boardgamearena.com/#!doc/Studio for more information.
-------

    gomoku_gomoku.tpl
    
    This is the HTML template of your game.
    
    Everything you are writing in this file will be displayed in the HTML page of your game user interface,
    in the "main game zone" of the screen.
    
    You can use in this template:
    _ variables, with the format {MY_VARIABLE_ELEMENT}.
    _ HTML block, with the BEGIN/END format
    
    See your "view" PHP file to check how to set variables and control blocks
-->


<div id="gmk_game_area">
	<div id="gmk_background">
		<div id="gmk_goban">
		</div>
	</div>	
</div>


<script type="text/javascript">

// Javascript HTML templates

/*
// Example:
var jstpl_some_game_item='<div class="my_game_item" id="my_game_item_${id}"></div>';

*/

var jstpl_intersection='<div class="gmk_intersection ${stone_type}" id="intersection_${x}_${y}"></div>';

var jstpl_stone='<div class="gmk_stone ${stone_type}" id="stone_${x}_${y}"></div>';

// Templates
var jstpl_player_board = '\<div class="cp_board">\
    <div id="stoneicon_p${id}" class="gmk_stoneicon gmk_stoneicon_${color}"></div><span id="stonecount_p${id}">0</span>\
</div>';

</script>  

{OVERALL_GAME_FOOTER}
