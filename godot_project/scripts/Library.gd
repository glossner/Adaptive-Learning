extends Node3D

var network_manager
var player

var hud_xp: Label
var hud_level: Label

func _ready():
	randomize()
	setup_full_library()
	setup_ui()
	
	# Connect player interaction
	var player_scn = load("res://scenes/Player.tscn")
	player = player_scn.instantiate()
	player.position = Vector3(0, 0.5, 0)
	player.interaction_requested.connect(_on_interaction)
	add_child(player)

func setup_ui():
	var canvas = CanvasLayer.new()
	add_child(canvas)
	
	hud_xp = Label.new()
	hud_xp.text = "XP: 0"
	hud_xp.position = Vector2(20, 20)
	canvas.add_child(hud_xp)
	
	hud_level = Label.new()
	hud_level.text = "Lvl: 1"
	hud_level.position = Vector2(20, 40)
	canvas.add_child(hud_level)

	# Controls Help
	var help = Label.new()
	help.text = "Controls:\n[WASD] Move\n[Mouse] Look\n[Left Click] Select / Capture Mouse\n[ESC] Release Mouse"
	help.position = Vector2(20, 80)
	help.modulate = Color(1, 1, 1, 0.7)
	canvas.add_child(help)

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
	
	# Directional Light - Adjust angle to hit player face
	var light = DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-45, 45, 0)
	light.shadow_enabled = true
	add_child(light)

<<<<<<< HEAD
	# 2. Sections Setup (Manual Placement based on Library Layout)
	# The room seems large. Let's push sections out further.
	# Alphabetical: English, History, Math, Science
=======
func create_shelf_row(pos: Vector3, category: String, color: Color):
	# Shelf Container (Static Body for Interaction)
	var shelf_body = StaticBody3D.new()
	shelf_body.position = pos + Vector3(0, 1.5, 0)
	shelf_body.set_meta("shelf_category", category)
	shelf_body.add_to_group("interactable")
	add_child(shelf_body)
	
	var shelf_mesh = MeshInstance3D.new()
	shelf_mesh.mesh = BoxMesh.new()
	shelf_mesh.mesh.size = Vector3(8, 3, 1)
	shelf_body.add_child(shelf_mesh)
	
	var col = CollisionShape3D.new()
	var shape = BoxShape3D.new()
	shape.size = shelf_mesh.mesh.size
	col.shape = shape
	shelf_body.add_child(col)
>>>>>>> d9c09d09b62b9235f98ba2d618ca78ae2f20b220
	
	# Radius from center
	var r = 18.0 
	
	setup_section("English", Vector3(0, 0, -r), Color.RED)        # North
	setup_section("History", Vector3(r, 0, 0), Color.BLUE, -90)   # East
	setup_section("Literature", Vector3(0, 0, r), Color.YELLOW, 180) # South (Wait, Math?)
	# User asked for: English, History, Math, Science.
	# Let's do:
	# English (North)
	# History (East)
	# Math (South)
	# Science (West)
	
	setup_section("English", Vector3(0, 0, -r), Color.RED)
	setup_section("History", Vector3(r, 0, 0), Color.BLUE, -90)
	setup_section("Math",    Vector3(0, 0, r), Color.GREEN, 180)
	setup_section("Science", Vector3(-r, 0, 0), Color.PURPLE, 90)
	
	# 3. College Portal
	setup_college_portal()

