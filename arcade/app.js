// https://javascriptobfuscator.com/Javascript-Obfuscator.aspx
// One global variable to avoid polluting namespace
var BBOArcade = {};

BBOArcade['gameName'] = 'arcade0';
BBOArcade['game_loaded'] = false;
BBOArcade['queue_pending'] = [];
BBOArcade['APIServer'] = 'https://universal-leaderboard.herokuapp.com/v1';
// BBOArcade['APIServer'] = 'http://localhost:3000/v1';

// used to track board number we just played
BBOArcade['justplayedboard'] = 0;

BBOArcade['most_recent_lb'] = null;

// used for web4
// BBOArcade['resetBoardCount'] = false;

BBOArcade['userName'] = 'anon';
BBOArcade['token'] = '';
BBOArcade['score'] = 0;
BBOArcade['orien'] = '';
BBOArcade['device'] = '';
// This is needed for Android devices
BBOArcade['resizeDelay'] = 500;

BBOArcade['rank'] = 0;
// Where should we redirect on timeout?
BBOArcade['timeoutURL'] = '//www.bridgebase.com';

// language codes
BBOArcade['catalog'] = {};

// At what width should we switch between portrait and landscape
BBOArcade['widthBreak'] = 1250;

if (Modernizr.touch) {
  BBOArcade['device'] = 'mobile';
} else {
  BBOArcade['device'] = 'desktop';
}

// Are we hiding the Leaderboard?
// Toggled by Player
BBOArcade['hideLB'] = false;

BBOArcade.small_device = small_device();

// required for ad setup
BBOArcade['adGame'] = 'web0';

// Depending on device we switch layout either on orinetation change event (mobile)
// or resize event (desktop)
// Setup listeners for these events

if (false && BBOArcade['device'] === 'mobile') {
  $(window).on("orientationchange", function () {
    if (window.orientation == 0 || Math.abs(window.orientation) == 180) {
      BBO_SetLayout("portrait", function () {
        BBO_ResizeDealComponent(BBOArcade['resizeDelay']);
      });
    } else {
      BBO_SetLayout("landscape", function () {
        BBO_ResizeDealComponent(BBOArcade['resizeDelay']);
      });
    }
  });
} else { // desktop
  $(window).on("resize", function () {
    if (window.innerWidth > window.innerHeight) {
      BBO_SetLayout("landscape", function () {
        BBO_ResizeDealComponent(BBOArcade['resizeDelay']);
      });
    } else {
      BBO_SetLayout("portrait", function () {
        BBO_ResizeDealComponent(BBOArcade['resizeDelay']);
      });
    }
  });
}
// This is what kicks off the game
BBO_FireResizeEvent();
BBOArcade['game_loaded'] = true;



// The code below comes from the file web0.js
// In the older version of the arcade game is was loaded dynamically
// there is no reason to do that anymore

BBOArcade['popupURL'] = "//www.bridgebase.com/arcade/splash_web0.php";

// gpt initialization used for generate ads on client
window.googletag = window.googletag || {};
window.googletag.cmd = window.googletag.cmd || [];
googletag.cmd.push(() => {
    googletag.pubads().disableInitialLoad();
    googletag.pubads().enableSingleRequest();
    googletag.pubads().enableAsyncRendering();
    googletag.pubads().collapseEmptyDivs(true);
    googletag.enableServices();
});

// set up ads configuration for more documentation about bbo ads see https://52entertainment.atlassian.net/wiki/spaces/DOCDEV/pages/9740288031/Ads+on+BBO
// and see the PPI (Prebid Page Integration) integration guide documentation https://resources.rubiconproject.com/resource/publisher-resources/demand-manager/ppi-prebid-page-integration-guide/
window.to = [{
    // name properties is empty at the init because it will be fill by calling magnite-ad.php script
    // returning the ad rtk shortcode value composed by "RTK_" and the ad unit shortcode for example RTK_ilTg
    hbInventory: {
        type: 'AUPDivID',
        values: {
            name: "",
        },
    },
    // This means, hold a prebid auction with the ad unit code "RTK_ilTg" serving in the div above.
    hbSource: {
        type: "auction",
        values: { amazonEnabled: true }
    },
    // The means, "serve the winning ad (either from prebid or google) to the div bbo_ad1_i"
    hbDestination: {
        //If you so not wish to send prebid bids to DFP but instead render the winning 
        // prebid bid to the page, replace type:"dfp" with type:"page"
        type: "gpt",
        values: {
            div: "bbo_arcade1_ad",
            // If you need custom GPT targeting, add it here
            // targeting: { color: 'blue', interests: ['sports', 'music', 'movies'] }
        }
    }
}, {
    hbInventory: {
        type: 'AUPDivID',
        values: {
            name: "",
        },
    },
    hbSource: {
        type: "auction",
        values: { amazonEnabled: true }
    },
    hbDestination: {
        type: "gpt",
        values: {
            div: "bbo_arcade2_ad"
        }
    }
}];


