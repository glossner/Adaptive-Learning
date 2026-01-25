extends Node3D

var network_manager
var player

var hud_xp: Label
var hud_level: Label
var hud_grade: Label
var grade_gauge: TextureProgressBar

var grade_percent_label: Label
var sidebar_panel: Panel
var joystick_left: VirtualJoystick
var joystick_right: VirtualJoystick
var hud_role: Label

func _ready():
	randomize()
	# Init Network Manager
	network_manager = preload("res://scripts/NetworkManager.gd").new()
	add_child(network_manager)
	
	# Sync Username
	var gm = get_node("/root/GameManager")
	if gm:
		network_manager.current_username = gm.player_username
		
	setup_full_library()
	setup_ui()
	
	print("[Library] Player Grade: ", GameManager.player_grade)
	print("[Library] Manual Mode: ", GameManager.manual_selection_mode)
	
	# Connect player interaction
	var player_scn = load("res://scenes/Player.tscn")
	player = player_scn.instantiate()
	player.position = Vector3(0, 0.5, 0)
	player.interaction_requested.connect(_on_interaction)
	add_child(player)

func _process(_delta):
	# Feed joystick input to player
	if player and is_instance_valid(player):
		if joystick_left:
			player.external_move_input = joystick_left.get_output()
			# Flip Y for movement? No, usually Up is Negative Y in 2D, but Forward is Negative Z in 3D.
			# Player code: Vector3(input.x, 0, input.y) -> Z is input.y
			# Joystick Up (-1) -> Forward (Neg Z). Matches.
			
		if joystick_right:
			player.external_look_input = joystick_right.get_output()

func setup_ui():
	var canvas = CanvasLayer.new()
	add_child(canvas)
	
	# Sidebar Background
	sidebar_panel = Panel.new()
	sidebar_panel.name = "Panel"
	sidebar_panel.custom_minimum_size = Vector2(240, 0)
# ...
	# Container with Margins
	var margin = MarginContainer.new()
	margin.name = "MarginContainer"
