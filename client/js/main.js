jQuery(function($) {
  var eventMethod = window.addEventListener ? "addEventListener" : "attachEvent";
  var eventer = window[eventMethod];
  var messageEvent = eventMethod == "attachEvent" ? "onmessage" : "message";
  
  eventer(messageEvent,function(e) {
    // $("#fingerprint-iframe").addClass("hide");
    // $("#fingerprint-iframe").attr("src", "./fingerprint/details.html?" + e.data['single']);
    $("#fingerprint-button").prop('disabled', false);
    $("#fingerprint-button").html("Details");
    $("#fingerprint-button").addClass("hide");
    $("#fingerprint_result").removeClass("hide");
    $("#browser_fingerprint").html(e.data['single']);
    $("#computer_fingerprint").html(e.data['cross']);
  },false);


  //Preloader
  var preloader = $('.preloader');
  $(window).load(function(){
    preloader.remove();
  });

  //#main-slider
  var slideHeight = $(window).height();
  $('#home-slider .item').css('height',slideHeight);

	$(window).resize(function(){'use strict',
		$('#home-slider .item').css('height',slideHeight);
	});

	//Initiat WOW JS
	new WOW().init();
	//smoothScroll
	smoothScroll.init();

	//Countdown
	$('#features').bind('inview', function(event, visible, visiblePartX, visiblePartY) {
		if (visible) {
			$(this).find('.timer').each(function () {
				var $this = $(this);
				$({ Counter: 0 }).animate({ Counter: $this.text() }, {
					duration: 2000,
					easing: 'swing',
					step: function () {
						$this.text(Math.ceil(this.Counter));
					}
				});
			});
			$(this).unbind('inview');
		}
	});

  //add fingerprint iframe
  $("#fingerprint-button").click(function() {
    if ($("#fingerprint-button").text() != "Details") {
      $("#fingerprint-button").html("Running");
      $("#fingerprint-button").prop('disabled', true);
      $("#fingerprint-iframe").attr("src", "./fingerprint/index.html");
    } else {
      $("#fingerprint-result").addClass("hide");
      $("#fingerprint-button").html("Run again")
    }
    $('html, body').animate({
      scrollTop: $("#fingerprint").offset().top - 5
    }, 1000);
  });

});