var enableAutoRefresher = function() {
  var RefresherConfig = {
      enabled: true,
      interval: 90,
      awayTimeout: 240,
      userActivity: true,
      transactionObjects: window.to
  };
  window.refresher = new window.AutoRefresher(RefresherConfig);
  window.refresher.start();
  //Now you can stop the refersher at any time by calling window.refresher.stop()
}

// We do this to account for async loading of the the autorefresh script
if (window.AutoRefresherReady) {
  enableAutoRefresher();
} else {
  window.addEventListener('AutoRefresherReady', function() {
      enableAutoRefresher();
  });
}

function BBO_SetTableOptions() {
  // BBO_constructAndSendXMLToTable("jt_set_mode", ["mode"], ["stress"]);
  BBO_constructAndSendXMLToTable("jt_control", ["what", "control"], ["resize", "n"]);
  BBO_constructAndSendXMLToTable("jt_set_mode", ["mode", "human_declares"], ["arcade", "y"]);
  BBO_constructAndSendXMLToTable("jt_deal_end", ["show_all_hands", "require_click", "click_msg", "delay"], ["y", "y", BBOArcade['catalog'].AR013, "5000"]);
  BBO_constructAndSendXMLToTable("jt_set_url ", ["which", "url"], ["language", "//webutil.bridgebase.com/v2/languages/lang.php"]);
  BBO_constructAndSendXMLToTable("jt_set_url ", ["which", "url", "cookies"], ["play", "/u_bm/robot.php?botstyle=advanced","y"]);
  BBO_constructAndSendXMLToTable("jt_set_url ", ["which", "url"], ["explain", "/u_bm/u_bm.php"]);
  BBO_constructAndSendXMLToTable("jt_set_url ", ["which", "url", "cookies"], ["dealer", "/u_dealer/u_dealer.php?reuse=y", "y"]);
  BBO_constructAndSendXMLToTable("jt_manage_buttons", ["id", "command", "yours"], ["redeal", "remove", "y"]);
  BBO_constructAndSendXMLToTable("jt_customize_ui", ["what", "how"], ["show_all_cards", "y"]);
  BBO_constructAndSendXMLToTable("jt_customize_ui", ["what", "how"], ["show_auction", "y"]);
  BBO_constructAndSendXMLToTable("jt_customize_ui", ["what", "how"], ["show_vul", "y"]);
  BBO_constructAndSendXMLToTable("jt_customize_ui", ["what", "how"], ["show_contract", "y"]);
  BBO_constructAndSendXMLToTable("jt_customize_ui", ["what", "how"], ["show_trump", "n"]);
  BBO_constructAndSendXMLToTable("jt_customize_ui", ["what", "how"], ["show_legal_plays", "y"]);
  BBO_constructAndSendXMLToTable("jt_customize_ui", ["what", "how"], ["show_score", "y"]);
  BBO_constructAndSendXMLToTable("jt_customize_ui", ["what", "how"], ["show_tricks", "y"]);
  BBO_constructAndSendXMLToTable("jt_set_names", ["s", "w", "n", "e"], [BBOArcade['catalog'].AR008, BBOArcade['catalog'].AR007, BBOArcade['catalog'].AR007, BBOArcade['catalog'].AR007]);
  BBO_constructAndSendXMLToTable("jt_control", ["what", "control"], ["score", "y"]);
  BBO_constructAndSendXMLToTable("jt_control", ["what", "control"], ["dealing", "n"]);
  BBO_constructAndSendXMLToTable("jt_notify_me", ["when", "notify"], ["trick_end", "n"]);
  BBO_constructAndSendXMLToTable("jt_notify_me", ["when", "notify"], ["deal_end", "y"]);
}

function BBO_DealEnd(xmlDoc) {
  var board = xmlDoc.firstChild.getAttribute("b");
  BBOArcade['justplayedboard'] = board;

  BBO_constructAndSendXMLToTable("jt_deal_end", ["show_all_hands", "require_click", "click_msg", "delay"], ["y", "y", BBOArcade['catalog'].AR013, "5000"]);
  var score = xmlDoc.firstChild.getAttribute("total_score");
  BBO_ReportScore(score, function () {
    BBO_GetLBData();
  });
}

