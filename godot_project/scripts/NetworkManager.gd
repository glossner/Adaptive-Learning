extends Node

signal chat_response_received(response: String, action: String, state: Dictionary)
signal session_ready(data: Dictionary)
signal error_occurred(msg: String)
signal progress_updated(xp: int, level: int, mastery: int)

# PROD URL (Render)
var prod_url = "https://adaptive-learning-backend.onrender.com" # Placeholder - User should update? Or I just assume
# LOCAL URL
var local_url = "http://127.0.0.1:8000"

var base_url = ""
var session_id = ""
var current_username = "Player1"

func _ready():
	print("NetworkManager ready")
	# Detect Environment
	if OS.has_feature("editor") or OS.has_feature("debug"):
		base_url = local_url
		print("NetworkManager: Using LOCAL Backend: " + base_url)
	else:
		base_url = prod_url
		print("NetworkManager: Using PROD Backend: " + base_url)

func get_topic_graph(topic: String, success_callback: Callable, error_callback: Callable):
	var data = {
		"username": current_username,
		"topic": topic
	}
	post_request("/get_topic_graph", data, success_callback, error_callback)

func set_current_node(topic: String, node_id: String, success_callback: Callable, error_callback: Callable):
	var data = {
		"username": current_username,
		"topic": topic,
		"node_id": node_id
	}
	post_request("/set_current_node", data, success_callback, error_callback)

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

func send_message(msg: String, view_as_student: bool = false, grade_override: int = -1):
	if session_id == "":
		emit_signal("error_occurred", "No active session")
		return
		
	var http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(_on_chat_completed)
	
	var data = {
		"session_id": session_id,
		"message": msg,
		"view_as_student": view_as_student
	}
	
	if grade_override > 0:
		data["grade_override"] = grade_override
		print("NetworkManager: Custom Grade Override applied: ", grade_override)
	
	print("NetworkManager: Sending Data: ", data)
	
	var body = JSON.stringify(data)
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
			
			emit_signal("chat_response_received", response_text, action, state)
			
			# Check for mastery update
			if state.has("mastery"):
				print("NetworkManager: Progress Update Received: ", state["mastery"])
				emit_signal("progress_updated", 0, 0, state["mastery"])
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
