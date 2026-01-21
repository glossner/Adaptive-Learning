extends Control

# Main UI
@onready var create_user_btn = $Panel/TopRightContainer/CreateUserButton
@onready var user_option = $Panel/MainContainer/UserOption
@onready var manual_check = $Panel/MainContainer/ManualCheck
@onready var advanced_btn = $Panel/MainContainer/AdvancedButton
@onready var start_button = $Panel/MainContainer/StartButton
@onready var status_label = $Panel/MainContainer/StatusLabel

# Advanced UI
@onready var advanced_popup = $AdvancedPopup
@onready var grade_option = $AdvancedPopup/VBox/GradeOption
@onready var location_option = $AdvancedPopup/VBox/LocationOption
@onready var style_option = $AdvancedPopup/VBox/StyleOption
@onready var save_check = $AdvancedPopup/VBox/SaveProfileCheck
@onready var close_advanced_btn = $AdvancedPopup/VBox/CloseAdvanced

func _ready():
	# Setup Dropdowns (Advanced)
	grade_option.clear()
	grade_option.add_item("Kindergarten", 0)
	for i in range(1, 13):
		grade_option.add_item("Grade " + str(i), i)
	grade_option.add_item("Undergraduate", 13)
	grade_option.add_item("Masters", 15)
	grade_option.select(5)
	
	location_option.clear()
	var locs = ["New Hampshire", "California", "Texas", "New York", "International"]
	for l in locs:
		location_option.add_item(l)
	
	style_option.clear()
	var styles = ["Visual", "Text-Based", "Auditory", "Kinesthetic"]
	for s in styles:
		style_option.add_item(s)
	
	# Connect Signals
	create_user_btn.pressed.connect(_on_create_user_pressed)
	advanced_btn.pressed.connect(_on_advanced_pressed)
	close_advanced_btn.pressed.connect(_on_close_advanced_pressed)
	start_button.pressed.connect(_on_start_pressed)
	user_option.item_selected.connect(_on_user_selected)
	
	# Load Users
	fetch_users()

func fetch_users():
	var nm = preload("res://scripts/NetworkManager.gd").new()
	add_child(nm)
	nm.get_users(func(users):
		user_option.clear()
		user_option.add_item("Select User...", 0)
		user_option.set_item_disabled(0, true)
		
		for u in users:
			user_option.add_item(u)
			
		# Try to load previous user prefs
		load_preferences(users)
		nm.queue_free()
	)

func _on_create_user_pressed():
	get_tree().change_scene_to_file("res://scenes/Registration.tscn")

func _on_advanced_pressed():
	advanced_popup.visible = true

func _on_close_advanced_pressed():
	advanced_popup.visible = false

func _on_user_selected(index):
	# Auto-load preferences for this user if we had them saved locally?
	# For now, just simplistic logic.
	pass

func _on_start_pressed():
	var user_idx = user_option.selected
	if user_idx == 0:
		status_label.text = "Please select a user!"
		return
	var username = user_option.get_item_text(user_idx)
	
	# Gather settings from Advanced (even if hidden, they hold values)
	var grade_val = grade_option.get_selected_id()
	var loc_val = location_option.get_item_text(location_option.selected)
	var style_val = style_option.get_item_text(style_option.selected)
	var do_save = save_check.button_pressed
	var is_manual = manual_check.button_pressed
	
	save_preferences(username, grade_val)
	
	status_label.text = "Initializing Session..."
	start_button.disabled = true
	
	var nm = preload("res://scripts/NetworkManager.gd").new()
	add_child(nm)
	nm.session_ready.connect(_on_session_ready)
	
	# Set global manager state
	var gm = get_node("/root/GameManager")
	if gm:
		gm.player_username = username
		gm.manual_selection_mode = is_manual
		gm.player_grade = grade_val
		
		# Sync NetworkManager
		NetworkManager.current_username = username
	
	var data = {
		"username": username,
		"grade_level": grade_val,
		"location": loc_val,
		"learning_style": style_val,
		"save_profile": do_save
	}
	
	# We use direct HTTP here as per original, or could use NM?
	# Original used HTTPRequest directly in _on_start_pressed usually, but let's stick to consistent pattern.
	# Actually originally I used NM for session ready signal but HTTP for init.
	
	var http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(func(result, code, headers, body):
		if code == 200:
			var json = JSON.parse_string(body.get_string_from_utf8())
			get_tree().change_scene_to_file("res://scenes/Library.tscn")
		else:
			status_label.text = "Error: " + str(code)
			start_button.disabled = false
	)
	
	var body_json = JSON.stringify(data)
	var headers = ["Content-Type: application/json"]
	http.request("http://127.0.0.1:8000/init_session", headers, HTTPClient.METHOD_POST, body_json)

func _on_session_ready(data):
	pass

func load_preferences(user_list):
	var config = ConfigFile.new()
	var err = config.load("user://settings.cfg")
	if err == OK:
		var saved_name = config.get_value("user", "username", "")
		# Try select user
		for i in range(user_option.item_count):
			if user_option.get_item_text(i) == saved_name:
				user_option.selected = i
				break
		
		# Load advanced settings?
		var s_grade = config.get_value("user", "grade", 10)
		# Select grade
		for i in range(grade_option.item_count):
			if grade_option.get_item_id(i) == s_grade:
				grade_option.selected = i
				break

func save_preferences(name, grade):
	var config = ConfigFile.new()
	config.set_value("user", "username", name)
	config.set_value("user", "grade", grade)
	config.save("user://settings.cfg")
