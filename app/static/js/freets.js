$(document).ready(function(){   
  $('.dropdown-button').dropdown({ hover: false });
  $(".button-collapse").sideNav();
  $('select').material_select();
  $('.parallax').parallax();
  $('.collapsible').collapsible({
    accordion : true
  });
 $('.datepicker').pickadate({
    format: 'dddd mmmm dd',
    selectMonths: false,
    selectYears: true
  });
 $('.timepicker').pickatime({
    format: 'h:i A'
  });
});


