extends Node

var current_topic: String = ""
var player_username = "Player1"
var player_grade = 10
var player_location = "New Hampshire"
var player_style = "Visual"

# Simple Global to hold state between scenes
func set_topic(topic: String):
	current_topic = topic
