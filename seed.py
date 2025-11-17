import random
from faker import Faker
from werkzeug.security import generate_password_hash
from app import app, db
from app.db_models import User, Item, Cart, Order, Ordered_item

fake = Faker()

def seed_users(n=5):
    users = []
    admin_info = None
    for i in range(n):
        is_admin = True if i == 0 else False  # first user is admin
        password = "Admin123!" if is_admin else fake.password(length=10)
        user = User(
            name=fake.name(),
            email=fake.unique.email(),
            phone=fake.phone_number(),
            password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8),
            admin=is_admin,
            email_confirmed=True
        )
        db.session.add(user)
        users.append((user, password))  # tuple: (user_obj, plain_password)
        if is_admin:
            admin_info = {"email": user.email, "password": password}
    db.session.commit()
    return users, admin_info

def seed_items(n=10):
    items = []
    categories = ["Electronics", "Books", "Clothing", "Toys"]
    for _ in range(n):
        item = Item(
            name=fake.unique.word().title(),
            price=round(random.uniform(10, 500), 2),
            category=random.choice(categories),
            image="https://via.placeholder.com/150",
            details=fake.sentence(),
            price_id=f"price_{random.randint(1000,9999)}"
        )
        db.session.add(item)
        items.append(item)
    db.session.commit()
    return items

def seed_cart(users, items, n=10):
    for _ in range(n):
        user = random.choice(users)
        item = random.choice(items)
        quantity = random.randint(1, 5)
        cart_item = Cart(
            uid=user.id,
            itemid=item.id,
            quantity=quantity
        )
        db.session.add(cart_item)
    db.session.commit()

def seed_orders(users, items, n=5):
    for _ in range(n):
        user = random.choice(users)
        order = Order(
            uid=user.id,
            date=fake.date_time_this_year(),
            status=random.choice(["Pending", "Shipped", "Delivered"])
        )
        db.session.add(order)
        db.session.commit()

        # Add 1-3 ordered items per order
        for _ in range(random.randint(1, 3)):
            item = random.choice(items)
            ordered_item = Ordered_item(
                oid=order.id,
                itemid=item.id,
                quantity=random.randint(1, 5)
            )
            db.session.add(ordered_item)
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        # Reset database
        db.drop_all()
        db.create_all()

        # Seed users and get admin credentials
        users, admin_credentials = seed_users(5)  # Make sure your seed_users returns (users_list, admin_info)

        # Seed other tables
        items = seed_items(10)
        seed_cart([u[0] for u in users], items, 10)  # if users is list of tuples
        seed_orders([u[0] for u in users], items, 5)

        # Print admin login info
        print(f"Admin credentials -> Email: {admin_credentials['email']}, Password: {admin_credentials['password']}")

        print("Database seeded successfully!")

