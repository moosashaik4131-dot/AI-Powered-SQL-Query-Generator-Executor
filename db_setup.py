import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from faker import Faker
import random

load_dotenv()

Base = declarative_base()
fake = Faker()

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(120))
    city = Column(String(100))

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    category = Column(String(100))
    price = Column(Float)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    order_date = Column(Date)
    customer = relationship("Customer")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    order = relationship("Order")
    product = relationship("Product")

def seed_database(db_path=None):
    db_path = db_path or os.getenv("DB_URL")
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    categories = ["Electronics", "Books", "Clothing", "Home & Kitchen", "Toys"]

    customers = [Customer(name=fake.name(), email=fake.email(), city=fake.city()) for _ in range(30)]
    products = [Product(name=fake.word().capitalize() + " " + fake.word().capitalize(),
                         category=random.choice(categories),
                         price=round(random.uniform(5, 500), 2)) for _ in range(20)]
    session.add_all(customers + products)
    session.commit()

    orders = []
    for _ in range(80):
        order = Order(customer_id=random.choice(customers).id,
                       order_date=fake.date_between(start_date="-1y", end_date="today"))
        orders.append(order)
    session.add_all(orders)
    session.commit()

    items = []
    for order in orders:
        for _ in range(random.randint(1, 4)):
            items.append(OrderItem(order_id=order.id,
                                    product_id=random.choice(products).id,
                                    quantity=random.randint(1, 5)))
    session.add_all(items)
    session.commit()

    print("Database seeded successfully.")

if __name__ == "__main__":
    seed_database()