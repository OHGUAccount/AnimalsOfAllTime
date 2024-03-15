const UPVOTE_CLASS = "btn-outline-danger";
const DOWNVOTE_CLASS = "btn-outline-primary";
const NORMAL_CLASS = "btn-outline-secondary";


function updateUpvote(upvote) {
  var upvoteID = $(upvote).attr('id');
  var downvoteID = upvoteID.replace('upvote', 'downvote');
  var $downvote = $('#' + downvoteID);
  $downvote.attr('data-status', 'downvote');
  $downvote.removeClass(DOWNVOTE_CLASS);
  $downvote.addClass(NORMAL_CLASS);

  $(upvote).attr('data-status', 'upvoted');
  $(upvote).removeClass(NORMAL_CLASS);
  $(upvote).addClass(UPVOTE_CLASS);
}

function updateDownvote(downvote) {
  var downvoteID = $(downvote).attr('id');
  var upvoteID = downvoteID.replace('downvote', 'upvote');
  var $upvote = $('#' + upvoteID);
  $upvote.attr('data-status', 'upvote');
  $upvote.removeClass(UPVOTE_CLASS);
  $upvote.addClass(NORMAL_CLASS);
  
  $(downvote).attr('data-status', 'downvoted');
  $(downvote).removeClass(NORMAL_CLASS);
  $(downvote).addClass(DOWNVOTE_CLASS);
}

function updateUpvoted(upvoted) {
  $(upvoted).attr('data-status', 'upvote');
  $(upvoted).removeClass(UPVOTE_CLASS);
  $(upvoted).addClass(NORMAL_CLASS);
}

function updateDownvoted(downvoted) {
  $(downvoted).attr('data-status', 'downvote');
  $(downvoted).removeClass(DOWNVOTE_CLASS);
  $(downvoted).addClass(NORMAL_CLASS);
}

function updateButton(voteButton) {
  var dataStatus = $(voteButton).attr('data-status');
  switch (dataStatus) {
    case 'upvote':
      updateUpvote(voteButton);
      break;
    case 'downvote':
      updateDownvote(voteButton);
      break;
    case 'upvoted':
      updateUpvoted(voteButton);
      break; 
    case 'downvoted':
      updateDownvoted(voteButton);
      break; 
  }
}

function updateCount(voteButton, newCount){
  var buttonID = $(voteButton).attr('id');
  if (buttonID.includes('upvote')) {
    var countID = buttonID.replace('upvote', 'count');
  }
  else {
    var countID = buttonID.replace('downvote', 'count');
  }
  var $countElm = $('#' + countID);
  $countElm.text(newCount);    
}


$(document).ready(function(){
  $(".vote").addClass("btn btn-outline-secondary border-0");

  $(document).on('click', '.vote', function(){
    var voteButton = this;
    $.ajax({
      url: '/wildthoughts/vote/',
      type: 'GET',
      data: {
          'category': $(this).attr('data-category'),
          'id': $(this).attr('data-id'),
          'status': $(this).attr('data-status')
      },
      success: function(response) {
          console.log("working");
          if(response.status === 'success') {
            updateButton(voteButton); 
            updateCount(voteButton, response.count); 
          }
      },
    })
  });  
});