# ...
	var vbox = VBoxContainer.new()
	vbox.name = "VBoxContainer"
	sidebar_panel.set_anchors_preset(Control.PRESET_LEFT_WIDE)
	
	# Mobile Check (Simple heuristic or responsive)
	# For now, default to Hidden on start if screen width is small? 
	# Or just add a toggle button and let user decide.
	
	# Style: Dark semi-transparent
	var style = StyleBoxFlat.new()
	style.bg_color = Color(0.1, 0.1, 0.1, 0.9)
	sidebar_panel.add_theme_stylebox_override("panel", style)
	canvas.add_child(sidebar_panel)
	
	# Menu Toggle Button (Always visible)
	var menu_btn = Button.new()
	menu_btn.text = "MENU"
	menu_btn.position = Vector2(10, 10)
	menu_btn.pressed.connect(_on_toggle_menu)
	canvas.add_child(menu_btn)
	
	# Add Joysticks (Always add if touch capability or override)
	# Check feature "touchscreen"
	if true: # Force enable for testing/tablet support even on hybrid
		var joystick_scn = load("res://scenes/VirtualJoystick.tscn")
		if joystick_scn:
			joystick_left = joystick_scn.instantiate()
			# Anchor Bottom Left
			joystick_left.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
			joystick_left.offset_left = 50
			joystick_left.offset_bottom = -50
			joystick_left.position = Vector2(50, get_viewport().get_visible_rect().size.y - 250) # Fallback pos
			# Make it smaller region? No, it fills anchor unless we resize.
			# Our VJ scene is full screen control?
			# Wait, the VJ scene root is Anchors Preset 15 (Full Rect).
			# We should probably resize it or count on its internal logic.
			# Internal logic checks distance from Base center.
			# Base is center anchored.
			# We need to position the CONTROL node to the corner.
			joystick_left.custom_minimum_size = Vector2(250, 250)
			joystick_left.size = Vector2(250, 250)
			# Reset anchors to be simple
			joystick_left.set_anchors_preset(Control.PRESET_BOTTOM_LEFT)
			joystick_left.position = Vector2(20, get_viewport().get_visible_rect().size.y - 270)
			
			canvas.add_child(joystick_left)
			
			joystick_right = joystick_scn.instantiate()
			# Anchor Bottom Right
			joystick_right.joystick_mode = "Look"
			joystick_right.set_anchors_preset(Control.PRESET_BOTTOM_RIGHT)
			joystick_right.size = Vector2(250, 250)
			joystick_right.position = Vector2(get_viewport().get_visible_rect().size.x - 270, get_viewport().get_visible_rect().size.y - 270)
			
			canvas.add_child(joystick_right)
	
	# Container with Margins
	var margin = MarginContainer.new()
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 20)
	margin.add_theme_constant_override("margin_top", 20)
	margin.add_theme_constant_override("margin_right", 20)
	margin.add_theme_constant_override("margin_bottom", 20)
	sidebar_panel.add_child(margin)


	
	var vbox = VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 15)
	margin.add_child(vbox)
	
	# 1. Player Stats
	hud_xp = Label.new()
	hud_xp.text = "XP: 0"
	vbox.add_child(hud_xp)
	
	hud_level = Label.new()
	hud_level.text = "Lvl: 1"
	vbox.add_child(hud_level)
	
	hud_grade = Label.new()
	hud_grade.text = "Grade: ?"

	vbox.add_child(hud_grade)
	
	# Role Label
	# Role Label
	hud_role = Label.new()
	hud_role.text = "Role: Student"
	hud_role.name = "HudRole"
	vbox.add_child(hud_role)
	
	var grade_label_small = Label.new()
	grade_label_small.text = "Grade Completion:"
	grade_label_small.add_theme_font_size_override("font_size", 12)
	vbox.add_child(grade_label_small)
	
	grade_gauge = TextureProgressBar.new()
	grade_gauge.min_value = 0
	grade_gauge.max_value = 100
	grade_gauge.value = 0
	grade_gauge.custom_minimum_size = Vector2(0, 15)
	grade_gauge.texture_under = _create_img_tex(Color(0.2, 0.2, 0.2), 200, 15)
	grade_gauge.texture_progress = _create_img_tex(Color(0.9, 0.5, 0.2), 200, 15)
	vbox.add_child(grade_gauge)
	
	grade_percent_label = Label.new()
	grade_percent_label.text = "0%"
	grade_percent_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	vbox.add_child(grade_percent_label)
	
	vbox.add_child(HSeparator.new())
	
	# 2. Course Menu
	var title = Label.new()
	title.text = "COURSES"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 20)
	vbox.add_child(title)
	
	var subjects = ["Math", "Science", "History", "English"]
	for sub in subjects:
		var btn = Button.new()
		btn.text = sub
		btn.custom_minimum_size = Vector2(0, 45)
		# Connect with bind to pass argument
		btn.pressed.connect(resume_shelf.bind(sub))
		vbox.add_child(btn)
		
		# Progress Bar (Background)
		var p = TextureProgressBar.new()
		p.name = "Progress_" + sub
		p.texture_under = _create_img_tex(Color(0.2, 0.2, 0.2), 200, 5)
		p.texture_progress = _create_img_tex(Color(0, 0.8, 0.2), 200, 5)
		p.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
		p.custom_minimum_size = Vector2(0, 5)
		p.min_value = 0
		p.max_value = 100
		p.value = 0
		p.mouse_filter = Control.MOUSE_FILTER_IGNORE
		btn.add_child(p)
		
	# Spacer
	var spacer = Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(spacer)
	
	# 3. Controls Help
	var help = Label.new()
	help.text = "CONTROLS\n[WASD] Move\n[Mouse] Look\n[Click] Select\n[ESC] Cursor"
	help.modulate = Color(1, 1, 1, 0.6)
	help.autowrap_mode = TextServer.AUTOWRAP_WORD
	help.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vbox.add_child(help)
	
	vbox.add_child(HSeparator.new())
	
	# 4. Log Out / Edit Profile
	var exit_btn = Button.new()
	exit_btn.text = "Main Menu"
	exit_btn.pressed.connect(func(): get_tree().change_scene_to_file("res://scenes/Startup.tscn"))
	vbox.add_child(exit_btn)
	
	# Fetch Stats
	fetch_stats()
	
	# Start Hidden on Mobile?
	# sidebar_panel.visible = false

