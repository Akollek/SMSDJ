
function update_playing(snapshot){
    if (! snapshot.val() ){
        $('#now-playing').html('');
        return;
    } 
    console.log(snapshot.val());
    console.log(Object.keys(snapshot.val())[0]);
    playing = snapshot.val()[Object.keys(snapshot.val())[0]];
    $('#now-playing').html(playing); 
}


function update_queue(snapshot){
    if (! snapshot.val() ){
        $('#queue').html('');
        return;
    } 
    queue =  snapshot.val()[Object.keys(snapshot.val())[0]];
    html = "";
    
    for( var i=0, len = queue.length; i<len; i++){
        html = html + 
            "<li> "+queue[i] +"</li>";
    }
    
    $('#queue').html(html);
}



$(document).ready(function(){
    var playing_ref =  new Firebase('https://sms-dj.firebaseio.com/playing')
    playing_ref.on('value', update_playing);
        
    var queue_ref = new Firebase('https://sms-dj.firebaseio.com/queue')
    queue_ref.on('value', update_queue);

});
     
