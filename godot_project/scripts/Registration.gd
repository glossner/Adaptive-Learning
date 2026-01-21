extends Control

@onready var username_input = $Panel/ScrollContainer/VBoxContainer/UsernameInput
@onready var sex_option = $Panel/ScrollContainer/VBoxContainer/SexOption
@onready var birthday_picker = $Panel/ScrollContainer/VBoxContainer/Birthday/HBoxContainer
@onready var interests_input = $Panel/ScrollContainer/VBoxContainer/InterestsInput
@onready var grade_option = $Panel/ScrollContainer/VBoxContainer/GradeOption
@onready var location_option = $Panel/ScrollContainer/VBoxContainer/LocationOption
@onready var style_option = $Panel/ScrollContainer/VBoxContainer/StyleOption
@onready var role_option = $Panel/ScrollContainer/VBoxContainer/RoleOption
@onready var status_label = $Panel/ScrollContainer/VBoxContainer/StatusLabel
@onready var create_button = $Panel/ScrollContainer/VBoxContainer/CreateButton
@onready var back_button = $Panel/ScrollContainer/VBoxContainer/BackButton

func _ready():
    # Setup Dropdowns
    sex_option.clear()
    sex_option.add_item("Select Sex...", 0)
    sex_option.set_item_disabled(0, true)
    sex_option.add_item("Male", 1)
    sex_option.add_item("Female", 2)
    sex_option.add_item("Other", 3)
    sex_option.selected = 0
    
    # Role Setup
    if role_option:
        role_option.clear()
        role_option.add_item("Student", 0)
        role_option.add_item("Teacher", 1)
        role_option.selected = 0

    grade_option.clear()
    for i in range(1, 13):
        grade_option.add_item("Grade " + str(i), i)
    grade_option.select(5) # Default Grade 6
    
    location_option.clear()
    var locs = ["New Hampshire", "California", "Texas", "New York", "International"]
    for l in locs:
        location_option.add_item(l)
    
    style_option.clear()
    var styles = ["Visual", "Text-Based", "Auditory", "Kinesthetic"]
    for s in styles:
        style_option.add_item(s)

    create_button.pressed.connect(_on_create_pressed)
    back_button.pressed.connect(_on_back_pressed)

func _on_back_pressed():
    get_tree().change_scene_to_file("res://scenes/Startup.tscn")

func _on_create_pressed():
    var username = username_input.text.strip_edges()
    if username == "":
        status_label.text = "Username required!"
        return
        
    var sex_idx = sex_option.selected
    if sex_idx == 0:
        status_label.text = "Please select sex."
        return
    var sex_val = sex_option.get_item_text(sex_idx)
    
    # Role
    var role_val = "Student"
    if role_option and role_option.selected == 1:
        role_val = "Teacher"

    # Birthday (Simple Text for now or use SpinBoxes if implemented)
    # Assuming we use 3 spinboxes in HBoxContainer: Year, Month, Day
    var year = $Panel/ScrollContainer/VBoxContainer/Birthday/HBoxContainer/Year.value
    var month = $Panel/ScrollContainer/VBoxContainer/Birthday/HBoxContainer/Month.value
    var day = $Panel/ScrollContainer/VBoxContainer/Birthday/HBoxContainer/Day.value
    var birthday_val = "%04d-%02d-%02d" % [year, month, day]
    
    var data = {
        "username": username,
        "grade_level": grade_option.get_selected_id(),
        "location": location_option.get_item_text(location_option.selected),
        "learning_style": style_option.get_item_text(style_option.selected),
        "sex": sex_val,
        "role": role_val,
        "birthday": birthday_val,
        "interests": interests_input.text,
        "save_profile": true
    }
    
    status_label.text = "Creating Profile..."
    create_button.disabled = true
    
    var http = HTTPRequest.new()
    add_child(http)
    http.request_completed.connect(func(result, code, headers, body):
        if code == 200:
            status_label.text = "Profile Created!"
            
            print("[Registration] Success. Updating Global State for user: ", username)
            # Update Global State directly via Autoload
            GameManager.player_username = username
            GameManager.player_grade = grade_option.get_selected_id()
            GameManager.manual_selection_mode = false
            
            # Sync NetworkManager too
            NetworkManager.current_username = username
            
            # Auto-login to Library
            get_tree().change_scene_to_file("res://scenes/Library.tscn")
        else:
            status_label.text = "Error: " + str(code)
            create_button.disabled = false
    )
    
    var body_json = JSON.stringify(data)
    var headers = ["Content-Type: application/json"]
    http.request("http://127.0.0.1:8000/init_session", headers, HTTPClient.METHOD_POST, body_json)