function BBO_SetupPlayerNameDiv(cb) {

  // Setup the playername DIV so user can enter their own player name
  $('#playercount').empty();
  $("#playercount").append('<span style="">' + BBOArcade['catalog'].AR004 + ':</span>&nbsp;<span id="numberofplayers"></span>');

  $("#playername").empty();

  // If the userName is already set then we use it. This is necessary for reconects
  if (BBOArcade['userName'] !== 'anon') {
    BBO_constructAndSendXMLToTable("jt_set_names", ["s", "w", "n", "e"], [BBOArcade['userName'], "Robot", "Robot", "Robot"]);
    BBO_ReportScore(BBOArcade['score'], function () {
      BBO_GetLBData();
    });
  } else {
    // Username Entry Field
    $("#playername").append('<form id="usernameform" action="' + BBOArcade['APIServer'] + '/setName"> <input placeholder="' + BBOArcade['catalog'].AR005 + '" autocomplete="off" size="10" id="username" name="username" type="text"><button id="gobutton" type="submit">' + BBOArcade['catalog'].AR006 + '</button>');
    $("#usernameform").on("submit", function (e) {
      var userName = $.trim($("#username").val());
      if (userName === "") {
        return false;
      }
      $("#playername").empty();
      var formURL = $(this).attr("action");

      $.ajax({
        "url": formURL,
        "method": 'POST',
        "timeout": 10000,
        "data": {
          "name": userName,
          "token": BBOArcade.token,
          "score": BBOArcade.score,
          "gameName": BBOArcade.gameName
        }
      })
        .done(function (data) {
          if (data.name == undefined) {
            console.log(data.err);
            BBOArcade.userName = 'anon';
            return BBO_SetupPlayerNameDiv(cb);
          } else {
            BBOArcade.userName = data.name;
            BBO_constructAndSendXMLToTable("jt_set_names", ["s", "w", "n", "e"], [BBOArcade.userName, "Robot", "Robot", "Robot"]);
            BBO_GetLBData();
          }
        }).fail(function () {
          BBO_constructAndSendXMLToTable("jt_set_names", ["s", "w", "n", "e"], ["Anon", "Robot", "Robot", "Robot"]);
        });
      // Stop a real submit from happening
      e.preventDefault();
    });
    
    var username = gup('u');
    if (username && username !== '') {
      $('#username').val(username);
      $("#gobutton").trigger("click");
    }
  }
  BBO_GetPlayerCount(cb);
}

function BBO_GetPlayerCount(cb) {
  $.ajax({
    "url": BBOArcade.APIServer + '/getPlayerCount',
    "method": 'POST',
    "timeout": 10000,
    "data": {
      "token": BBOArcade.token,
      "gameName": BBOArcade.gameName
    }
  })
    .done(function (data) {
      $("#numberofplayers").html(data.players);
    }).always(function () {
      cb && cb();
    });
}

function BBO_DisplayPopup() {

  if (gup("p") == "n") return;

  // Blur the main page
  BBO_Blur(1);

  var dialogOptions = {
    close: function (e, ui) {
      $(this).dialog("close");
      BBO_Blur(0);
      $("#dialog").remove();
    },
    dialogClass: "no-close",
    title: BBOArcade['catalog'].AR003,
    draggable: false,
    modal: true,
    width: parseInt($(document).width() * .60),
    height: parseInt($(document).height() * .65),
    buttons: {},
    resizable: false
  }

  // Need this trick since  left side of the JSON can't be a variable
  // The button name needs to be on the left side
  dialogOptions["buttons"][BBOArcade['catalog'].AR002] = function () { $(this).dialog('close'); };

  // load the iframe data now -- when the src was defined in the HTML it would
  // appear to soon on devices with slow internet and the page would look awkward
  $("#dialogiframe").attr("src", BBOArcade['popupURL']);
  $("#dialog").css('display', 'inherit').dialog(dialogOptions);
}

function gup(name, source) {
  name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");

  var regexS = "[\\?&]" + name + "=([^&#]*)";
  var regex = new RegExp(regexS);
  var results;

  if (source) {
    results = regex.exec(source);
  }
  else {
    results = regex.exec(window.location.href);
  }
  if (results == null)
    return "";
  else
    return results[1];
}

//
// end of web0.js code
//



