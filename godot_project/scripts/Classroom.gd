extends Node3D

var network_manager
var current_topic = ""
var chat_log: RichTextLabel
var input_field: LineEdit

func _ready():
	network_manager = preload("res://scripts/NetworkManager.gd").new()
	add_child(network_manager)
	network_manager.chat_response_received.connect(_on_agent_response)
	network_manager.session_ready.connect(_on_session_ready)
	
	# Player instantiation
	var player_scn = load("res://scenes/Player.tscn")
	var player = player_scn.instantiate()
	player.position = Vector3(0, 0.5, 4.0) # Move back to see room
	player.rotation_degrees = Vector3(0, 0, 0) # Face -Z (Agents)
	add_child(player)
	
	setup_ui()
	
	# Check for global topic
	var gm = get_node("/root/GameManager")
	if gm and gm.current_topic != "":
		initialize(gm.current_topic)
	else:
		initialize("Demo Topic") # Fallback

func initialize(topic: String):
	current_topic = topic
	# Delay message slightly to allow UI to build
	await get_tree().create_timer(0.5).timeout
	network_manager.select_book(topic)
	append_chat("System", "Welcome to the " + topic + " class.")

func setup_classroom():
	# Environment
	var env = WorldEnvironment.new()
	var environment = Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.1, 0.1, 0.15) # Dark Blue-Gray
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.5, 0.5, 0.5)
	env.environment = environment
	add_child(env)

	# Floor
	var floor_mesh = MeshInstance3D.new()
	floor_mesh.mesh = BoxMesh.new()
	floor_mesh.mesh.size = Vector3(10, 0.5, 10)
	floor_mesh.position.y = -0.25
	add_child(floor_mesh)
	
	# Light
	var light = DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-60, 30, 0)
	light.shadow_enabled = true
	add_child(light)

	# Teacher (Capsule)
	var teacher = MeshInstance3D.new()
	teacher.mesh = CapsuleMesh.new()
	teacher.position = Vector3(0, 1, -3)
	var t_mat = StandardMaterial3D.new()
	t_mat.albedo_color = Color.ORANGE
	teacher.material_override = t_mat
	add_child(teacher)
	
	var t_label = Label3D.new()
	t_label.text = "Teacher"
	t_label.position = Vector3(0, 2.2, -3)
	t_label.font_size = 64
	t_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	add_child(t_label)
	
	# Tutor (Sphere)
	var tutor = MeshInstance3D.new()
	tutor.mesh = SphereMesh.new()
	tutor.position = Vector3(2, 1, -2)
	var tu_mat = StandardMaterial3D.new()
	tu_mat.albedo_color = Color.CYAN
	tutor.material_override = tu_mat
	add_child(tutor)

	var tu_label = Label3D.new()
	tu_label.text = "Tutor"
	tu_label.position = Vector3(2, 1.8, -2)
	tu_label.font_size = 64
	tu_label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	add_child(tu_label)

func setup_ui():
	var canvas = CanvasLayer.new()
	add_child(canvas)
	
	# Back Button
	var back_btn = Button.new()
	back_btn.text = "< Back to Library"
	back_btn.position = Vector2(20, 20)
	back_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/Library.tscn"))
	canvas.add_child(back_btn)
	
	# Chat Panel (Right Side Sidebar)
	var panel = Panel.new()
	panel.anchor_left = 0.6 # Starts at 60% width
	panel.anchor_top = 0.0 # Top
	panel.anchor_right = 1.0 # Right edge
	panel.anchor_bottom = 1.0 # Bottom edge
	panel.modulate = Color(1, 1, 1, 0.9) 
	canvas.add_child(panel)
	
	var vbox = VBoxContainer.new()
	vbox.anchor_right = 1.0
	vbox.anchor_bottom = 1.0
	vbox.offset_left = 20
	vbox.offset_top = 20
	vbox.offset_right = -20
	vbox.offset_bottom = -20
	panel.add_child(vbox)
	
	chat_log = RichTextLabel.new()
	chat_log.size_flags_vertical = Control.SIZE_EXPAND_FILL
	chat_log.scroll_following = true
	vbox.add_child(chat_log)
	
	input_field = LineEdit.new()
	input_field.placeholder_text = "Press 'Enter' to type..."
	input_field.text_submitted.connect(_on_submit)
	input_field.focus_entered.connect(_on_focus)
	input_field.focus_exited.connect(_on_unfocus)
	vbox.add_child(input_field)

func _input(event):
	# Shortcut to focus chat
	if event.is_action_pressed("ui_accept") and not input_field.has_focus():
		input_field.grab_focus()
		# Player absorbs input unless we release mouse, but focusing line edit usually helps?
		# We need to explicitly tell player (or just set mouse mode)
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func _on_focus():
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func _on_unfocus():
	# Don't immediately capture, let user click?
	# Or capture if they click game world (handled by Player)
	pass

func _on_submit(text):
	if text == "": 
		input_field.release_focus()
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
		return
		
	input_field.text = ""
	append_chat("You", text)
	network_manager.send_message(text)
	
	# Refocus for consistent typing? Or release?
	# Let's keep focus for convo flow, or release to move?
	# Usually keep focus in chat mode. 
	# User can press ESC to leave chat (handled by Player logic? No, Player logic handles ESC->Visible)
	# We need ESC to unfocus lineedit?
	
	# Simple flow: Submit -> Keep typing. ESC -> Move.
	input_field.grab_focus()

func _on_agent_response(response, action):
	append_chat("Agent", response)

func _on_session_ready(data):
	var summary = data.get("history_summary")
	if summary == null:
		summary = ""
	append_chat("System", "Session loaded. Mastery: " + str(data["mastery"]) + "%. " + summary)

func append_chat(sender, msg):
	var bbcode = markdown_to_bbcode(msg)
	chat_log.append_text("[b]" + sender + ":[/b] " + bbcode + "\n")

func markdown_to_bbcode(text: String) -> String:
	# Basic Markdown to BBCode converter
	var res = text
	# Bold **text** -> [b]text[/b]
	# We use regex or simple replacement for now
	# Godot's RegEx support is good.
	
	var regex = RegEx.new()
	
	# Bold **...**
	regex.compile("\\*\\*(.*?)\\*\\*")
	res = regex.sub(res, "[b]$1[/b]", true)
	
	# Italic *...*
	regex.compile("\\*(.*?)\\*")
	res = regex.sub(res, "[i]$1[/i]", true)
	
	# Headers # ... -> [font_size=24]...[/font_size]
	# regex.compile("^# (.*)$") # Multiline flag needed? simpler loop?
	# Simple header replace for now
	if res.begins_with("# "):
		res = "[font_size=24]" + res.substr(2) + "[/font_size]"
	
	return res
