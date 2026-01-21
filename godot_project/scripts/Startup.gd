extends Control

@onready var username_input = $VBoxContainer/UsernameInput
@onready var grade_option = $VBoxContainer/GradeOption
@onready var location_option = $VBoxContainer/LocationOption
@onready var style_option = $VBoxContainer/StyleOption
@onready var start_button = $VBoxContainer/StartButton
@onready var status_label = $VBoxContainer/StatusLabel

var user_option: OptionButton

func _ready():
	# 1. Setup User Selection UI
	setup_user_ui()
	
	# Populate Grade Options
	grade_option.clear()
	grade_option.add_item("Kindergarten", 0)
	for i in range(1, 13):
		grade_option.add_item("Grade " + str(i), i)
	grade_option.add_item("Undergraduate", 13)
	grade_option.add_item("Masters", 15)
	grade_option.select(5)
	
	# Populate Location (Sample)
	location_option.clear()
	var locs = ["New Hampshire", "California", "Texas", "New York", "International"]
	for l in locs:
		location_option.add_item(l)
	
	# Populate Styles
	style_option.clear()
	var styles = ["Visual", "Text-Based", "Auditory", "Kinesthetic"]
	for s in styles:
		style_option.add_item(s)
		
	# Manual Selection Option
	var manual_check = CheckBox.new()
	manual_check.text = "Let me choose (Disable Adaptive Defaults)"
	$VBoxContainer.add_child(manual_check)
	$VBoxContainer.move_child(manual_check, $VBoxContainer.get_child_count() - 3)
	manual_check.name = "ManualSelectCheck"
	
	# Header
	var header = Label.new()
	header.text = "USER PROFILE SETTINGS"
	header.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	header.add_theme_font_size_override("font_size", 24)
	$VBoxContainer.add_child(header)
	$VBoxContainer.move_child(header, 0)
	
	# Save Profile Checkbox
	var save_check = CheckBox.new()
	save_check.text = "Update Saved Profile?"
	save_check.button_pressed = false 
	save_check.name = "SaveProfileCheck"
	$VBoxContainer.add_child(save_check)
	$VBoxContainer.move_child(save_check, $VBoxContainer.get_child_count() - 3)
	
	# Load User Data
	fetch_users()
	
	# Connect buttons
	if start_button:
		start_button.text = "Start Session"
		start_button.pressed.connect(_on_start_pressed)

func setup_user_ui():
	# Hide original input initially
	if username_input:
		username_input.visible = false
	
	user_option = OptionButton.new()
	user_option.item_selected.connect(_on_user_selected)
	$VBoxContainer.add_child(user_option)
	if username_input:
		$VBoxContainer.move_child(user_option, username_input.get_index()) # Place where input was
	
func fetch_users():
	var nm = preload("res://scripts/NetworkManager.gd").new()
	add_child(nm)
	nm.get_users(func(users):
		user_option.clear()
		user_option.add_item("Select User...", 0)
		user_option.set_item_disabled(0, true)
		
		for u in users:
			user_option.add_item(u)
			
		user_option.add_separator()
		user_option.add_item("Create New User...", 999)
		
		# Load preferences to auto-select if possible
		load_preferences(users)
		nm.queue_free()
	)

func _on_user_selected(index):
	var id = user_option.get_item_id(index)
	var text = user_option.get_item_text(index)
	
	if id == 999: # Create New
		if username_input:
			username_input.visible = true
			username_input.text = ""
			username_input.grab_focus()
	else:
		if username_input:
			username_input.visible = false
			username_input.text = text
		# Ideally trigger preference load here too

func load_preferences(user_list = []):
	var config = ConfigFile.new()
	var err = config.load("user://settings.cfg")
	if err == OK:
		var saved_name = config.get_value("user", "username", "")
		var saved_grade = config.get_value("user", "grade", 10)
		var saved_loc = config.get_value("user", "location", "New Hampshire")
		var saved_style = config.get_value("user", "style", "Visual")
		var saved_manual = config.get_value("user", "manual_mode", true) 
		
		print("Loaded Prefs - Name: ", saved_name)
		
		# Try to select in dropdown
		if saved_name in user_list:
			for i in range(user_option.item_count):
				if user_option.get_item_text(i) == saved_name:
					user_option.selected = i
					if username_input:
						username_input.text = saved_name
					break
		
		# Select Grade
		if grade_option:
			for i in range(grade_option.item_count):
				var id = grade_option.get_item_id(i)
				if int(id) == int(saved_grade):
					grade_option.selected = i
					break
		
		# Select Location
		if location_option:
			for i in range(location_option.item_count):
				if location_option.get_item_text(i) == saved_loc:
					location_option.selected = i
					break
					
		# Select Style
		if style_option:
			for i in range(style_option.item_count):
				if style_option.get_item_text(i) == saved_style:
					style_option.selected = i
					break
		
		# Manual Check
		var check = $VBoxContainer.get_node_or_null("ManualSelectCheck")
		if check:
			check.button_pressed = saved_manual

func _on_start_pressed():
	var user_val = ""
	if username_input:
		user_val = username_input.text.strip_edges()
		
	if user_val == "":
		status_label.text = "Please enter or select a username!"
		return
		
	var grade_val = grade_option.get_selected_id()
	
	save_preferences(user_val, grade_val)
	
	status_label.text = "Initializing Session..."
	start_button.disabled = true
	
	var nm = preload("res://scripts/NetworkManager.gd").new()
	add_child(nm)
	nm.session_ready.connect(_on_session_ready)
	
	# Get Checkbox states
	var manual_check = $VBoxContainer.get_node_or_null("ManualSelectCheck")
	var is_manual = manual_check.button_pressed if manual_check else false
	
	var save_check = $VBoxContainer.get_node_or_null("SaveProfileCheck")
	var do_save = save_check.button_pressed if save_check else false
	
	# Set global manual mode
	var gm = get_node("/root/GameManager")
	if gm:
		gm.manual_selection_mode = is_manual
		gm.player_grade = grade_val
	
	var data = {
		"username": user_val,
		"grade_level": grade_val,
		"location": location_option.get_item_text(location_option.selected),
		"learning_style": style_option.get_item_text(style_option.selected),
		"save_profile": do_save
	}
	
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

func save_preferences(name, grade):
	var config = ConfigFile.new()
	config.set_value("user", "username", name)
	config.set_value("user", "grade", grade)
	config.set_value("user", "location", location_option.get_item_text(location_option.selected))
	config.set_value("user", "style", style_option.get_item_text(style_option.selected))
	
	var check = $VBoxContainer.get_node_or_null("ManualSelectCheck")
	if check:
		config.set_value("user", "manual_mode", check.button_pressed)
		
	config.save("user://settings.cfg")

func _on_session_ready(data):
	pass