func _on_toggle_menu():
	if sidebar_panel:
		sidebar_panel.visible = not sidebar_panel.visible

func _create_img_tex(color, w, h):
	var img = Image.create(w, h, false, Image.FORMAT_RGBA8)
	img.fill(color)
	return ImageTexture.create_from_image(img)

func fetch_stats():
	var gm = get_node("/root/GameManager")
	var data = {"username": gm.player_username}
	# Reuse init_session struct for convenience or make empty request
	# get_player_stats uses init_session struct for username
	NetworkManager.post_request("/get_player_stats", data, _on_stats_received, func(code, err): print("Stats Error: " + err))

func _on_stats_received(code, response):
	if response and response.has("stats"):
		var stats = response["stats"]
		print("Received Stats: ", stats)
		
		# Update Grade UI
		if stats.has("current_grade_level") and hud_grade:

			hud_grade.text = "Grade: " + str(stats["current_grade_level"])
			
		if hud_role and stats.has("role"):
			hud_role.text = "Role: " + str(stats["role"])
			
		if stats.has("grade_completion"):
			var g_val = stats["grade_completion"]
			if grade_gauge: grade_gauge.value = g_val
			if grade_percent_label: grade_percent_label.text = str(g_val) + "%"
		
		var vbox = get_node("CanvasLayer/Panel/MarginContainer/VBoxContainer")
		if vbox:
			for i in range(vbox.get_child_count()):
				var c = vbox.get_child(i)
				if c is Button and c.has_node("Progress_" + c.text):
					var sub = c.text.to_lower()
					var p = c.get_node("Progress_" + c.text)
					if stats.has(sub):
						p.value = stats[sub]

func setup_full_library():
	print("Loading Library Asset from: res://assets/models/Library/library.glb")
	# 1. Environment: Load Library Model
	var lib_model = load("res://assets/models/Library/library.glb").instantiate()
	lib_model.scale = Vector3(1, 1, 1) # Adjust if needed
	add_child(lib_model)
	
	# Safety Floor (Invisible) in case GLB has no collision
	var floor_body = StaticBody3D.new()
	var floor_col = CollisionShape3D.new()
	var floor_shape = BoxShape3D.new()
	floor_shape.size = Vector3(100, 1, 100)
	floor_col.shape = floor_shape
	floor_col.position = Vector3(0, -0.5, 0)
	floor_body.add_child(floor_col)
	add_child(floor_body)
	
	# World Environment (Sky/Light)
	var env = WorldEnvironment.new()
	var environment = Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.5, 0.7, 0.9) 
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(1.0, 1.0, 1.0) # Full brightness ambient
	env.environment = environment
	add_child(env)
	
	# Directional Light - Disable shadows if enclosure blocks it
	var light = DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-45, 45, 0)
	light.shadow_enabled = false # Shadows might make it pitch black if inside a box
	add_child(light)
	
	# Add an OmniLight for interior fill
	var omni = OmniLight3D.new()
	omni.omni_range = 50.0
	omni.light_energy = 2.0
	omni.position = Vector3(0, 10, 0)
	add_child(omni)

	# 2. Sections Setup
	# Radius from center - Adjusted to be closer (User reported only Math visible, likely clipping)
	var r = 12.0 
	
	setup_section("English", Vector3(0, 0, -r), Color.RED)        # North
	setup_section("History", Vector3(r, 0, 0), Color.BLUE, -90)   # East
	setup_section("Math",    Vector3(0, 0, r), Color.GREEN, 180) # South
	setup_section("Science", Vector3(-r, 0, 0), Color.PURPLE, 90) # West
	
	# Add a second fill light
	var omni2 = OmniLight3D.new()
	omni2.omni_range = 50.0
	omni2.light_energy = 1.5
	omni2.position = Vector3(0, 5, 20) # Other side
	add_child(omni2)
	
	# 3. College Portal
	setup_college_portal()

