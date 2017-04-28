var source_result = $("#search-result-template").html();
var template_result = Handlebars.compile(source_result);
var source_playlist = $("#playlist-template").html();
var template_playlist = Handlebars.compile(source_playlist);

var search_result = [];
var playlist = [];
var current_track = {};
var volume=0;
// playing,paused,stopped
var state="stopped";
var host; 
var ws; 
host=window.location.host;
ws=new WebSocket('ws://' + host + '/ws');

ws.onopen = function() {
    //$message.attr("class", 'label label-success');
    //$message.text('open');
};

ws.onmessage = function(ev) {
    var json = JSON.parse(ev.data);
    //alert(json.command);
    if (json.command === "playlist_changed") {
        playlist = json.payload;
        updatePlaylist();
    }else if (json.command === "current_changed"){
        current_track=json.payload;
        updateCurrent();
    }else if (json.command === "state_changed"){
        state=json.payload;
        updateState();
    }else if (json.command === "volume_changed"){
        volume=json.payload;
        updateVolume();
    }else if (json.command === "init_state"){
        init_state=json.payload;
        state=init_state.state;
        current_track=init_state.current_track;
        playlist=init_state.playlist;
        volume=init_state.volume;
        updatePlaylist();
        updateCurrent();
        updateVolume();
        updateState();
    }
};

ws.onclose = function(ev) {
    //$message.attr("class", 'label label-important');
    //$message.text('closed');
};
ws.onerror = function(ev) {
    //$message.attr("class", 'label label-warning');
    //$message.text('error occurred');
};

$(document).ready(function() {
  setTimeout(function(){
  updateState();
  $("#btnPrevious").prop('disabled', false);
  $("#btnNext").prop('disabled', false);
  ws.send(JSON.stringify({ 'init_state': null}));
   },2000);
});

$('#yt_search').keypress(function (e) {
 var key = e.which;
 if(key == 13)  // the enter key code
  {
    $('#btn-search').click();
    return false;  
  }
});   

function search() {
    var query = $('#yt_search').val();
    $.ajax({
        contentType: 'application/json',
        data: JSON.stringify({
            "q": query
        }),
        dataType: 'json',
        success: function(data) {
            search_result = data.results;
            var html = template_result(data.results);
            $("#yt_search_results").html(html);
        },
        error: function() {
            console.log("Device control failed");
        },
        processData: false,
        type: 'POST',
        url: '/api'
    });
}

function play(){
	if ($.isEmptyObject(current_track) && playlist.length>0){
		ws.send(JSON.stringify({ 'play': playlist[0] }));
	}else if (state!="playing"){
		ws.send(JSON.stringify({ 'play': null }));
	}
}

function pause(){
	if (state=="playing"){
		ws.send(JSON.stringify({ 'pause': null }));
	}
}

function mute(level){
    ws.send(JSON.stringify({ 'mute': null}));
}

function incrementVolume(level){
    ws.send(JSON.stringify({ 'increment_volume': null}));
}

function decrementVolume(level){
    ws.send(JSON.stringify({ 'decrement_volume': null}));
}

function next(){
	ws.send(JSON.stringify({ 'next': null }));
}

function previous(){
	ws.send(JSON.stringify({ 'previous': null }));
}

function selectSong(url){
	var track = getTrackFromPlaylist(url);
	if (track){
		changeTrack(track);
	}
}

function changeTrack(track){
	ws.send(JSON.stringify({ 'play': track }));
}

function updateCurrent(){
	var id= current_track.id;
	if (id){
	$(".playlist-track").removeClass("active");
	$("#"+id).addClass("active");
	}
}
function updateState(){
	if (state=="playing"){
		$("#btnPlay").prop('disabled', true);
		$("#btnPause").prop('disabled', false);
        $("#status").text("Playing: " + current_track.title);
	}else if (state=="paused"){
		$("#btnPlay").prop('disabled', false);
		$("#btnPause").prop('disabled', true);
        $("#status").text("Paused");
	}else if (state=="stopped"){
		$("#btnPlay").prop('disabled', false);
		$("#btnPause").prop('disabled', true);
        $("#status").text("Stopped");
	}
}

function clearSearch() {
    $("#yt_search_results").html("");
    $('#yt_search').val("");
}

function updatePlaylist() {
    if (playlist.length>0){
        var html = template_playlist(playlist);
        $("#playlist").html(html);
        updateCurrent();
    }else{
        var empty='<li class="list-group-item disabled">Playlist is empty</li>';
        $("#playlist").html(empty);
    }
}

function updateVolume(){
    var volume_string=volume;
    if (volume===0){
        volume_string="Muted"
    }
    $("#volume-status").text("Volume: "+volume_string);
}



function getTrackByUrl(list,url){
	var tracks = list.filter(function(element) {
        return element.url == url; });
    if (tracks.length > 0) {
    	return tracks[0];
    }
}

function getTrackFromSearchResults(url){
	return getTrackByUrl(search_result,url);
}

function getTrackFromPlaylist(url){
	return getTrackByUrl(playlist,url);
}

function addToPlaylist(url) {
	var track = getTrackFromSearchResults(url);
	if (track){
		ws.send(JSON.stringify({ 'add_track': track }));
	}
}

function removeFromPlaylist(url) {
	var track = getTrackFromPlaylist(url);
    ws.send(JSON.stringify({ 'remove_track': track }));
}

Handlebars.registerHelper("inc", function(value, options)
{
    return parseInt(value) + 1;
});