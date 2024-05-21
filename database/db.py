from collections import defaultdict
import traceback
from sqlalchemy import Float, create_engine, Column, Integer, String, ForeignKey, Sequence, UniqueConstraint, desc, exists, text, update
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from settings import HOST, NAME_DB, PASSWORD, PORT, USERNAME

username = USERNAME
password = PASSWORD
port = PORT
name_db = NAME_DB
host = HOST

engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{name_db}')
Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    price = Column(Integer)
    url = Column(String, nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=False)

    category = relationship("Сategory", backref="products") 

    def __repr__(self):
        return f"Product(id={self.id}, name='{self.name}', price={self.price}, url={self.url}, category_id={self.category_id})"

class Сategory(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String, nullable=False, unique=True) 

    __table_args__ = (
        UniqueConstraint('url', name='uq_category_url'),
    )

    def __repr__(self):
        return f"Сategory(id={self.id}, username='{self.name}')"
    
class Section(Base):
    __tablename__ = 'sections'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    url = Column(String, nullable=False, unique=True)

    __table_args__ = (
        UniqueConstraint('url', name='uq_section_url'),
    )

    def __repr__(self):
        return f"Section(id={self.id}, url='{self.url}')"
    
class UserProduct(Base):
    __tablename__ = 'user_products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    quantity = Column(Float)
    price = Column(Integer)
    status_price = Column(String)
    list_id = Column(Integer, ForeignKey('user_product_lists.list_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    similar_name = Column(String)

    user = relationship("User", backref="user_products") 
    product_list = relationship("UserProductList", backref="user_products")

    def __repr__(self):
        return f"UserProduct(id={self.id}, name='{self.name}', quantity={self.quantity}, price={self.price}, list_id={self.list_id}, user_id={self.user_id})"
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)

    def __repr__(self):
        return f"User(id={self.id}, username='{self.username}')"

class UserProductList(Base):
    __tablename__ = 'user_product_lists'

    id = Column(Integer, primary_key=True)
    list_id = Column(Integer, Sequence('user_product_lists_seq'), unique=True, nullable=False)

    def __repr__(self):
        return f"UserProductList(id={self.id}, list_id={self.list_id})"

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def writing_to_product(json_data):
    session = Session()
    try:
        for product in json_data:
            p = UserProduct(
                name=product['name'],
                quantity=product['quantity'],
                price=product['price'],
                status_price=['status_price'],
                list_id=product['list_id'],
                user_id=product['user_id']
            )
            session.add(p)
        session.commit()
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        raise Exception(repr(e))
    finally:
        session.close()

def update_product_prices(data_list):
    session = Session()
    try:
        for data in data_list:
            product_id = data['product_id']
            full_price = data['full_price']
            status_price = data['status']
            similar_name = data['similar_name']

            stmt = update(UserProduct).where(
                UserProduct.id == product_id
            ).values(price=full_price, status_price=status_price, similar_name=similar_name)
            session.execute(stmt)
            session.commit()

    finally:
        session.close()

def writing_to_users(user_id, first_name, last_name):
    session = Session()
    try:
        u = User(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name
        )
        session.add(u)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def writing_to_product_list():
    session = Session()
    new_list = UserProductList()
    session.add(new_list)
    session.commit()
    session.close()

def get_last_plist():
    session = Session()
    last_record = session.query(UserProductList).order_by(UserProductList.list_id.desc()).first()
    session.close()
    if last_record:
        return last_record
    else:
        return None
    
def get_user_id(user_id):
    session = Session()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        if user:
            return user.id
        else:
            return False
    finally:
        session.close()

def get_all_plist(user_id):
    session = Session()
    try:
        all_plist = session.query(UserProduct).filter(UserProduct.user_id == user_id).all() 
        if all_plist:
            grouped_products = defaultdict(list)
            for product in all_plist:
                grouped_products[product.list_id].append(product.__dict__)
            return dict(grouped_products)
    finally:
        session.close()

def get_last_plist():
    session = Session()
    try:
        last_record = session.query(UserProductList).order_by(desc(UserProductList.id)).first()
        last_plist = last_record.list_id
        return last_plist
    finally:
        session.close()

def get_last_products(last_plist, user_id):
    session = Session()
    try:
        user = session.query(User).filter(User.user_id == user_id).first()
        bd_user_id = user.id
        list_products = session.query(UserProduct).filter(UserProduct.user_id == bd_user_id, UserProduct.list_id == last_plist).all()
        if not list_products:
            text_answer = f'В списке №{last_plist} ничего нет.\nВидимо он пуст, попробуй посмотреть все списки.'
            return text_answer
        text_answer = f'Последний список №{last_plist} и вот что там было:\n'
        for product in list_products:
            name = product.name
            quantity = product.quantity 
            text_answer += f'{name} {quantity}\n'
        return text_answer
    finally:
        session.close()

def writing_to_sections(all_sections_list):
    session = Session()
    try:
        for section in all_sections_list:
            url=section['url']
            db_link = session.query(exists().where(Section.url == url)).scalar()
            if not db_link:
                sec = Section(
                    name=section['name'],
                    url=url
                )
                session.add(sec)
            else:
                continue
        session.commit()
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        raise Exception(repr(e))
    finally:
        session.close()

def get_all_sections():
    session = Session()
    try:
        sections = session.query(Section).all()
        sections_dict = {section.id: section.url for section in sections}
        return sections_dict
    finally:
        session.close()

def writing_to_categories(all_categories_list):
    session = Session()
    try:
        for category in all_categories_list:
            name_cat = category['name_category']
            link_cat = category['link_category']
            db_link = session.query(exists().where(Сategory.url == link_cat)).scalar()
            if not db_link:
                category_db = Сategory(
                    name=name_cat,
                    url=link_cat
                )
                session.add(category_db)
            else:
                continue
        session.commit()                
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        raise Exception(repr(e))
    finally:
        session.close()

def get_all_categories():
    session = Session()
    try:
        categories = session.query(Сategory).all()
        categories_dict = {category.id: category.url for category in categories}
        return categories_dict
    finally:
        session.close()

def writing_to_product_shop(all_products_list):
    session = Session()
    try:
        for product in all_products_list:
            name_product = product['name']
            price_product = product['price']
            url_product = product['url']
            category_id_product = product['category_id']
            db_link = session.query(exists().where(Product.url == url_product)).scalar()
            if not db_link:
                product_db = Product(
                    name=name_product,
                    price=price_product,
                    url=url_product,
                    category_id=category_id_product
                )
                session.add(product_db)
            else:
                continue
        session.commit()                
    except Exception as e:
        session.rollback()
        traceback.print_exc()
        raise Exception(repr(e))
    finally:
        session.close()

def get_id_section(url):
    session = Session()
    try:
        section = session.query(Section).filter_by(url=url).first()
        if section:
            return section.id
        else:
            return False
    finally:
        session.close()

def get_name_section(id):
    session = Session()
    try:
        section = session.query(Section).filter_by(id=id).first()
        if section:
            return section.name
        else:
            return False
    finally:
        session.close()

def get_id_category(url):
    session = Session()
    try:
        section = session.query(Сategory).filter_by(url=url).first()
        if section:
            return section.id
        else:
            return False
    finally:
        session.close() 
    
def get_all_categories_list():
    session = Session()
    try:
        categories = session.query(Сategory).all()
        categories_list = [{'name': category.name, 'url': category.url} for category in categories]
        return categories_list
    finally:
        session.close()
    
def get_all_section_list():
    session = Session()
    try:
        sections = session.query(Section).all()
        sections_list = [{'name': section.name, 'url': section.url} for section in sections]
        return sections_list
    finally:
        session.close()

def get_all_user_products():
    session = Session()
    try:
        products = session.query(UserProduct).filter(UserProduct.price == 0).all()
        product_list = [{'name': product.name, 'quantity': product.quantity, 'product_id': product.id} for product in products]
        return product_list
    finally:
        session.close()