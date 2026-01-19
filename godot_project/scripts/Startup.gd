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
		
	start_button.pressed.connect(_on_start_pressed)

func _on_start_pressed():
	var username = username_input.text
	if username == "":
		status_label.text = "Please enter a username."
		return
		
	var grade_idx = grade_option.get_selected_id()
	var location = location_option.get_item_text(location_option.selected)
	var style = style_option.get_item_text(style_option.selected)
	
	status_label.text = "Connecting..."
	start_button.disabled = true
	
	var data = {
		"username": username,
		"grade_level": grade_idx,
		"location": location,
		"learning_style": style
	}
	
	NetworkManager.post_request("/init_session", data, _on_init_success, _on_init_fail)

func _on_init_success(_response_code, data):
	status_label.text = "Welcome, " + data["username"] + "!"
	# Save global user info if needed in GameManager
	GameManager.player_username = data["username"]
	GameManager.player_grade = data["grade_level"]
	
	# Transition to Library
	get_tree().change_scene_to_file("res://scenes/Library.tscn")

func _on_init_fail(_response_code, error_msg):
	status_label.text = "Error: " + error_msg
	start_button.disabled = false