// The Deal Component is hard-coded to communicate with us via
// this function name (Don't rename it!)
function BBO_ProcessIncomingXML(xmlDoc) {
  // console.log(xmlDoc);
  // This message type happens just once once on startup
  if (xmlDoc.firstChild.nodeName == "tj_loaded") {

    // Load language codes first since we will need them in place for the next steps
    BBO_LoadLanguageCodes(function () {

      // Configure Table
      BBO_SetTableOptions();
      // Show table
      BBO_constructAndSendXMLToTable("jt_show_table", null, null);
      BBO_DisplayPopup();
      BBO_BuildLeaderBoard();
    });
  }

  if (xmlDoc.firstChild.nodeName == "tj_notify") {
    var when = xmlDoc.firstChild.getAttribute("when");

    if (when == "deal_end") {
      BBO_DealEnd(xmlDoc);
    }

    // if (when=="error") {
    //   var msg = xmlDoc.firstChild.getAttribute("type");
    //   console.log('ERROR: Deal Component report error: ' + err);
    // }
  }

  if (xmlDoc.firstChild.nodeName == "tj_ready_for_deal") {
    if (BBOArcade['resetBoardCount']) {
      // reset the board count to 1
      BBO_SetTableScore(0);
      BBOArcade['justplayedboard'] = 0;
      BBO_constructAndSendXMLToTable("jt_random_deal", ["board", "constraints"], ["1", "" + " /* b=0 */ "]);
//	BBO_constructAndSendXMLToTable("jt_random_deal", ["board", "constraints"], ["1", "hcp(south)>=hcp(west)  && hcp(south)>=hcp(north) && hcp(south)>=hcp(east)" + " /* b=0 */ "]);
      BBOArcade['resetBoardCount'] = false;
    } else {
      var next_boardnumber_0_15 = (parseInt(BBOArcade['justplayedboard']) + 1 - 1) % 16;   // map all boards onto 0-15

      BBO_constructAndSendXMLToTable("jt_random_deal", ["constraints"], ["" + " /* b=" + next_boardnumber_0_15 + " */ "]);
//	BBO_constructAndSendXMLToTable("jt_random_deal", ["constraints"], ["hcp(south)>=hcp(west)  && hcp(south)>=hcp(north) && hcp(south)>=hcp(east)" + " /* b=" + next_boardnumber_0_15 + " */ "]);
    }
  }

  if (when == "button_click") {
    var which = xmlDoc.firstChild.getAttribute("which");
  }

  // if (xmlDoc.firstChild.nodeName=="tj_resize") {
  // }

  // if (when=="splash_done") {
  // }

} // BBO_ProcessIncomingXML()

function BBO_SetTableScore(score) {
  BBO_constructAndSendXMLToTable("jt_change_score", ["how", "score"], ["set", score]);
}

function BBO_DealComponentPopUp(title, msg) {
  BBO_constructAndSendXMLToTable("jt_message_box", ["id", "text", "title", "center_text", "button_1_id", "button_1_label"], ["go", msg, title, "y", "1", "OK"]);
}

function BBO_ReportScore(score, cb) {
  BBOArcade.score = score;

  $.ajax({
    "url": BBOArcade.APIServer + '/reportScore',
    "method": 'POST',
    "timeout": 10000,
    "data": {
      "token": BBOArcade.token,
      "name": BBOArcade.userName,
      "score": score,
      "gameName": BBOArcade.gameName,
      "device": BBOArcade.device
    }
  })
    .done(function (data) {
      BBOArcade.rank = data.rank;
      BBOArcade.token = data.token;
      cb & cb(data.rank);
    }).fail(function () {
      cb && cb();
    });
}

function BBO_FireResizeEvent() {
  if (false && BBOArcade['device'] === 'mobile') {
    $(window).orientationchange();
  } else {
    if (window.innerWidth > window.innerHeight) {
      BBO_SetLayout("landscape", function () {
        BBO_ResizeDealComponent(BBOArcade['resizeDelay']);
      });
    } else {
      BBO_SetLayout("portrait", function () {
        BBO_ResizeDealComponent(BBOArcade['resizeDelay']);
      });
    }
  }
}

function BBO_LoadLanguageCodes(cb) {
  // io.socket.get('/getLanguageCatalog', function (data, jwres) {
  //     BBOArcade['catalog'] = data;
  //     cb();
  // })

  BBOArcade['catalog'] = {
    "AR001": "Leaderboard",
    "AR002": "Play",
    "AR003": "Just Play Bridge",
    "AR004": "Players online",
    "AR005": "Player Name",
    "AR006": "GO",
    "AR007": "Robot",
    "AR008": "You",
    "AR009": "Bridge - 4 hands",
    "AR010": "Game Over",
    "AR011": "Score",
    "AR012": "Rank",
    "AR013": "Click to Continue",
    "AR014": "Play Again",
    "AR015": "Bridge - 4 hands"
  }

  cb();
}

