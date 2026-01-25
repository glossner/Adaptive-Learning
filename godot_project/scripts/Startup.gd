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
@onready var role_option = $AdvancedPopup/VBox/RoleOption # [NEW] Assumed node exists or will be added dynamically?
# CAUTION: The user did NOT edit the .tscn file to add the node.
# I should probably spawn it dynamically in code if I can't edit .tscn directly easily via tools.
# BUT Registration.gd had it. Startup.gd UI is simpler.
# Let's assume I need to Create it in code if it doesn't exist?
# Or I can just blindly reference it and ask user to add it? No, I must fix it.
# I will create it in _ready if null?
# Let's add variable and initialization.
@onready var location_option = $AdvancedPopup/VBox/LocationOption
@onready var style_option = $AdvancedPopup/VBox/StyleOption
@onready var save_check = $AdvancedPopup/VBox/SaveProfileCheck
@onready var close_advanced_btn = $AdvancedPopup/VBox/CloseAdvanced
var forgot_pcode_popup: Window = null # Dynamic window for reset

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

	# Role Setup (Dynamic or referencing existing if added to scene)
	# Since I cannot edit .tscn binary/text easily without breaking, I will create it dynamically
	if not has_node("AdvancedPopup/VBox/RoleOption"):
		role_option = OptionButton.new()
		role_option.name = "RoleOption"
		$AdvancedPopup/VBox.add_child(role_option)
		# Move it up?
		$AdvancedPopup/VBox.move_child(role_option, 1) # After Grade?
		
	role_option.clear()
	role_option.add_item("Student", 0)
	role_option.add_item("Teacher", 1)
	role_option.selected = 0
	role_option.selected = 0
	
	# Dynamic Password Input for Login
	if not has_node("Panel/MainContainer/PasswordInput"):
		var pwd = LineEdit.new()
		pwd.name = "PasswordInput"
		pwd.placeholder_text = "Password"
		pwd.secret = true
		$Panel/MainContainer.add_child(pwd)
		# Build UI order: UserOption -> Password -> ManualCheck -> etc.
		# UserOption is at ? ManualCheck is at ?
		# Let's try to place it before StartButton
		$Panel/MainContainer.move_child(pwd, $Panel/MainContainer/StartButton.get_index())
	
	# Forgot Password Link
	if not has_node("Panel/MainContainer/ForgotLink"):
		var link = LinkButton.new()
		link.name = "ForgotLink"
		link.text = "Forgot Password?"
		link.underline = LinkButton.UNDERLINE_MODE_ALWAYS
		link.modulate = Color(0.5, 0.5, 1.0)
		link.pressed.connect(_on_forgot_password_pressed)
		$Panel/MainContainer.add_child(link)
		$Panel/MainContainer.move_child(link, $Panel/MainContainer/StartButton.get_index() + 1) # Below Start
	
	create_user_btn.pressed.connect(_on_create_user_pressed)
	advanced_btn.pressed.connect(_on_advanced_pressed)
	close_advanced_btn.pressed.connect(_on_close_advanced_pressed)
	start_button.pressed.connect(_on_start_pressed)
	user_option.item_selected.connect(_on_user_selected)
	
	# Load Users
	# Check if we are in Editor or Debug build (Local)
	if OS.has_feature("editor") or OS.has_feature("debug"):
		print("Startup: Local environment detected. Bypassing Access Control.")
		fetch_users()
	else:
		# Production / Release build
		_setup_access_control()