func setup_section(category: String, pos: Vector3, color: Color, rot_deg: float = 0):
	# Create a "Shelf Interaction Area"
	var shelf_area = StaticBody3D.new() # Using StaticBody for raycast interaction
	shelf_area.position = pos
	shelf_area.rotation_degrees = Vector3(0, rot_deg, 0)
	shelf_area.set_meta("shelf_category", category)
	shelf_area.add_to_group("interactable")
	add_child(shelf_area)
	
	# Invisible Collision Box for the whole shelf unit
	var col = CollisionShape3D.new() 
	var shape = BoxShape3D.new()
	shape.size = Vector3(4, 3, 1) # Size of a typical shelf unit
	col.shape = shape
	col.position = Vector3(0, 1.5, 0)
	shelf_area.add_child(col)
	
	# Add Books physically
	var book_scn = load("res://assets/models/Books/Book.obj") 
	# Note: .obj imports as Mesh, we need to handle it. Best to load as mesh.
	# Actually, easier to use MeshInstance with the array mesh from OBJ loader if auto-import works.
	# Or user might have a .tscn for it. Let's assume raw mesh for now.
	
	for b in range(5):
		var book_mesh_inst = MeshInstance3D.new()
		var mesh_res = load("res://assets/models/Books/Book.obj")
		if mesh_res and mesh_res is Mesh:
			book_mesh_inst.mesh = mesh_res
		else:
			book_mesh_inst.mesh = BoxMesh.new()
			book_mesh_inst.mesh.size = Vector3(0.2, 0.4, 0.8)
			
		# Adjust placement relative to shelf unit center
		# Shelf area is at 'pos'.
		# Assuming shelf faces -Z by default (rot 0).
		# We want books physically ON the shelf.
		# X spread: (b * 0.4) - 1.0 (Centered around 0)
		# Y height: 1.2 (Eye levelish). Maybe vary for multiple shelves?
		# Z depth: Push back against wall? If shelf is at 0,0,0 relative, maybe back is at -0.5?
		# Adjusted Z to -0.4 to sit on shelf
		
		# Let's add multiple rows of books?
		# Row 1 (Lower)
		book_mesh_inst.position = Vector3((b * 0.5) - 1.0, 1.0, -0.2)
		book_mesh_inst.scale = Vector3(0.15, 0.15, 0.15) 
		book_mesh_inst.rotation_degrees = Vector3(0, randf_range(-10, 10), 0) # Random wobble
		
		# Color override
		var mat = StandardMaterial3D.new()
		mat.albedo_color = color.lightened(randf() * 0.2)
		book_mesh_inst.material_override = mat
		
<<<<<<< HEAD
		shelf_area.add_child(book_mesh_inst)

	# Label
	var label = Label3D.new()
	label.text = category
	label.font_size = 96
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
=======
		# Collision
		var b_col = CollisionShape3D.new()
		var b_shape = BoxShape3D.new()
		b_shape.size = mesh.mesh.size
		b_col.shape = b_shape
		b_col.position = mesh.position
		
		# Add to shelf body? No, make books children of shelf logic
		# Note: Area3D inside StaticBody might be weird for raycast?
		# Better to keep books separate children of the main scene or just child of shelf_body but managed carefully.
		# Let's add books as children of shelf_body for transform hierarchy
		book.position = shelf_mesh.position + mesh.position # Adjust local pos
		
		# Re-do Book Logic slightly:
		book = Area3D.new()
		book.position = Vector3((b * 0.7) - 3.5, 0, 0.6)
		shelf_body.add_child(book)
		
		book.add_child(mesh) # Mesh at 0,0,0 relative to Book Area
		mesh.position = Vector3.ZERO
		
		b_col = CollisionShape3D.new()
		b_col.shape = b_shape
		book.add_child(b_col)

		# Visual Checks
		var topic_name = category + " " + str(b+1)
		book.set_meta("topic", topic_name)
		book.add_to_group("interactable")
		
		# Better Label
		var label = Label3D.new()
		label.text = topic_name
		label.font_size = 128
		label.scale = Vector3(0.05, 0.05, 0.05)
		label.position = Vector3(0, 0, 0.42)
		label.rotation_degrees = Vector3(0, 0, 90)
		label.modulate = Color.BLACK 
		label.outline_render_priority = 0
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		book.add_child(label)
>>>>>>> d9c09d09b62b9235f98ba2d618ca78ae2f20b220


func _on_interaction(collider):
	print("Library received interaction with: ", collider)
	if collider.has_meta("topic"):
		var topic = collider.get_meta("topic")
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
