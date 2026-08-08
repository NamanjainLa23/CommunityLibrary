import random
from app.db import SessionLocal, Base, engine
from app.models.user import User
from app.models.community import Community
from app.models import book, borrow  # noqa: ensure related models load
from app.core.security import get_password_hash
Base.metadata.create_all(bind=engine)
db = SessionLocal()
communities = db.query(Community).all()
if not communities:
    raise SystemExit("No communities found. Insert communities first.")
password_hash = get_password_hash("password123")
users_data = [
    ("user",  "namanjainj363@gmail.com",  "Naman",   "Jain",  "9897600364"),
    ("user0",  "namanjain32111@gmail.com",  "Prince",   "Jain",  "9000000000"),
    ("user1",  "nikita.nyu30@mail.com",  "Nikita",   "Gupta",  "9000000001"),
    ("user2",  "user2@example.com",  "Rohan",  "Mehta",   "9000000002"),
    ("user3",  "user3@example.com",  "Priya",  "Nair",    "9000000003"),
    ("user4",  "user4@example.com",  "Vikram", "Singh",   "9000000004"),
    ("user5",  "user5@example.com",  "Neha",   "Patel",   "9000000005"),
    ("user6",  "user6@example.com",  "Arjun",  "Rao",     "9000000006"),
    ("user7",  "user7@example.com",  "Kavya",  "Iyer",    "9000000007"),
    ("user8",  "user8@example.com",  "Aditya", "Joshi",   "9000000008"),
    ("user9",  "user9@example.com",  "Sneha",  "Gupta",   "9000000009"),
    ("user10", "user10@example.com", "Rahul",  "Verma",   "9000000010"),
    ("user11", "user11@example.com", "Ananya", "Das",     "9000000011"),
    ("user12", "user12@example.com", "Karan",  "Malhotra","9000000012"),
]
created = []
for username, email, first, last, mobile in users_data:
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        created.append(existing)
        continue
    user = User(
        username=username,
        email=email,
        hashed_password=password_hash,
        first_name=first,
        last_name=last,
        mobile=mobile,
        is_active=True,
    )
    # assign 2–3 random communities
    user.communities = random.sample(communities, k=min(3, len(communities)))
    db.add(user)
    created.append(user)
db.commit()
print(f"Users: {db.query(User).count()}")
for u in db.query(User).all():
    names = [c.name for c in u.communities]
    print(f"  {u.username}: {names}")
db.close()
print("\nLogin with any user, password: password123")