function BBO_XButton() {
  // Setp LB Minimize button
  var button = $('#hidelbbtn');
  button.off('click').click(function () {
    if (BBOArcade['hideLB'] === true) {
      BBOArcade['hideLB'] = false;
      button.html("X");
      refreshbutton();
      $('.lbcontainer').show();
      BBO_FireResizeEvent();
      $.ajax({
        "url": BBOArcade.APIServer + '/openLB',
        "method": 'POST',
        "timeout": 10000,
        "data": {
          "gameName": BBOArcade.gameName
        }
      })
        .always(function (data) {
        });
    } else {
      BBOArcade['hideLB'] = true;
      button.html('+');
      refreshbutton();
      $('.lbcontainer').hide();
      BBO_ClearPlayerNameDiv(function () {
        BBO_FireResizeEvent();
        $.ajax({
          "url": BBOArcade.APIServer + '/closeLB',
          "method": 'POST',
          "timeout": 10000,
          "data": {
            "gameName": BBOArcade.gameName
          }
        })
          .always(function (data) {
          });
      });
    }
  });

  if (BBOArcade['device'] == 'mobile' && BBOArcade['hideLB'] == false && BBOArcade.small_device) {
    button.click();
  }

  refreshbutton();
  


}

function refreshbutton() {
  var button = $('#hidelbbtn');
  if ( !button ) return;
  if ( BBOArcade['device']=='desktop' && BBOArcade['orien']=='landscape' && button.html() == 'X' ) {
    button.css('display','none'); // experiment
  } else {
    button.css('display','inline-block'); // experiment
  }
}

function BBO_ClearPlayerNameDiv(cb) {
  cb();
}

function BBO_ResizeDealComponent(delay) {
  delay = delay || 0;

  setTimeout(function () {
    BBO_constructAndSendXMLToTable("jt_resize", null, null);
  }, delay);

}

// We only want to reset these CSS settings when there is an actual
// switch, not on every resize event
// Test if this is the first time through (orien === '')
// Or if the orien has changed

// Portrait requires some CSS settings that landscape does not
// and vice versa. For those settings that get set for one orientation
// but not the other we have to actively set them to 'initial' otherwise
// they stick around and cause mischief

