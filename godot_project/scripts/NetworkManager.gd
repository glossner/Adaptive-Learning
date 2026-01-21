extends Node

signal chat_response_received(response: String, action: String)
signal session_ready(data: Dictionary)
signal error_occurred(msg: String)
signal progress_updated(xp: int, level: int, mastery: int)

var base_url = "http://127.0.0.1:8000"
var session_id = ""
var current_username = "Player1"

func _ready():
	print("NetworkManager ready")

func select_book(topic: String):
	var http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(_on_select_completed)
	
	var body = JSON.stringify({
		"username": current_username,
		"topic": topic,
		"manual_mode": GameManager.manual_selection_mode,
		"session_grade_level": GameManager.player_grade
	})
	var headers = ["Content-Type: application/json"]
	var error = http.request(base_url + "/select_book", headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		emit_signal("error_occurred", "Failed to send select request")

func _on_select_completed(_result, response_code, headers, body):
	var response_body = body.get_string_from_utf8()
	if response_code == 200:
		var json = JSON.parse_string(response_body)
		if json:
			session_id = json["session_id"]
			emit_signal("session_ready", json)
			print("Session initialized: " + session_id)
		else:
			emit_signal("error_occurred", "Failed to parse JSON")
	else:
		emit_signal("error_occurred", "Select failed: " + str(response_code))

func send_message(msg: String):
	if session_id == "":
		emit_signal("error_occurred", "No active session")
		return
		
	var http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(_on_chat_completed)
	
	var body = JSON.stringify({
		"session_id": session_id,
		"message": msg
	})
	var headers = ["Content-Type: application/json"]
	http.request(base_url + "/chat", headers, HTTPClient.METHOD_POST, body)

func _on_chat_completed(result, response_code, headers, body):
	var response_body = body.get_string_from_utf8()
	if response_code == 200:
		var json = JSON.parse_string(response_body)
		if json:
			var response_text = json["response"]
			var state = json["state_snapshot"]
			var action = state["current_action"] if state and state.has("current_action") else "IDLE"
			
			emit_signal("chat_response_received", response_text, action)
			
			# Check for mastery update
			if state.has("mastery"):
				print("NetworkManager: Progress Update Received: ", state["mastery"])
				emit_signal("progress_updated", 0, 0, int(state["mastery"]))
		else:
			emit_signal("error_occurred", "Failed to parse JSON")
	else:
		emit_signal("error_occurred", "Chat failed: " + str(response_code))

func post_request(endpoint: String, data: Dictionary, success_callback: Callable, error_callback: Callable):
	var http = HTTPRequest.new()
	add_child(http)
	
	# Connect the completion signal to a lambda or intermediate function that calls the callback
	# But Godot 4 lambdas are clean:
	http.request_completed.connect(func(result, response_code, headers, body):
		var response_body = body.get_string_from_utf8()
		if response_code == 200:
			var json = JSON.parse_string(response_body)
			if json:
				success_callback.call(response_code, json)
			else:
				error_callback.call(response_code, "Failed to parse JSON")
		else:
			error_callback.call(response_code, "Request failed: " + str(response_code))
		
		# Cleanup
		http.queue_free()
	)
	
	var body_json = JSON.stringify(data)
	var headers = ["Content-Type: application/json"]
	var error = http.request(base_url + endpoint, headers, HTTPClient.METHOD_POST, body_json)
	if error != OK:
		error_callback.call(0, "Failed to send request")
		http.queue_free()

func get_users(callback: Callable):
	var http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(func(result, code, headers, body):
		if code == 200:
			var json = JSON.parse_string(body.get_string_from_utf8())
			callback.call(json)
		else:
			callback.call([])
		http.queue_free()
	)
	http.request(base_url + "/get_users")
