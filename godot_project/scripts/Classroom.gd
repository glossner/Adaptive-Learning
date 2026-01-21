extends Node3D

var network_manager
var current_topic = ""
var chat_log: RichTextLabel
var input_field: LineEdit
var completion_gauge: TextureProgressBar
var mastery_label: Label

func _ready():
	network_manager = preload("res://scripts/NetworkManager.gd").new()
	add_child(network_manager)
	network_manager.chat_response_received.connect(_on_agent_response)
	network_manager.session_ready.connect(_on_session_ready)
	network_manager.progress_updated.connect(_on_progress_updated)
	
	# Camera Setup (Since we removed player)
	var cam = Camera3D.new()
	add_child(cam)
	cam.position = Vector3(0, 2, 4)
	cam.look_at(Vector3(0, 1, 0))
	
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
	
	# Directional Light
	var light = DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-60, 30, 0)
	light.shadow_enabled = true
	add_child(light)

	# FILL Light (Omni) for character visibility
	var omni = OmniLight3D.new()
	omni.omni_range = 10.0
	omni.position = Vector3(0, 3, 2)
	add_child(omni)

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
	
	# Main Container (Split View)
	var main_hbox = HBoxContainer.new()
	main_hbox.anchor_right = 1.0
	main_hbox.anchor_bottom = 1.0
	main_hbox.offset_left = 20
	main_hbox.offset_top = 20
	main_hbox.offset_right = -20
	main_hbox.offset_bottom = -20
	main_hbox.add_theme_constant_override("separation", 20)
	canvas.add_child(main_hbox)
	
	# [LEFT] Sidebar (20%)
	var sidebar = VBoxContainer.new()
	sidebar.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	sidebar.size_flags_stretch_ratio = 0.25 # Ratio 1:4 (20%:80%)
	main_hbox.add_child(sidebar)
	
	var back_btn = Button.new()
	back_btn.text = "< Back to Library"
	back_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/Library.tscn"))
	sidebar.add_child(back_btn)
	
	# Spacer
	var spacer = Control.new()
	spacer.custom_minimum_size = Vector2(0, 20)
	sidebar.add_child(spacer)
	
	# Action Buttons
	var actions = ["Teach Me", "Quiz Me", "Explain", "Examples"]
	for a in actions:
		var btn = Button.new()
		btn.text = a
		btn.custom_minimum_size = Vector2(0, 40)
		btn.pressed.connect(func(): _on_submit(a))
		sidebar.add_child(btn)
		
	# Spacer
	var spacer2 = Control.new()
	spacer2.custom_minimum_size = Vector2(0, 30)
	sidebar.add_child(spacer2)
	
	# Completion Gauge
	var gauge_label = Label.new()
	gauge_label.text = "Topic Mastery"
	sidebar.add_child(gauge_label)
	
	completion_gauge = TextureProgressBar.new()
	completion_gauge.min_value = 0
	completion_gauge.max_value = 100
	completion_gauge.value = 0
	# Create simple textures programmatically
	var bg_img = Image.create(200, 30, false, Image.FORMAT_RGBA8)
	bg_img.fill(Color(0.2, 0.2, 0.2))
	var fill_img = Image.create(200, 30, false, Image.FORMAT_RGBA8)
	fill_img.fill(Color(0, 0.8, 0.2))
	
	completion_gauge.texture_under = ImageTexture.create_from_image(bg_img)
	completion_gauge.texture_progress = ImageTexture.create_from_image(fill_img)
	sidebar.add_child(completion_gauge)
	
	mastery_label = Label.new()
	mastery_label.text = "0%"
	sidebar.add_child(mastery_label)
		
	# [RIGHT] Chat Interface (80%)
	var chat_panel = Panel.new()
	chat_panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	chat_panel.size_flags_stretch_ratio = 1.0
	chat_panel.modulate = Color(1, 1, 1, 0.9)
	main_hbox.add_child(chat_panel)
	
	var chat_vbox = VBoxContainer.new()
	chat_vbox.set_anchors_preset(Control.PRESET_FULL_RECT)
	chat_vbox.offset_left = 10
	chat_vbox.offset_top = 10
	chat_vbox.offset_right = -10
	chat_vbox.offset_bottom = -10
	chat_panel.add_child(chat_vbox)
	
	chat_log = RichTextLabel.new()
	chat_log.size_flags_vertical = Control.SIZE_EXPAND_FILL
	chat_log.scroll_following = true
	chat_log.selection_enabled = true
	chat_vbox.add_child(chat_log)
	
	input_field = LineEdit.new()
	input_field.placeholder_text = "Type your question here or use the menu..."
	input_field.text_submitted.connect(_on_submit)
	# input_field.focus_entered.connect(_on_focus) # No longer needed without captured mouse
	# input_field.focus_exited.connect(_on_unfocus)
	chat_vbox.add_child(input_field)
	
	# Ensure mouse is visible since we removed the FPS player
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE

func setup_simplified_ui(parent):
	var grid = HBoxContainer.new()
	grid.size_flags_vertical = Control.SIZE_SHRINK_END
	grid.custom_minimum_size = Vector2(0, 100)
	parent.add_child(grid)
	
	var actions = ["Yes", "No", "Explain", "Quiz Me"]
	for a in actions:
		var btn = Button.new()
		btn.text = a
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.pressed.connect(func(): _on_submit(a))
		grid.add_child(btn)

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
	
	# Initial mastery
	update_gauge(data.get("mastery", 0))
	
	append_chat("System", "Session loaded. Mastery: " + str(data.get("mastery", 0)) + "%. " + summary)
	
	# Proactive Trigger if mastery is 0 (New Topic)
	if data.get("mastery", 0) == 0:
		network_manager.send_message("Please start the lesson.")

func _on_progress_updated(xp, level, mastery):
	update_gauge(mastery)

func update_gauge(val):
	if completion_gauge:
		# Tween the value for smooth effect
		var tween = create_tween()
		tween.tween_property(completion_gauge, "value", val, 0.5)
	if mastery_label:
		mastery_label.text = str(val) + "%"

	

	


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