func setup_section(category: String, pos: Vector3, color: Color, rot_deg: float = 0):
	# Create a "Shelf Interaction Area"
	var shelf_area = StaticBody3D.new() 
	shelf_area.position = pos
	shelf_area.rotation_degrees = Vector3(0, rot_deg, 0)
	shelf_area.set_meta("shelf_category", category)
	shelf_area.add_to_group("interactable")
	add_child(shelf_area)
	
	# REMOVED: Large blocking collision box
	# Instead, rely on individual book areas for selection.
	# If we need physical collision for player, we should add a smaller box BEHIND books.
	var col = CollisionShape3D.new() 
	var shape = BoxShape3D.new()
	shape.size = Vector3(6, 4, 1) # Thin backing
	col.shape = shape
	col.position = Vector3(0, 2.0, -0.5) # Push back
	shelf_area.add_child(col)
	
	for b in range(5):
		# Create Interactable Book Area
		var book_area = Area3D.new()
		# Position logic:
		# Row 1
		book_area.position = Vector3((b * 0.6) - 1.2, 1.0, 0.2) # Slight forward stick out
		book_area.rotation_degrees = Vector3(0, 90 + randf_range(-10, 10), 0)
		shelf_area.add_child(book_area)
		
		# Mesh
		var book_mesh_inst = MeshInstance3D.new()
		var mesh_res = load("res://assets/models/Books/Book.obj")
		if mesh_res and mesh_res is Mesh:
			book_mesh_inst.mesh = mesh_res
		else:
			book_mesh_inst.mesh = BoxMesh.new()
			book_mesh_inst.mesh.size = Vector3(0.2, 0.4, 0.8)
			
		book_mesh_inst.scale = Vector3(0.15, 0.15, 0.15)
		
		# Color override
		var mat = StandardMaterial3D.new()
		mat.albedo_color = color.lightened(randf() * 0.2)
		book_mesh_inst.material_override = mat
		
		book_area.add_child(book_mesh_inst)
		
		# Collision for Raycast
		var b_col = CollisionShape3D.new()
		var b_shape = BoxShape3D.new()
		b_shape.size = Vector3(0.2, 0.4, 0.8) * 0.3 # Larger hit box than mesh just in case
		b_col.shape = b_shape
		# Adjust collision center if needed
		b_col.position = Vector3(0, 0.1, 0)
		book_area.add_child(b_col)
		
		# Metadata for Interaction
		var topic_name = category + " " + str(b + 1)
		book_area.set_meta("topic", topic_name)
		book_area.add_to_group("interactable")

		# Row 2 (Higher)
		var book2 = book_area.duplicate()
		book2.position = Vector3((b * 0.6) - 1.2, 2.5, 0.2)
		book2.rotation_degrees = Vector3(0, 90 + randf_range(-10, 10), 0)
		
		# Metadata for Row 2
		var topic_name_2 = category + " " + str(b + 6)
		book2.set_meta("topic", topic_name_2)
		
		shelf_area.add_child(book2)

	# Label
	var label = Label3D.new()
	label.text = category
	label.font_size = 128 # Larger text
	label.position = Vector3(0, 3.0, 0) # Lower slightly
	label.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	label.modulate = Color(1, 1, 1) # White text for better visibility on dark wood?
	label.outline_render_priority = 0
	label.outline_size = 4 # Outline for readability
	shelf_area.add_child(label)
	
	# 3D Progress Gauge
	var progress = ProgressBar.new()
	progress.value = 0 # Todo: fetch from backend
	progress.show_percentage = true
	progress.custom_minimum_size = Vector2(200, 30)
	
	var vp = SubViewport.new()
	vp.size = Vector2(200, 30)
	vp.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	vp.add_child(progress)
	
	var vp_mesh = MeshInstance3D.new()
	vp_mesh.mesh = PlaneMesh.new()
	vp_mesh.mesh.size = Vector2(1, 0.15)
	vp_mesh.mesh.orientation = PlaneMesh.FACE_Z
	vp_mesh.rotation_degrees = Vector3(0, 180, 0) # Flip to face forward?
	vp_mesh.position = Vector3(0, 3.0, 0.6)
	
	var vp_mat = StandardMaterial3D.new()
	var tex = vp.get_texture()
	vp_mat.albedo_texture = tex
	vp_mesh.material_override = vp_mat
	
	shelf_area.add_child(vp)
	shelf_area.add_child(vp_mesh)

