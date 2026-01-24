extends Control

class_name VirtualJoystick

# Helper class for on-screen joystick
# Emits a vector and input strength

@export var joystick_mode: String = "Movement" # or "Look"
@export var deadzone: float = 0.2
@export var clamp_to_circle: bool = true

var input_vector: Vector2 = Vector2.ZERO
var _touch_index: int = -1
var _base_radius: float = 0.0
var _handle_radius: float = 0.0

@onready var _base = $Base
@onready var _handle = $Base/Handle

func _ready():
	# Assume Base is circular-ish, size is diameter
	_base_radius = _base.size.x / 2.0
	_handle_radius = _handle.size.x / 2.0
	
	# Center handle
	_handle.position = Vector2(_base_radius - _handle_radius, _base_radius - _handle_radius)
	
	# Hide if not touch? Or let parent manage visibility.
	# if not OS.has_feature("touchscreen"): hide()

func _physics_process(_delta):
	pass

func _input(event):
	if event is InputEventScreenTouch:
		if event.pressed:
			if _touch_index == -1:
				# Check if touch inside base
				var center = _base.global_position + Vector2(_base_radius, _base_radius)
				if event.position.distance_to(center) < _base_radius * 1.5: # Generous hit area
					_touch_index = event.index
					_update_joystick(event.position)
		elif event.index == _touch_index:
			_reset_joystick()
			
	elif event is InputEventScreenDrag:
		if event.index == _touch_index:
			_update_joystick(event.position)

func _update_joystick(touch_pos: Vector2):
	var center = _base.global_position + Vector2(_base_radius, _base_radius)
	var local = touch_pos - center
	
	var dist = local.length()
	if clamp_to_circle:
		if dist > _base_radius:
			local = local.normalized() * _base_radius
			
	_handle.global_position = center + local - Vector2(_handle_radius, _handle_radius)
	
	# Calculate normalized vector
	input_vector = local / _base_radius
	
	# Deadzone
	if input_vector.length() < deadzone:
		input_vector = Vector2.ZERO

func _reset_joystick():
	_touch_index = -1
	input_vector = Vector2.ZERO
	# Re-center
	_handle.position = Vector2(_base_radius - _handle_radius, _base_radius - _handle_radius)

func get_output() -> Vector2:
	return input_vector