function BBO_SetLayout(layout, cb) {

  var show_ads = true;

  if (gup('p') == 'n') {
    show_ads = false;
  }

  var frame = $("#framecontent");
  var main = $("#maincontent");
  var ad_div = $("#bbo_arcade1_ad");
  var ad_div2 = $("#bbo_arcade2_ad");


  /*
      // uday - temp - block ads for mac, safari , desktop
      if (BBOArcade['device'] !== 'mobile') {  // not mobile
          if (navigator.appVersion.indexOf("Mac") != -1) {   // mac
              var isSafari = Object.prototype.toString.call(window.HTMLElement).indexOf('Constructor') > 0 || (function (p) {
                      return p.toString() === "[object SafariRemoteNotification]";
                  })(!window['safari'] || safari.pushNotification);
              if (isSafari) {  // safari
                  ad_div.hide().empty();
                  show_ads = false;
              }
          } // mac
      }  // not mobile
  */

    var curOrientation = BBOArcade.orien;
  var curLbHeight = frame.css("height");
  var curLbWidth = frame.css("width");

  BBOArcade.orien = layout;

  const adsShortcodePromises = [];

  if (layout === 'portrait') {
    if (BBOArcade['hideLB'] === true) {
      var lbHeight = '20px';
    } else {
      lbHeight = '110px';
    }
    $('.item').css('width', '33%');

    if (curLbHeight != lbHeight) {
      frame.css({
        'left': '0px',
        'width': '100%',
        'top': 'auto',
        'height': lbHeight
      });

      main.css({
        'left': '0px',
        'right': 'initial',
        'bottom': lbHeight,
        'width': '100%'
      });
    }

    if (curOrientation != layout) {
      BBO_LeaderboardUpdate(null); // update the LB for whatever this orientation happens to be
      refreshbutton();
      if (show_ads) {
        if (BBOArcade['device'] == 'mobile') {
          if (BBOArcade.small_device) {   // as per DE , don't mess with the banner ad
            BBO_show_ad(ad_div, main, 'height', '50px', adsShortcodePromises);
          } else {
            BBO_show_ad(ad_div, main, 'height', '90px', adsShortcodePromises);
          }
        } else {
          BBO_show_ad(ad_div, main, 'height', '90px', adsShortcodePromises);
        }
      } else {  // not showing ads
        main.css('top', "0px");
        ad_div.empty();
        ad_div2.empty();
      }
    }
  } else { // layout == 'landscape'
    if (BBOArcade.device == 'mobile' && BBOArcade.small_device) {
      show_ads = false;
    }
    var lbWidth = '160px';
    if (BBOArcade['hideLB'] === true) {
      lbWidth = '15px';
    } else if (BBOArcade.device == 'desktop') {
      lbWidth = '300px';
    }
    $('.item').css('width', '100%');
    if (lbWidth != curLbWidth) {
      frame.css({
        'top': '0',
        'width': lbWidth,
        'height': '100%',
        'left': 'auto'
      });
      main.css({
        'top': '0px',
        // .css('left': '160px',
        'right': lbWidth,
        'bottom': '0px',
        // in this case auto seemed to work better than initial
        // not sure why
        'width': 'auto'
      });
    }
    ad_div.css({
      'height': "100%",
      'overflow-y': 'hidden'
    });
    ad_div2.css({
      'width': "300px",
      'height': "250px",
      'margin-top': "10px",
      'overflow-y': 'hidden'
    });


    if (curOrientation != layout) {
      BBO_LeaderboardUpdate(null); // update the LB for whatever this orientation happens to be
      refreshbutton();
      if (show_ads) {
        if (BBOArcade['device'] == 'mobile') {
          if (BBOArcade.small_device) {
            BBO_show_ad(ad_div, main, 'width', '120px', adsShortcodePromises);
          } else {
            BBO_show_ad(ad_div, main, 'width', '160px', adsShortcodePromises);
          }
        }
        else {
          BBO_show_ad(ad_div, main, 'width', '160px', adsShortcodePromises);
          if ( BBOArcade['device'] == 'desktop' &&  BBOArcade['orien'] == 'landscape' ) {
            BBO_show_ad2(adsShortcodePromises);
          }
        }
      } else { // not showing ads
        main.css('left', "0px");
        if (window.refresher) {
          window.refresher.stop();
        }
        ad_div.empty();
        ad_div2.empty();
      }
    }

  }
  if (adsShortcodePromises.length > 0) {
    Promise.all(adsShortcodePromises).then((resultList) => {
      const ad1Result = resultList[0];
      if (ad1Result.result && !ad1Result.error) {
        window.to[0].hbInventory.values.name = "RTK_" + ad1Result.result.ad_unit_shortcode;
      } else {
        console.error(ad1Result.error);
      }
      if (resultList[1]) {
        const ad2Result = resultList[1];
        if (ad2Result.result && !ad2Result.error) {
          window.to[1].hbInventory.values.name = "RTK_" + ad2Result.result.ad_unit_shortcode;
        } else {
          console.error(ad2Result.error);
        }
      }
      window.refresher.config.transactionObjects = window.to;
      // Once hbInventory values are set we can request bids
      window.pbjs = window.pbjs || {};
      window.pbjs.que = window.pbjs.que || [];
      window.pbjs.que.push(function () {
        window.pbjs.ppi.requestBids(window.to);
      });
      window.refresher.start(); // in case we previously stopped ads
    });
  }
  cb && cb();
}
function landscape_height(fallback) {
  if (!navigator) return fallback;

  // if landscape and iphone, cater to ios-Safari bug that pretends viewport is taller than it actually is
  //
  //  https://bugs.webkit.org/show_bug.cgi?id=141832
  //

  if (navigator.platform && (window.innerWidth > window.innerHeight) && (navigator.platform.indexOf("iPhone") != -1)) {
    if (window.innerHeight == 414) return "370px";
    if (window.innerHeight == 375) return "331px";
    if (window.innerHeight == 320) return "212px";
  }
  //if (window.innerWidth > window.innerHeight)
  return fallback;

}

function small_device() {


  // https://www.paintcodeapp.com/news/iphone-6-screens-demystified
  //
  // http://stackoverflow.com/questions/1038727/how-to-get-browser-width-using-javascript-code

  var w, h, smaller;

  if (BBOArcade['device'] == 'mobile') {
    var ratio = window.devicePixelRatio || 1;
    w = screen.width * ratio;   // width in rendered pixels
    h = screen.height * ratio;  // height in rendered pixels
  } else {
    w = $(window).width();
    h = $(window).height();
  }
  smaller = (w < h) ? w : h;
  //console.log("smaller dimension = " + smaller);
  return (smaller < 728);
}


function BBO_Blur(v) {
  return;  // blur triggers a weird bug in IOS mobile safari. overflow:hidden stops working on card stack and dummy  2016-09-20
  // var filterVal = 'blur(' + v + 'px )';
  // $("#framecontentLeft, #framecontentRight, #maincontent")
  //     .css('filter',filterVal)
  //     .css('webkitFilter',filterVal)
  //     .css('mozFilter',filterVal)
  //     .css('oFilter',filterVal)
  //     .css('msFilter',filterVal);
}

