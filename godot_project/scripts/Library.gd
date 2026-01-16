extends Node3D

var network_manager
var chat_log: RichTextLabel
var input_field: LineEdit
var topic_input: LineEdit
var start_button: Button

func _ready():
	setup_environment()
	setup_ui()
	
	network_manager = preload("res://scripts/NetworkManager.gd").new()
	add_child(network_manager)
	network_manager.chat_response_received.connect(_on_agent_response)
	network_manager.init_success.connect(_on_session_started)
	network_manager.error_occurred.connect(_on_error)

func setup_environment():
	var floor_mesh = MeshInstance3D.new()
	floor_mesh.mesh = BoxMesh.new()
	floor_mesh.mesh.size = Vector3(20, 0.5, 20)
	floor_mesh.position.y = -0.25
	add_child(floor_mesh)
	
	var cam = Camera3D.new()
	cam.position = Vector3(0, 2, 5)
	add_child(cam)
	
	var light = DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-60, -30, 0)
	light.shadow_enabled = true
	add_child(light)
	
	# Create some "Books" (boxes)
	for i in range(5):
		var book = MeshInstance3D.new()
		book.mesh = BoxMesh.new()
		book.mesh.size = Vector3(0.5, 0.8, 0.2)
		book.position = Vector3(i - 2, 1, -2)
		var mat = StandardMaterial3D.new()
		mat.albedo_color = Color(randf(), randf(), randf())
		book.material_override = mat
		add_child(book)

func setup_ui():
	var canvas = CanvasLayer.new()
	add_child(canvas)
	
	var panel = Panel.new()
	panel.anchor_right = 1.0
	panel.anchor_bottom = 1.0
	# Make it transparent or partial?
	panel.modulate.a = 0.0 # Invisible background for full screen
	canvas.add_child(panel)
	
	# Chat Area (Bottom Left)
	var chat_container = VBoxContainer.new()
	chat_container.anchor_top = 0.6
	chat_container.anchor_bottom = 1.0
	chat_container.anchor_right = 0.4
	chat_container.offset_left = 20
	chat_container.offset_bottom = -20
	panel.add_child(chat_container)
	
	chat_log = RichTextLabel.new()
	chat_log.size_flags_vertical = Control.SIZE_EXPAND_FILL
	chat_log.scroll_following = true
	chat_container.add_child(chat_log)
	
	input_field = LineEdit.new()
	input_field.placeholder_text = "Type your answer or question..."
	input_field.text_submitted.connect(_on_input_submitted)
	chat_container.add_child(input_field)
	
	# Start Session UI (Top Center)
	var start_box = VBoxContainer.new()
	start_box.anchor_left = 0.4
	start_box.anchor_right = 0.6
	start_box.anchor_bottom = 0.2
	panel.add_child(start_box)
	
	topic_input = LineEdit.new()
	topic_input.placeholder_text = "Enter Topic (e.g. Calculus)"
	start_box.add_child(topic_input)
	
	start_button = Button.new()
	start_button.text = "Start Learning"
	start_button.pressed.connect(_on_start_pressed)
	start_box.add_child(start_button)
	
	append_chat("System", "Welcome to the Adaptive Library. Enter a topic to begin.")

func append_chat(sender: String, msg: String):
	chat_log.append_text("[b]" + sender + ":[/b] " + msg + "\n")

func _on_start_pressed():
	var topic = topic_input.text
	if topic == "":
		return
	start_button.disabled = true
	append_chat("System", "Initializing session for " + topic + "...")
	network_manager.init_session(topic, "Grade 10") # Default grade for now

func _on_session_started(session_id):
	append_chat("System", "Session Started! Agents are ready.")
	# Hide start UI?
	start_button.visible = false
	topic_input.visible = false
	# Trigger first message? Agent usually waits for user or we can trigger hello.
	network_manager.send_message("Hello, I am ready to learn.")

func _on_input_submitted(text):
	if text == "":
		return
	input_field.text = ""
	append_chat("You", text)
	network_manager.send_message(text)

func _on_agent_response(response, action):
	append_chat("Agent", response)
	if action == "PROBLEM_GIVEN":
		append_chat("System", "A problem has been assigned. Please solve it.")

func _on_error(msg):
	append_chat("Error", msg)
	start_button.disabled = false
