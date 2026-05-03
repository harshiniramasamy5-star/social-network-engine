from graph import social

def seed():
    users = [
        (1,  "Harshini",  "CS Student & Developer"),
        (2,  "Arjun",     "ML Engineer at Google"),
        (3,  "Priya",     "Full Stack Developer"),
        (4,  "Ravi",      "Data Scientist"),
        (5,  "Meera",     "UI/UX Designer"),
        (6,  "Kiran",     "Backend Engineer"),
        (7,  "Divya",     "DevOps Engineer"),
        (8,  "Sanjay",    "Product Manager"),
        (9,  "Ananya",    "AI Researcher"),
        (10, "Vikram",    "Startup Founder"),
        (11, "Lakshmi",   "Software Architect"),
        (12, "Rahul",     "Cybersecurity Expert"),
    ]
    for uid, name, bio in users:
        social.add_user(uid, name, bio)

    follows = [
        (1,2),(1,3),(1,4),(1,9),
        (2,1),(2,4),(2,9),(2,11),
        (3,1),(3,5),(3,6),(3,8),
        (4,2),(4,9),(4,11),
        (5,3),(5,8),(5,10),
        (6,3),(6,7),(6,11),
        (7,6),(7,12),
        (8,3),(8,5),(8,10),
        (9,2),(9,4),(9,11),
        (10,5),(10,8),(10,12),
        (11,2),(11,4),(11,9),
        (12,7),(12,10),
    ]
    for f, t in follows:
        social.follow(f, t)

    print(f"Seeded: {len(users)} users, {len(follows)} follows")

if __name__ == "__main__":
    seed()