function BBO_BuildLeaderBoard() {
  BBO_GetToken(function () {
    BBO_SetupPlayerNameDiv(function () {
      BBO_GetLBData(function () {
        BBO_XButton();
      });
    });
  });
}

function BBO_GetLBData(cb) {
  // Ask for the leaderboard the first time
  // After the first time we will get update messages from server

  $.ajax({
    "url": BBOArcade.APIServer + '/getTopXUsers',
    "method": 'POST',
    "timeout": 5000,
    "data": {
      "gameName": BBOArcade.gameName
    }
  })
    .done(function (data) {
      BBO_LeaderboardUpdate(data.leaders);
      BBO_GetPlayerCount(cb);
    }).fail(function () {
      BBO_GetPlayerCount(cb);
    });
}

function BBO_GetToken(cb) {

  $.ajax({
    url: BBOArcade.APIServer + '/auth',
    method: 'POST',
    timeout: 10000,
    data: { gameName: BBOArcade.gameName }
  })
    .done(function (data) {
      BBOArcade.token = data.token;
      cb && cb();
    }).fail(function () {
      cb && cb();
    });
}

function BBO_LeaderboardUpdate(lb) {
  var counter = 1;
  var numCols = 2;
  var tdClass = '';
  var lineText = '';

  if ( lb == null ) {
    lb = BBOArcade['most_recent_lb'];
  } else {
    BBOArcade['most_recent_lb']  = lb;
  }
  
  if ( lb === null )  return; 

  $("#lbtable").empty();
  //$('#lbtable').append('<div class="block leaderboard">' + BBOArcade['catalog'].AR001 + '</div>');

  lb.forEach(function (currentValue, index, fullArray) {

    if (!(index % numCols)) {
      tdClass = (fullArray[index] === BBOArcade['userName']) ? 'tdhighlight' : 'tdnohighlight';
      lineText = build_lbline(BBOArcade['device'], BBOArcade['orien'], counter,sanitizeString(fullArray[index],20), sanitizeString(fullArray[index+1],7));
      counter++;
      $('#lbtable').append('<div class="item block ' + tdClass + '">' + lineText + '</div>');
    }
  }, null);

  // Each LB entry has two values in the LB array so divide length by 2
  BBO_AddPlayerRank(BBOArcade['rank'], BBOArcade['score'], BBOArcade['userName'], (lb.length / 2), function () {
    // BBO_HighlightMyName(BBOArcade['userName'], function() {
    // Adjust pocketgrid item width
    if (BBOArcade['orien'] === 'landscape') {
      $('.item').css('width', '100%');
    } else {
      $('.item').css('width', '33%');
    }
  });
}

function build_lbline(device, orientation, rank, name, score) {
  var lineText='';

  if ( device == 'desktop' && orientation == 'landscape' )  {
    lineText = '';
    lineText = lineText + '<span style="display:inline-block;margin-left:18px;width:17px;padding-left:0px;font-family:Helvetica Neue Regular;">' + rank + '</span>' ;
    lineText = lineText + '<span style="display:inline-block;margin-left:30px;width:99px;padding-left:0px;font-family:Helvetica Neue Regular;">' + name + '</span>' ;
    lineText = lineText + '<span style="display:inline-block;margin-left:50px;width:71px;padding-left:0px;font-family:Helvetica Neue Regular;">' + score + '</span>' ;

  } else {
    lineText = rank + '. ' + name + ' ' + score;
  }

  return lineText;
}

function BBO_AddPlayerRank(rank, score, userName, LBLength, cb) {
  // If the player's rank is greater than the number of spots on the LB
  // then replace the last spot on the LB with this player and their rank
  // console.log('BBO_AddPlayerRank: rank:' + rank + ' score: ' + score + ' userName: ' + userName + ' length: ' + LBLength);
  if (rank > LBLength && userName !== 'anon' && userName) {
    if ( BBOArcade['device'] == 'desktop' && BBOArcade['orien'] == 'landscape' )  {
      var lineText = '';
      lineText = lineText + '<span style="display:inline-block;margin-left:18px;width:17px;padding-left:0px;font-family:Helvetica Neue Regular;">' + rank + '</span>' ;
      lineText = lineText + '<span style="display:inline-block;margin-left:30px;width:99px;padding-left:0px;font-family:Helvetica Neue Regular;">' + userName + '</span>' ;
      lineText = lineText + '<span style="display:inline-block;margin-left:50px;width:71px;padding-left:0px;font-family:Helvetica Neue Regular;">' + score + '</span>' ;      
      $('#lbtable > div').last().html( lineText );
    } else {
      $('#lbtable > div').last().html(rank + '. ' + userName + ' ' + score);
    }



  }
  cb();
}