func _setup_access_control():
	# Create Blocking Overlay
	var overlay = ColorRect.new()
	overlay.name = "AccessOverlay"
	overlay.set_anchors_preset(Control.PRESET_FULL_RECT)
	overlay.color = Color(0.1, 0.1, 0.1, 1.0) # Solid dark background
	add_child(overlay)
	
	var vbox = VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_CENTER)
	overlay.add_child(vbox)
	
	var label = Label.new()
	label.text = "Enter Access Code (Beta)"
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vbox.add_child(label)
	
	var input = LineEdit.new()
	input.placeholder_text = "Access Code"
	input.secret = true
	input.custom_minimum_size = Vector2(200, 30)
	vbox.add_child(input)
	
	var btn = Button.new()
	btn.text = "Verify"
	btn.custom_minimum_size = Vector2(100, 30)
	vbox.add_child(btn)
	
	var error_lbl = Label.new()
	error_lbl.name = "ErrorLabel"
	error_lbl.modulate = Color(1, 0.5, 0.5)
	vbox.add_child(error_lbl)
	
	btn.pressed.connect(func(): _verify_access_code(input.text, overlay, error_lbl))

func _verify_access_code(code: String, overlay: Control, err_label: Label):
	# Get code from Environment ONLY
	var valid_code = OS.get_environment("GAME_ACCESS_CODE")
	
	if valid_code == "":
		err_label.text = "Server Error: Access Code not configured."
		return

	if code == valid_code:
		overlay.queue_free()
		fetch_users() # PROCEED
	else:
		err_label.text = "Invalid Access Code"

func fetch_users():
	var nm = preload("res://scripts/NetworkManager.gd").new()
	add_child(nm)
	nm.get_users(func(users):
		# Handle Connection Error / Fallback
		if users == null:
			if nm.base_url == nm.local_url:
				print("Startup: Local backend unreachable. Falling back to PROD...")
				status_label.text = "Local offline. Switching to Render..."
				
				# SWITCH TO PROD
				nm.base_url = nm.prod_url
				# Update Global Access logic if needed? 
				# The singleton NetworkManager also needs update?
				# Actually 'nm' here is a local instance. 
				# We should update GLOBAL NM too for future calls?
				# The Autoload 'NetworkManager' is separate from this 'nm' instance.
				NetworkManager.base_url = NetworkManager.prod_url
				
				# RETRY once
				nm.get_users(func(retry_users):
					if retry_users == null:
						status_label.text = "Connection Failed (Local & Prod)."
						user_option.clear()
						user_option.add_item("Offline", 0)
						user_option.set_item_disabled(0, true)
					else:
						_populate_users(retry_users)
				)
				return
			else:
				status_label.text = "Connection Failed."
				user_option.clear()
				user_option.add_item("Offline", 0)
				user_option.set_item_disabled(0, true)
				return

		_populate_users(users)
		nm.queue_free()
	)

func _populate_users(users):
	user_option.clear()
	user_option.add_item("Select User...", 0)
	user_option.set_item_disabled(0, true)
	
	for u in users:
		user_option.add_item(u)
		
	# Try to load previous user prefs
	load_preferences(users)

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
	var username = user_option.get_item_text(user_idx)
	if username == "Select User...":
		status_label.text = "Please select a user."
		return
	
	# Verify Password
	var pwd_input = $Panel/MainContainer/PasswordInput
	var password = pwd_input.text.strip_edges()
	
	if password == "":
		status_label.text = "Password required."
		return
		
	status_label.text = "Logging in..."
	start_button.disabled = true
	
	# Login Call
	var nm_script = load("res://scripts/NetworkManager.gd").new()
	var url = nm_script.base_url + "/login"
	nm_script.queue_free()
	
	var http = HTTPRequest.new()
	add_child(http)
	http.request_completed.connect(func(result, code, headers, body):
		start_button.disabled = false
		
		# Handle Login Response
		if code == 200:
			var resp = JSON.parse_string(body.get_string_from_utf8())
			status_label.text = "Success!"
			
			# Proceed to select book/init session
			# GameManager.player_username = username # This line is commented out in the original snippet, but should be GameManager.player_username = username
			var gm = get_node("/root/GameManager")
			if gm:
				gm.player_username = username
			
			# We can now go to Library
			# Proceed to Initialize Session (Advanced options, etc.)
			_initialize_session(username)
		else:
			status_label.text = "Login Failed."
			if code == 400:
				var err = JSON.parse_string(body.get_string_from_utf8())
				if err and err.has("detail"):
					status_label.text = str(err["detail"])
	)
	
	var data = {
		"username": username,
		"password": password
	}
	var headers = ["Content-Type: application/json"]
	http.request(url, headers, HTTPClient.METHOD_POST, JSON.stringify(data))
	
	# Gather settings from Advanced (even if hidden, they hold values)
	
