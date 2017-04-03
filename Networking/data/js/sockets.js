<script type="text/javascript" charset="utf-8">
    
	
	var socket = new io.connect('ws://localhost:8888/websocket'); 

    // Add a connect listener
    socket.on('connect',function() {
      console.log("Connected!");
    });
    // Add a connect listener
    socket.on('message',function(data) {
      //document.getElementById("ItemPreview").src = "data:image/png;base64," + data;
    });
    // Add a disconnect listener
    socket.on('disconnect',function() {
      console.log('The client has disconnected!');
    });

	
	var ws = new WebSocket("ws://" + document.domain + ":" + location.port + "/websocket");
	ws.onopen = function() {
	   console.log("Connected!");
	};
	ws.onmessage = function(evt) {
		var jsonData = JSON.parse(evt.data);
		document.getElementById("video-feed").src = "data:image/png;base64," + jsonData["image"];
		document.getElementById("target-status").innerHTML = jsonData["targetStatus"];
		document.getElementById("dart-count").innerHTML = jsonData["dartAmmo"];
		document.getElementById("ball-count").innerHTML = jsonData["ballAmmo"];
	};
	ws.onclose = function() {
		console.log("Disconeccted!");
	};
</script>