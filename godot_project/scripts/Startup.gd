extends Control

@onready var username_input = $VBoxContainer/UsernameInput
@onready var grade_option = $VBoxContainer/GradeOption
@onready var location_option = $VBoxContainer/LocationOption
@onready var style_option = $VBoxContainer/StyleOption
@onready var start_button = $VBoxContainer/StartButton
@onready var status_label = $VBoxContainer/StatusLabel

func _ready():
	# Populate Grade Options
	grade_option.add_item("Kindergarten", 0)
	for i in range(1, 13):
		grade_option.add_item("Grade " + str(i), i)
	grade_option.add_item("Undergraduate", 13)
	grade_option.add_item("Masters", 15)
	grade_option.select(10) # Default to Grade 10
	
	# Populate Location (Sample)
	var locs = ["New Hampshire", "California", "Texas", "New York", "International"]
	for l in locs:
		location_option.add_item(l)
	
	# Populate Styles
	var styles = ["Visual", "Text-Based", "Auditory", "Kinesthetic"]
	for s in styles:
		style_option.add_item(s)
		
	# Load saved data
	load_preferences()
	
	# Connect buttons
	if start_button:
		start_button.pressed.connect(_on_start_pressed)

func load_preferences():
	var config = ConfigFile.new()
	var err = config.load("user://settings.cfg")
	if err == OK:
		var saved_name = config.get_value("user", "username", "")
		var saved_grade = config.get_value("user", "grade", 10)
		print("Loaded Prefs - Name: ", saved_name, " Grade: ", saved_grade)
		
		if username_input:
			username_input.text = saved_name
		
		# Find and select the grade in dropdown by ID
		if grade_option:
			for i in range(grade_option.item_count):
				var id = grade_option.get_item_id(i)
				if int(id) == int(saved_grade):
					grade_option.selected = i
					break

func save_preferences(username, grade):
	print("Saving Prefs - Name: ", username, " Grade: ", grade)
	var config = ConfigFile.new()
	config.set_value("user", "username", username)
	config.set_value("user", "grade", grade)
	config.save("user://settings.cfg")

func _on_start_pressed():
	var username = username_input.text.strip_edges()
	if username == "":
		status_label.text = "Please enter a username."
		return
		
	# Get Grade ID (which matches the grade level number we set)
	var grade_val = grade_option.get_selected_id()
	if grade_val == -1: grade_val = 10 # Fallback

	
	# Save for next time
	save_preferences(username, grade_val)
	
	# Show loading...
	if start_button:
		start_button.disabled = true
		status_label.text = "Initializing..."
	
	# Call Backend to Init Session
	var data = {
		"username": username, # Fixed: was user_id
		"grade_level": grade_val,
		"location": location_option.get_item_text(location_option.selected),
		"learning_style": style_option.get_item_text(style_option.selected)
	}
	
	print("Sending Init Request: ", data)
	NetworkManager.post_request("/init_session", data, _on_init_success, _on_init_fail)

func _on_init_success(_response_code, response):
	print("Session Initialized: ", response)
	# Store global state
	GameManager.player_username = response["username"] # Fixed: was user_id
	GameManager.player_grade = response["grade_level"]
	GameManager.player_location = location_option.get_item_text(location_option.selected) # Backend doesn't return loc yet
	
	# Switch to Library
	get_tree().change_scene_to_file("res://scenes/Library.tscn")

func _on_init_fail(_code, err):
	status_label.text = "Error: " + str(err)
	if start_button:
		start_button.disabled = false
		# start_button.text = "Start Learning" # Button text wasn't changed, so no need to reset