func _on_forgot_password_pressed():
	# Create Popup if missing
	if forgot_pcode_popup == null:
		forgot_pcode_popup = Window.new()
		forgot_pcode_popup.title = "Reset Password"
		forgot_pcode_popup.close_requested.connect(func(): forgot_pcode_popup.hide())
		forgot_pcode_popup.size = Vector2(300, 150)
		forgot_pcode_popup.position = Vector2(100, 100) # Simplify
		add_child(forgot_pcode_popup)
		
		var vbox = VBoxContainer.new()
		vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
		vbox.offset_left = 10; vbox.offset_top = 10; vbox.offset_right = -10; vbox.offset_bottom = -10
		forgot_pcode_popup.add_child(vbox)
		
		var lbl = Label.new()
		lbl.text = "Enter Username:"
		vbox.add_child(lbl)
		
		var txt = LineEdit.new()
		txt.placeholder_text = "Username"
		txt.name = "ResetInput"
		vbox.add_child(txt)
		
		var btn = Button.new()
		btn.text = "Send Reset Link"
		btn.pressed.connect(func(): _send_reset_request(txt.text))
		vbox.add_child(btn)
		
		var STATUS = Label.new()
		STATUS.name = "Status"
		STATUS.modulate = Color(1, 1, 0)
		vbox.add_child(STATUS)
		
	forgot_pcode_popup.popup_centered()

func _send_reset_request(username):
	var status = forgot_pcode_popup.get_node("VBoxContainer/Status") if forgot_pcode_popup.has_node("VBoxContainer/Status") else forgot_pcode_popup.get_child(0).get_node("Status") 
	# Actually node path is simpler
	
	if username == "": return
	status.text = "Sending..."
	
	var nm_script = load("res://scripts/NetworkManager.gd").new()
	var url = nm_script.base_url + "/request-password-reset"
	nm_script.queue_free()
	
	var http = HTTPRequest.new()
	forgot_pcode_popup.add_child(http)
	http.request_completed.connect(func(res, code, headers, body):
		http.queue_free()
		# Always success message for security/simplicity
		status.text = "If user exists, email sent!"
	)
	
	var data = {"username": username}
	var headers = ["Content-Type: application/json"]
	http.request(url, headers, HTTPClient.METHOD_POST, JSON.stringify(data))

func _initialize_session(username):
	var grade_val = grade_option.get_selected_id()
	var loc_val = location_option.get_item_text(location_option.selected)
	var style_val = style_option.get_item_text(style_option.selected)

	var role_val = "Student"
	if role_option and role_option.selected == 1:
		role_val = "Teacher"
		
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
	
	var init_data = {
		"username": username,
		"grade_level": grade_val,
		"location": loc_val,
		"learning_style": style_val,

		"role": role_val,
		"save_profile": do_save
	}
	
	var init_http = HTTPRequest.new()
	add_child(init_http)
	init_http.request_completed.connect(func(result, code, headers, body):
		if code == 200:
			var json = JSON.parse_string(body.get_string_from_utf8())
			get_tree().change_scene_to_file("res://scenes/Library.tscn")
		else:
			status_label.text = "Error: " + str(code)
			start_button.disabled = false
	)
	
	var body_json = JSON.stringify(init_data)
	var headers = ["Content-Type: application/json"]
	init_http.request(NetworkManager.base_url + "/init_session", headers, HTTPClient.METHOD_POST, body_json)

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
