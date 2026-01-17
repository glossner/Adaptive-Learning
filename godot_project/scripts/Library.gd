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
	var floor_mesh = MeshInstance3D.new()
	floor_mesh.mesh = BoxMesh.new()
	floor_mesh.mesh.size = Vector3(40, 0.5, 40)
	floor_mesh.position.y = -0.25
	floor_mesh.create_trimesh_collision()
	add_child(floor_mesh)
	
	var light = DirectionalLight3D.new()
	light.rotation_degrees = Vector3(-60, -30, 0)
	light.shadow_enabled = true
	add_child(light)
	
	var categories = ["Mathematics", "History", "Science", "Literature"]
	var colors = [Color.RED, Color.BLUE, Color.GREEN, Color.PURPLE]
	
	for i in range(len(categories)):
		var z_offset = -10 + (i * 6)
		create_shelf_row(Vector3(-5, 0, z_offset), categories[i], colors[i])
		create_shelf_row(Vector3(5, 0, z_offset), categories[i], colors[i])

func create_shelf_row(pos: Vector3, category: String, color: Color):
	var shelf = MeshInstance3D.new()
	shelf.mesh = BoxMesh.new()
	shelf.mesh.size = Vector3(8, 3, 1)
	shelf.position = pos + Vector3(0, 1.5, 0)
	shelf.create_trimesh_collision()
	add_child(shelf)
	
	for b in range(10):
		var book = Area3D.new()
		var mesh = MeshInstance3D.new()
		mesh.mesh = BoxMesh.new()
		mesh.mesh.size = Vector3(0.2, 0.4, 0.8) 
		mesh.position = Vector3((b * 0.7) - 3.5, 0, 0.6) 
		
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
		
		# Visual Checks
		var topic_name = category + " " + str(b+1)
		book.set_meta("topic", topic_name)
		book.add_to_group("interactable")
		shelf.add_child(book)
		
		# Better Label
		var label = Label3D.new()
		label.text = topic_name
		label.font_size = 128
		label.scale = Vector3(0.05, 0.05, 0.05)
		label.position = mesh.position + Vector3(0, 0, 0.42)
		label.rotation_degrees = Vector3(0, 0, 90)
		label.modulate = Color.BLACK 
		label.outline_render_priority = 0
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		book.add_child(label)
		
		# Debug
		print("Created book: " + topic_name + " at " + str(book.global_position))

func _on_interaction(collider):
	print("Library received interaction with: ", collider)
	if collider.has_meta("topic"):
		var topic = collider.get_meta("topic")
		print("Player selected topic: " + topic)
		goto_classroom(topic)
	elif collider.get_parent().has_meta("topic"):
		var topic = collider.get_parent().get_meta("topic")
		print("Player selected topic (parent): " + topic)
		goto_classroom(topic)
	else:
		print("Selected object has no topic meta.")

func goto_classroom(topic):
	print("Switching to classroom for topic: ", topic)
	var game_manager = get_node("/root/GameManager")
	if game_manager:
		game_manager.set_topic(topic)
	else:
		print("GameManager not found! Create Autoload.")
	
	get_tree().change_scene_to_file("res://scenes/Classroom.tscn")
