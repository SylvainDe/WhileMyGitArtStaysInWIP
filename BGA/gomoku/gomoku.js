/**
 *------
 * BGA framework: © Gregory Isabelli <gisabelli@boardgamearena.com> & Emmanuel Colin <ecolin@boardgamearena.com>
 * Gomoku implementation : © Emmanuel Colin <ecolin@boardgamearena.com>
 *
 * This code has been produced on the BGA studio platform for use on http://boardgamearena.com.
 * See http://en.boardgamearena.com/#!doc/Studio for more information.
 * -----
 *
 * gomoku.js
 *
 * Gomoku user interface script
 * 
 * In this file, you are describing the logic of your user interface, in Javascript language.
 *
 */
 
define([
    "dojo","dojo/_base/declare",
    "ebg/core/gamegui",
    "ebg/counter"
],
function (dojo, declare) {
    return declare("bgagame.gomoku", ebg.core.gamegui, {
        constructor: function(){
            console.log('gomoku constructor');
              
            // Here, you can init the global variables of your user interface
            // Example:
            // this.myGlobalValue = 0;

            // Game constants
        	this.gameConstants = null;

            // Array of current dojo connections (needed for method addEventToClass)
            this.connections = [];

        },
        
        /*
            setup:
            
            This method must set up the game user interface according to current game situation specified
            in parameter.
            
            The method is called each time the game interface is displayed to a player, ie:
            _ when the game starts
            _ when a player refreshes the game page (F5)
            
            "gamedatas" argument contains all datas retrieved by your "getAllDatas" PHP method.
        */
        
        setup: function( gamedatas )
        {
            console.log( "Starting game setup" );

            this.gameConstants = gamedatas.constants;
            
            // Setting up player boards
            for( var player_id in gamedatas.players )
            {
                var player = gamedatas.players[player_id];
                         
                // Setting up players boards if needed
                var player_board_div = $('player_board_'+player_id);
                dojo.place( this.format_block('jstpl_player_board', player ), player_board_div );
            }
            
            // Set up your game interface here, according to "gamedatas"

            // Setup intersections
            for( var id in gamedatas.intersections )
            {
                var intersection = gamedatas.intersections[id];

                dojo.place( this.format_block('jstpl_intersection', {
                    x:intersection.coord_x,
                    y:intersection.coord_y,
                    stone_type:(intersection.stone_color == null ? "no_stone" : 'stone_' + intersection.stone_color)
                } ), $ ( 'gmk_background' ) );

                var x_pix = this.getXPixelCoordinates(intersection.coord_x);
                var y_pix = this.getYPixelCoordinates(intersection.coord_y);
                
                this.slideToObjectPos( $('intersection_'+intersection.coord_x+'_'+intersection.coord_y), $('gmk_background'), x_pix, y_pix, 10 ).play();

                if (intersection.stone_color != null) {
                    // This intersection is taken, it shouldn't appear as clickable anymore
                    dojo.removeClass( 'intersection_' + intersection.coord_x + '_' + intersection.coord_y, 'clickable' );
                }
            } 

            // Init counters
            this.updateCounters(gamedatas.counters);
 
            // Tooltips
            this.addTooltipToClass( 'gmk_stoneicon_000000', _('Black'), '' );
            this.addTooltipToClass( 'gmk_stoneicon_ffffff', _('White'), '' );
 
            // Setup game notifications to handle (see "setupNotifications" method below)
            this.setupNotifications();

            // Add events on active elements (the third parameter is the method that will be called when the event defined by the second parameter happens - this method must be declared beforehand)
            this.addEventToClass( "gmk_intersection", "onclick", "onClickIntersection");

            console.log( "Ending game setup" );
        },

        getXPixelCoordinates: function( intersection_x )
        {
        	return this.gameConstants['X_ORIGIN'] + intersection_x * (this.gameConstants['INTERSECTION_WIDTH'] + this.gameConstants['INTERSECTION_X_SPACER']); 
        },
        
        getYPixelCoordinates: function( intersection_y )
        {
        	return this.gameConstants['Y_ORIGIN'] + intersection_y * (this.gameConstants['INTERSECTION_HEIGHT'] + this.gameConstants['INTERSECTION_Y_SPACER']); 
        },
       

        ///////////////////////////////////////////////////
        //// Game & client states
        
        // onEnteringState: this method is called each time we are entering into a new game state.
        //                  You can use this method to perform some user interface changes at this moment.
        //
        onEnteringState: function( stateName, args )
        {
            console.log( 'Entering state: '+stateName );
            console.log( args );
            
            switch( stateName )
            {
            
                case 'playerTurn':
                    if( this.isCurrentPlayerActive() )
                    {
                        var queueEntries = dojo.query( '.no_stone' );
	                    for(var i=0; i<queueEntries.length; i++) {
                           var isClickable = true;
                           if (args.args.tournamentOpening) {
                               var node = queueEntries[i].id;
                               var coord_x = node.split('_')[1];
                               var coord_y = node.split('_')[2];

                               if (args.args.numberOfStones == 0 && (coord_x != 9 || coord_y != 9 ) ) {
                                    isClickable = false;
                               }

                               if (args.args.numberOfStones == 1 && (coord_x < 8 || coord_x > 10 || coord_y < 8 || coord_y > 10 ) ) {
                                    isClickable = false;
                               }

                               if (args.args.numberOfStones == 2 && (coord_x > 6 && coord_x < 12 && coord_y > 6 && coord_y < 12 ) ) {
                                    isClickable = false;
                               }
                           }
                                                        
                           if (isClickable) {
    	                	   dojo.addClass( queueEntries[i], 'clickable' );
                           }
	                    }
                    }
            
            /* Example:
            
            case 'myGameState':
            
                // Show some HTML block at this game state
                dojo.style( 'my_html_block_id', 'display', 'block' );
                
                break;
           */
            }
        },

        // onLeavingState: this method is called each time we are leaving a game state.
        //                 You can use this method to perform some user interface changes at this moment.
        //
        onLeavingState: function( stateName )
        {
            console.log( 'Leaving state: '+stateName );
            
            switch( stateName )
            {
            
                case 'playerTurn':
                    if( this.isCurrentPlayerActive() )
                    {
                        var queueEntries = dojo.query( '.no_stone' );
	                    for(var i=0; i<queueEntries.length; i++) {
	                	   dojo.removeClass( queueEntries[i], 'clickable' );
	                    }
                    }

            /* Example:
            
            case 'myGameState':
            
                // Hide the HTML block we are displaying only during this game state
                dojo.style( 'my_html_block_id', 'display', 'none' );
                
                break;
           */           
            }               
        }, 

        // onUpdateActionButtons: in this method you can manage "action buttons" that are displayed in the
        //                        action status bar (ie: the HTML links in the status bar).
        //        
        onUpdateActionButtons: function( stateName, args )
        {
            console.log( 'onUpdateActionButtons: '+stateName );
                      
            if( this.isCurrentPlayerActive() )
            {
                switch( stateName )
                {

                }
            }
        },        

        ///////////////////////////////////////////////////
        //// Utility methods
        
        /*
        
            Here, you can defines some utility methods that you can use everywhere in your javascript
            script.
        
        */


        ///////////////////////////////////////////////////
        //// Player's action
        
        /*
        
            Here, you are defining methods to handle player's action (ex: results of mouse click on 
            game objects).
            
            Most of the time, these methods:
            _ check the action is possible at this game state.
            _ make a call to the game server
        
        */
        
        /* Example:
        
        onMyMethodToCall1: function( evt )
        {
            console.log( 'onMyMethodToCall1' );
            
            // Preventing default browser reaction
            dojo.stopEvent( evt );

            // Check that this action is possible (see "possibleactions" in states.inc.php)
            if( ! this.checkAction( 'myAction' ) )
            {   return; }

            this.ajaxcall( "/gomoku/gomoku/myAction.html", { 
                                                                    lock: true, 
                                                                    myArgument1: arg1, 
                                                                    myArgument2: arg2,
                                                                    ...
                                                                 }, 
                         this, function( result ) {
                            
                            // What to do after the server call if it succeeded
                            // (most of the time: nothing)
                            
                         }, function( is_error) {

                            // What to do after the server call in anyway (success or failure)
                            // (most of the time: nothing)

                         } );        
        },        
        
        */

        onClickIntersection: function( evt )
        {
            console.log( '$$$$ Event : onClickIntersection' );
            dojo.stopEvent( evt );

        	if( ! this.checkAction( 'playStone' ) )
            { return; }

            var node = evt.currentTarget.id;
            var coord_x = node.split('_')[1];
            var coord_y = node.split('_')[2];
            
            console.log( '$$$$ Selected intersection : (' + coord_x + ', ' + coord_y + ')' );
            
            if ( this.isCurrentPlayerActive() ) {
                this.ajaxcall( "/gomoku/gomoku/playStone.html", { lock: true, coord_x: coord_x, coord_y: coord_y }, this, function( result ) {}, function( is_error ) {} );
            }
        },

        
        ///////////////////////////////////////////////////
        //// Reaction to cometD notifications

        /*
            setupNotifications:
            
            In this method, you associate each of your game notifications with your local method to handle it.
            
            Note: game notification names correspond to your "notifyAllPlayers" and "notifyPlayer" calls in
                  your gomoku.game.php file.
        
        */
        setupNotifications: function()
        {
            console.log( 'notifications subscriptions setup' );
            
            // Here, associate your game notifications with local methods

            dojo.subscribe( 'stonePlayed', this, "notif_stonePlayed" );
            
            dojo.subscribe( 'finalScore', this, "notif_finalScore" );
	        this.notifqueue.setSynchronous( 'finalScore', 1500 );

            
            // Example 1: standard notification handling
            // dojo.subscribe( 'cardPlayed', this, "notif_cardPlayed" );
            
            // Example 2: standard notification handling + tell the user interface to wait
            //            during 3 seconds after calling the method in order to let the players
            //            see what is happening in the game.
            // dojo.subscribe( 'cardPlayed', this, "notif_cardPlayed" );
            // this.notifqueue.setSynchronous( 'cardPlayed', 3000 );
            // 
        },  
        
        // From this point and below, you can write your game notifications handling methods
        
        notif_stonePlayed: function( notif )
        {
	        console.log( '**** Notification : stonePlayed' );
            console.log( notif );

            // Create a stone
            dojo.place( this.format_block('jstpl_stone', {
                    stone_type:'stone_' + notif.args.color,
                    x:notif.args.coord_x,
                    y:notif.args.coord_y
                } ), $( 'intersection_' + notif.args.coord_x + '_' + notif.args.coord_y ) );

            // Place it on the player panel
            this.placeOnObject( $( 'stone_' + notif.args.coord_x + '_' + notif.args.coord_y ), $( 'player_board_' + notif.args.player_id ) );

            // Animate a slide from the player panel to the intersection
            dojo.style( 'stone_' + notif.args.coord_x + '_' + notif.args.coord_y, 'zIndex', 899 );
            var slide = this.slideToObject( $( 'stone_' + notif.args.coord_x + '_' + notif.args.coord_y ), $( 'intersection_' + notif.args.coord_x + '_' + notif.args.coord_y ), 1000 );
            dojo.connect( slide, 'onEnd', this, dojo.hitch( this, function() {
        			dojo.style( 'stone_' + notif.args.coord_x + '_' + notif.args.coord_y, 'zIndex', 'auto' );
       		}));
            slide.play();

            // This intersection is taken, it shouldn't appear as clickable anymore
            dojo.removeClass( 'intersection_' + notif.args.coord_x + '_' + notif.args.coord_y, 'clickable' );

            // Counters
	        this.updateCounters(notif.args.counters);
        },

        notif_finalScore: function( notif )
	    {
	        console.log( '**** Notification : finalScore' );
	        console.log( notif );
	      
            // Update score
            this.scoreCtrl[ notif.args.player_id ].incValue( notif.args.score_delta );
	    },

        /*
        Example:
        
        notif_cardPlayed: function( notif )
        {
            console.log( 'notif_cardPlayed' );
            console.log( notif );
            
            // Note: notif.args contains the arguments specified during you "notifyAllPlayers" / "notifyPlayer" PHP call
            
            // TODO: play the card in the user interface
        },    
        
        */
  });              
});


