extends Node

signal chat_response_received(response: String, action: String, state: Dictionary)
signal session_ready(data: Dictionary)
signal error_occurred(msg: String)
signal progress_updated(xp: int, level: int, mastery: int)

# PROD URL (Render)
var prod_url = "https://placeholder-backend.onrender.com" # Updated via Secrets.gd
# LOCAL URL
var local_url = "http://127.0.0.1:8000"

var base_url = ""
var session_id = ""
var current_username = "Player1"
var auth_token = ""


func _ready():
	print("NetworkManager ready")
	# Detect Environment
	if OS.has_feature("editor") or OS.has_feature("debug"):
		base_url = local_url
		print("NetworkManager: Using LOCAL Backend: " + base_url)
		# check for Secrets class
		var secrets_script = load("res://scripts/Secrets.gd")
		if secrets_script:
			# Try to get constant directly from script map or instance
			var inst = secrets_script.new()
			if "PROD_URL" in inst:
				prod_url = inst.PROD_URL
				# But typically consts are not props.
				# Let's try getting it from the script constants map
				var constants = secrets_script.get_script_constant_map()
				if constants.has("PROD_URL"):
					prod_url = constants["PROD_URL"]
		
		# Secrets loaded (prod_url updated), but keep base_url = local_url for now.
		# base_url = prod_url # ERROR: Do not overwrite local_url here!
	else:
		# Prod / Exported Build
		base_url = prod_url
		print("NetworkManager: Using PROD Backend: " + base_url)

# Helper to construct headers with Auth
func _get_headers() -> PackedStringArray:
	var headers = [
		"Content-Type: application/json",
		"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
		"Accept: application/json, text/plain, */*",
		"Connection: keep-alive"
	]
	# If we have a token, add it
	if auth_token != "":
		headers.append("Authorization: Bearer " + auth_token)
	return PackedStringArray(headers)

# Updated Login Handler (External scripts call this endpoint, but we should intercept the response structure if possible?
# ACTUALLY, Startup.gd makes the login call directly using HTTPRequest.
# NetworkManager does NOT have a 'login' function. It has 'send_message', 'select_book', etc.
# BUT Startup.gd does NOT store the token in NetworkManager.
# I MUST update Startup.gd to Set the token in NetworkManager after login success.
# AND I must update NetworkManager to USE that token.

# So first, let's update NetworkManager to USE it.

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
	
	# USE NEW HEADER HELPER
	var headers = _get_headers()
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
	
	var body = JSON.stringify(data)
	var headers = _get_headers()
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

func post_request(endpoint: String, data: Dictionary, success_callback: Callable, error_callback: Callable):
	var http = HTTPRequest.new()
	add_child(http)
	
	http.request_completed.connect(func(result, response_code, headers, body):
		var response_body = body.get_string_from_utf8()
		if response_code == 200:
			var json = JSON.parse_string(response_body)
			if json:
				success_callback.call(response_code, json)
		else:
			# Pass error code
			error_callback.call(response_code, "Request failed: " + str(response_code))
		http.queue_free()
	)
	
	var body_json = JSON.stringify(data)
	var headers = _get_headers()
	var error = http.request(base_url + endpoint, headers, HTTPClient.METHOD_POST, body_json)
	if error != OK:
		error_callback.call(0, "Failed to send request")
		http.queue_free()

func get_users(callback: Callable):
	# Public Endpoint? Usually. If protected, we need headers.
	# get_users list should probably be public or requires Basic Auth?
	# Implementation plan said secure sensitive endpoints. GET /get_users was not explicitly listed.
	# But if we secure everything, we might lock ourselves out of the "Login" dropdown.
	# Let's assume /get_users is PUBLIC for now (to populate the list).
	var http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(func(result, code, headers, body):
		# Just check success class.
		if code >= 200 and code < 300:
			callback.call(true)
			print("Response Headers: ", headers)
			print("Response Body: ", body.get_string_from_utf8())
		else:
			callback.call(false)
		http.queue_free()
	)