// All functions below are expected by the Deal Component in order to communicate
// back and forth

function BBO_XMLToString(xml) {
  var xmlString;
  if (window.ActiveXObject)
    xmlString = xml.xml;
  else
    xmlString = (new XMLSerializer()).serializeToString(xml);
  return xmlString;
}

function BBO_XMLFromString(xmlString) {
  var xmlDoc;
  if (window.ActiveXObject) {
    xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
    xmlDoc.async = false;
    xmlDoc.loadXML(xmlString);
  } else {
    parser = new DOMParser();
    xmlDoc = parser.parseFromString(xmlString, "text/xml");
  }
  return xmlDoc;
}

function BBO_XMLFromTable(xml) {

  /*
   *   This function simply  converts the incoming string into an xmlDoc and passes it to BBO_ProcessIncomingXML
   *
   *   The complication is that BBO_ProcessIncomingXML in turn relies upon game0.js ( or game4.js ) having loaded, and there is a race condition
   *
   *   So we put the incoming xml into a FIFO queue, and if the game[04].js file isn't ready, we try again later via setTimeout
  */


  var WAIT_FOR_GAME_TIMER_INTERVAL = 1000 * 1;

  if (xml !== null) {  // the setTimeout call to this function uses a null parm, fwiw
    BBOArcade['queue_pending'].push(xml);
  }

  if (BBOArcade['queue_pending'].length == 0) {
    return;
  }

  // some work in queue.  Is game ready?
  if (!(typeof BBO_ProcessIncomingXML == "function" && BBOArcade['game_loaded'] == true)) {  // not ready. check later
    if (xml == null || BBOArcade['queue_pending'].length == 1) {  // so that we only have one timer event
      setTimeout(function () { BBO_XMLFromTable(null); }, WAIT_FOR_GAME_TIMER_INTERVAL)
    }
    return;
  }

  // Game ready, and some jobs in queue.
  while (BBOArcade['queue_pending'].length > 0) {
    xml = BBOArcade['queue_pending'].shift();
    var xmlDoc = BBO_XMLFromString(xml);
    BBO_ProcessIncomingXML(xmlDoc);
  }


}

function BBO_XMLToTable(xml) {
  var xmlString = BBO_XMLToString(xml);
  if (window.BBO_XMLReceivedFromJS) {
    window.BBO_XMLReceivedFromJS(xmlString);
  }
}

function BBO_constructAndSendXMLToTable(name, attributes, values) {
  var xmlDoc = BBO_XMLFromString("<" + name + "/>");
  if (attributes != null && values != null && attributes.length == values.length) {
    for (var index = 0; index < attributes.length; index++) {
      xmlDoc.firstChild.setAttribute(attributes[index], values[index]);
    }
  }
  BBO_XMLToTable(xmlDoc);
}

function BBO_show_ad2(adsShortcodePromises){
  var url = '//ads.bridgebase.com/common/ads/magnite-ad.php?g=' + BBOArcade.adGame + '&d=desktop&o=landscape2';
  adsShortcodePromises.push($.get(url));
}

function BBO_show_ad(ad_div, main_div, ad_style_param, style_value, adsShortcodePromises) {
  var device;
  if (BBOArcade.device == 'mobile') {
    device = BBOArcade.small_device ? 'phone' : 'tablet';
  } else {
    device = 'desktop';
  }
  var url = '//ads.bridgebase.com/common/ads/magnite-ad.php?g=' + BBOArcade.adGame + '&d=' + device + '&o=' + BBOArcade.orien;
  adsShortcodePromises.push($.get(url));
  
  var ad_style, maincontent_style;
  if (ad_style_param == 'height') {
    ad_style = { height: style_value, width: '' };
    maincontent_style = { top: style_value };
  } else {
    ad_style = { width: style_value, height: '100%' };
    maincontent_style = { left: style_value };
  }
  ad_div.css(ad_style);
  main_div.css(maincontent_style);
}

function gup(name, source) {
  name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");

  var regexS = "[\\?&]" + name + "=([^&#]*)";
  var regex = new RegExp(regexS);
  var results;

  if (source) {
    results = regex.exec(source);
  }
  else {
    results = regex.exec(window.location.href);
  }
  if (results == null)
    return "";
  else
    return results[1];
}

function sanitizeString(str,max){
  if ( typeof str === 'string' ) {
      str = str.replace(/[^a-z0-9 \.,_-]/gim,"?");
      return str.trim().slice(0,max);
  } else {
      return '?';
  }
}