func setup_college_portal():
	var portal = Area3D.new()
	portal.position = Vector3(0, 1, 12) # Far end?
	add_child(portal)
	
	var mesh = MeshInstance3D.new()
	mesh.mesh = CylinderMesh.new()
	mesh.mesh.height = 0.1
	mesh.mesh.top_radius = 1.0
	mesh.mesh.bottom_radius = 1.0
	portal.add_child(mesh)
	
	var col = CollisionShape3D.new()
	var shape = CylinderShape3D.new()
	shape.height = 2.0
	shape.radius = 1.0
	col.shape = shape
	col.position = Vector3(0, 1, 0)
	portal.add_child(col)
	
	var label = Label3D.new()
	label.text = "College Portal"
	label.position = Vector3(0, 2, 0)
	portal.add_child(label)
	
	# Signal
	portal.body_entered.connect(_on_portal_entered)

func _on_portal_entered(body):
	if body.name == "Player":
		print("College Portal Entered!")
		# Simple feedback for now
		hud_xp.text = "Welcome to College!"


func _on_interaction(collider):
	print("Library received interaction with: ", collider)
	if collider.has_meta("topic"):
		var topic = collider.get_meta("topic")
		
		# Adaptive Logic Check
		if not GameManager.manual_selection_mode:
			# If NOT manual, we enforce the player's grade level.
			# e.g. topic "Math 3" -> "Math 10" if player is grade 10
			var parts = topic.split(" ")
			if parts.size() >= 2:
				var subject = parts[0] # "Math"
				# Construct new topic with user's grade
				# Handle "Math 10" vs "Math 1"
				topic = subject + " " + str(GameManager.player_grade)
				print("Adaptive Mode: Overriding topic to " + topic)
		
		goto_classroom(topic)
	elif collider.has_meta("shelf_category"):
		var cat = collider.get_meta("shelf_category")
		print("Shelf selected: " + cat)
		resume_shelf(cat)
	elif collider.get_parent().has_meta("topic"):
		goto_classroom(collider.get_parent().get_meta("topic"))


func resume_shelf(category):
	var game_manager = get_node("/root/GameManager")
	var data = {
		"username": game_manager.player_username,
		"shelf_category": category
	}
	NetworkManager.post_request("/resume_shelf", data, _on_resume_success, _on_resume_fail)

func _on_resume_success(_code, response):
	print("Resuming: " + response["topic"])
	goto_classroom(response["topic"])

func _on_resume_fail(_code, err):
	print("Error resuming shelf: " + err)

func goto_classroom(topic):
	print("Switching to classroom for topic: ", topic)
	var game_manager = get_node("/root/GameManager")
	if game_manager:
		game_manager.set_topic(topic)
	
	get_tree().change_scene_to_file("res://scenes/Classroom.tscn")
