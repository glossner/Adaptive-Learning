extends Node3D

var network_manager
var player

# UI Elements
var chat_ui: Control
var chat_log: RichTextLabel
var input_field: LineEdit
var toc_ui: Control
var toc_label: Label
var hud_xp: Label

# State
var current_topic = ""

func _ready():
	setup_full_library()
	setup_ui()
	
	network_manager = preload("res://scripts/NetworkManager.gd").new()
	add_child(network_manager)
	network_manager.chat_response_received.connect(_on_agent_response)
	network_manager.session_ready.connect(_on_session_ready)
	network_manager.error_occurred.connect(_on_error)
	
	# Spawn Player
	var player_scn = load("res://scenes/Player.tscn")
	player = player_scn.instantiate()
	player.position = Vector3(0, 0.5, 0)
	add_child(player)

func setup_full_library():
	# Floor
	var floor_mesh = MeshInstance3D.new()
	floor_mesh.mesh = BoxMesh.new()
	floor_mesh.mesh.size = Vector3(40, 0.5, 40)
	floor_mesh.position.y = -0.25
	floor_mesh.create_trimesh_collision()
	add_child(floor_mesh)
	
	# Light
	var light = DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-60, -30, 0)
	light.shadow_enabled = true
	add_child(light)
	
	# Shelves Generation
	var categories = ["Mathematics", "History", "Science", "Literature"]
	var colors = [Color.RED, Color.BLUE, Color.GREEN, Color.PURPLE]
	
	for i in range(len(categories)):
		var z_offset = -10 + (i * 6)
		create_shelf_row(Vector3(-5, 0, z_offset), categories[i], colors[i])
		create_shelf_row(Vector3(5, 0, z_offset), categories[i], colors[i])

func create_shelf_row(pos: Vector3, category: String, color: Color):
	# Shelf Frame
	var shelf = MeshInstance3D.new()
	shelf.mesh = BoxMesh.new()
	shelf.mesh.size = Vector3(8, 3, 1)
	shelf.position = pos + Vector3(0, 1.5, 0)
	shelf.create_trimesh_collision()
	add_child(shelf)
	
	# Books
	for b in range(10):
		var book = Area3D.new()
		var mesh = MeshInstance3D.new()
		mesh.mesh = BoxMesh.new()
		mesh.mesh.size = Vector3(0.2, 0.4, 0.8) # Thick book sticking out
		mesh.position = Vector3((b * 0.7) - 3.5, 0, 0.6) # On shelf
		
		var mat = StandardMaterial3D.new()
		mat.albedo_color = color.lightened(randf() * 0.5)
		mesh.material_override = mat
		
		# Collision
		var col = CollisionShape3D.new()
		var shape = BoxShape3D.new()
		shape.size = mesh.mesh.size
		col.shape = shape
		col.position = mesh.position
		
		book.add_child(mesh)
		book.add_child(col)
		# Store metadata
		book.set_meta("topic", category + " - Vol " + str(b+1))
		book.input_event.connect(_on_book_input.bind(book))
		
		shelf.add_child(book)
		
		# Label (Text3D is new in Godot 3/4, Label3D in 4)
		var label = Label3D.new()
		label.text = category
		label.font_size = 32
		label.position = mesh.position + Vector3(0, 0.3, 0.45)
		label.scale = Vector3(0.1, 0.1, 0.1)
		book.add_child(label)

func _on_book_input(camera, event, pos, normal, shape_idx, book):
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		var topic = book.get_meta("topic")
		print("Selected: " + topic)
		show_toc(topic)

func setup_ui():
	var canvas = CanvasLayer.new()
	add_child(canvas)
	
	# HUD
	hud_xp = Label.new()
	hud_xp.text = "XP: 0 | Lvl: 1"
	hud_xp.position = Vector2(20, 20)
	canvas.add_child(hud_xp)
	
	# TOC Popup
	toc_ui = Panel.new()
	toc_ui.anchor_left = 0.3
	toc_ui.anchor_right = 0.7
	toc_ui.anchor_top = 0.2
	toc_ui.anchor_bottom = 0.8
	toc_ui.visible = false
	canvas.add_child(toc_ui)
	
	var vbox = VBoxContainer.new()
	vbox.anchor_right = 1.0
	vbox.anchor_bottom = 1.0
	vbox.offset_left = 20
	vbox.offset_top = 20
	vbox.offset_right = -20
	vbox.offset_bottom = -20
	toc_ui.add_child(vbox)
	
	toc_label = Label.new()
	toc_label.text = "Table of Contents"
	vbox.add_child(toc_label)
	
	var start_btn = Button.new()
	start_btn.text = "Start / Resume"
	start_btn.pressed.connect(_on_toc_start_pressed)
	vbox.add_child(start_btn)
	
	var close_btn = Button.new()
	close_btn.text = "Close"
	close_btn.pressed.connect(func(): 
		toc_ui.visible = false
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	)
	vbox.add_child(close_btn)
	
	# Chat UI (Hidden until started)
	chat_ui = Panel.new()
	chat_ui.anchor_top = 0.6
	chat_ui.anchor_bottom = 1.0
	chat_ui.anchor_right = 0.4
	chat_ui.visible = false
	canvas.add_child(chat_ui)
	
	var cvbox = VBoxContainer.new()
	cvbox.anchor_right = 1.0
	cvbox.anchor_bottom = 1.0
	chat_ui.add_child(cvbox)
	
	chat_log = RichTextLabel.new()
	chat_log.size_flags_vertical = Control.SIZE_EXPAND_FILL
	chat_log.scroll_following = true
	cvbox.add_child(chat_log)
	
	input_field = LineEdit.new()
	input_field.text_submitted.connect(_on_chat_submit)
	cvbox.add_child(input_field)

func show_toc(topic):
	current_topic = topic
	toc_label.text = "Book: " + topic + "\nLoading progress..."
	toc_ui.visible = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	
	network_manager.select_book(topic)

func _on_toc_start_pressed():
	toc_ui.visible = false
	chat_ui.visible = true
	# Keep mouse visible for chat
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE 
	append_chat("System", "Opening " + current_topic + "...")

func _on_session_ready(data):
	toc_label.text = "Book: " + current_topic + "\nMastery: " + str(data["mastery"]) + "%\n" + str(data.get("history_summary", ""))
	hud_xp.text = "XP: " + str(data["xp"]) + " | Lvl: " + str(data["level"])

func _on_chat_submit(text):
	if text == "": return
	input_field.text = ""
	append_chat("You", text)
	network_manager.send_message(text)

func _on_agent_response(response, action):
	append_chat("Agent", response)

func append_chat(sender, msg):
	chat_log.append_text("[b]" + sender + ":[/b] " + msg + "\n")

func _on_error(msg):
	print("Error: " + msg)
	append_chat("Error", msg)
