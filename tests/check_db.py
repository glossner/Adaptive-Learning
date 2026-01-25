from backend.database import SessionLocal, Player

def check_user(username):
    db = SessionLocal()
    player = db.query(Player).filter(Player.username == username).first()
    if player:
        print(f"User: {player.username}")
        print(f"Grade: {player.grade_level}")
        print(f"Location: {player.location}")
    else:
        print(f"User {username} not found.")
    db.close()

if __name__ == "__main__":
    check_user("hkoehn")
