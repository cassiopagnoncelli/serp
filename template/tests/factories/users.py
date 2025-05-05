from app.models import User

def create_user(db, **kwargs):
    user = User(name=kwargs.get("name", "Test"), email=kwargs.get("email", "test@example.com"))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
