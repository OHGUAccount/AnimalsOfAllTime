$(document).ready(function(){
  // Just declare upvote, upvoted, downvote or downvoted 
  // for the button's class and jquery will style them automatically!
  $(".upvote, .downvote").addClass("btn btn-outline-secondary border-0");
  $(".upvoted").addClass("btn btn-outline-danger border-0");
  $(".downvoted").addClass("btn btn-outline-primary border-0");

  // From upvote to upvoted
  $(document).on('click', '.upvote', function(){
    var upvote_id = $(this).attr('id');
    var downvote_id = upvote_id.replace('upvote', 'downvote');
    var $downvote = $('#' + downvote_id);
    $downvote.removeClass("downvoted btn-outline-primary");
    $downvote.addClass('downvote btn-outline-secondary');
    $(this).removeClass("upvote btn-outline-secondary");
    $(this).addClass("upvoted btn-outline-danger");
  });

  // From downvote to downvoted
  $(document).on('click', '.downvote', function(){
    var downvote_id = $(this).attr('id');
    var upvote_id = downvote_id.replace('downvote', 'upvote');
    var $upvote = $('#' + upvote_id);
    $upvote.removeClass("upvoted btn-outline-danger");
    $upvote.addClass('upvote btn-outline-secondary');
    $(this).removeClass("downvote btn-outline-secondary");
    $(this).addClass("downvoted btn-outline-primary");
  });

  // From upvoted to upvote
  $(document).on('click', '.upvoted', function(){
    $(this).removeClass("upvoted btn-outline-danger");
    $(this).addClass("upvote btn-outline-secondary");
  });

  // From downvoted to dowvote
  $(document).on('click', '.downvoted', function(){
    $(this).removeClass("downvoted btn-outline-primary");
    $(this).addClass("downvote btn-outline-secondary");
  });
});
