extends Node

signal chat_response_received(response: String, action: String)
signal init_success(session_id: String)
signal error_occurred(msg: String)

var base_url = "http://127.0.0.1:8000"
var session_id = ""

func _ready():
	print("NetworkManager ready")

func init_session(topic: String, grade: String):
	var http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(_on_init_completed)
	
	var body = JSON.stringify({
		"user_id": "student_1",
		"grade_level": grade,
		"topic": topic
	})
	var headers = ["Content-Type: application/json"]
	var error = http.request(base_url + "/init", headers, HTTPClient.METHOD_POST, body)
	if error != OK:
		emit_signal("error_occurred", "Failed to send init request")

func _on_init_completed(result, response_code, headers, body):
	var response_body = body.get_string_from_utf8()
	if response_code == 200:
		var json = JSON.parse_string(response_body)
		if json:
			session_id = json["session_id"]
			emit_signal("init_success", session_id)
			print("Session initialized: " + session_id)
		else:
			emit_signal("error_occurred", "Failed to parse JSON")
	else:
		emit_signal("error_occurred", "Init failed: " + str(response_code))

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
			# state_snapshot is a dict
			var action = state["current_action"] if state and state.has("current_action") else "IDLE"
			
			emit_signal("chat_response_received", response_text, action)
		else:
			emit_signal("error_occurred", "Failed to parse JSON")
	else:
		emit_signal("error_occurred", "Chat failed: " + str(response_code))
