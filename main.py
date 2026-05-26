import sys
import pymysql

from PyQt6 import uic
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

ROLE_GUEST = "Гость"
ROLE_CLIENT = "Клиент"
ROLE_MANAGER = "Менеджер"
ROLE_ADMIN = "Администратор"

connection = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    database="demo",
    cursorclass=pymysql.cursors.DictCursor
)

cursor = connection.cursor()


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi("login.ui", self)

        self.loginButton.clicked.connect(self.login)
        self.guestButton.clicked.connect(self.guest_enter)

    def login(self):
        login = self.loginEdit.text()
        password = self.passwordEdit.text()

        sql = """
        SELECT users.full_name,
               roles.role_name
        FROM users
        JOIN roles
        ON users.role_id = roles.role_id
        WHERE login=%s AND password=%s
        """

        cursor.execute(sql, (login, password))
        user = cursor.fetchone()

        if user:
            full_name = user["full_name"]
            role = user["role_name"]

            self.products = ProductsWindow(
                role,
                full_name
            )

            self.products.show()
            self.close()
        else:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Неверный логин или пароль"
            )

    def guest_enter(self):
        self.products = ProductsWindow(ROLE_GUEST, "Гость")
        self.products.show()
        self.close()

class ProductsWindow(QMainWindow):
    def __init__(self, role, full_name):
        super().__init__()

        uic.loadUi("products.ui", self)

        self.searchEdit.setVisible(False)
        self.filterBox.setVisible(False)
        self.sortBox.setVisible(False)
        self.ordersButton.setVisible(False)
        self.deleteButton.setVisible(False)

        self.role = role
        self.full_name = full_name

        self.labelUser.setText(full_name)

        self.container = QWidget()
        self.scrollArea.setWidget(self.container)
        self.scrollArea.setWidgetResizable(True)

        self.verticalLayout = QVBoxLayout(self.container)

        self.load_suppliers()
        self.load_products()
        self.setup_role()

        self.backButton.clicked.connect(self.go_back)
        self.ordersButton.clicked.connect(self.open_orders)

        self.searchEdit.textChanged.connect(self.load_products)
        self.filterBox.currentTextChanged.connect(self.load_products)
        self.sortBox.currentTextChanged.connect(self.load_products)

    def load_products(self):

        for i in reversed(range(self.verticalLayout.count())):
            widget = self.verticalLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        search = self.searchEdit.text()
        supplier = self.filterBox.currentText()
        sort = self.sortBox.currentText()

        sql = """
        SELECT
            p.product_name,
            c.category_name,
            p.description,
            m.manufacturer_name,
            s.supplier_name,
            p.price,
            p.unit,
            p.discount,
            p.stock_quantity,
            p.image_path
        FROM products p
        JOIN categories c ON p.category_id = c.category_id
        JOIN manufacturers m ON p.manufacturer_id = m.manufacturer_id
        JOIN suppliers s ON p.supplier_id = s.supplier_id
        WHERE (p.product_name LIKE %s
        OR c.category_name LIKE %s
        OR m.manufacturer_name LIKE %s
        OR s.supplier_name LIKE %s)
        """

        params = [
            f"%{search}%",
            f"%{search}%",
            f"%{search}%",
            f"%{search}%"
        ]

        # фильтр по поставщику
        if supplier != "Все поставщики":
            sql += " AND s.supplier_name=%s"
            params.append(supplier)

        # сортировка
        if sort == "По возрастанию":
            sql += " ORDER BY p.stock_quantity ASC"

        elif sort == "По убыванию":
            sql += " ORDER BY p.stock_quantity DESC"

        cursor.execute(sql, params)

        products = cursor.fetchall()

        for product in products:
            card = self.create_product_card(product)
            self.verticalLayout.addWidget(card)

    def create_product_card(self, product):
        card = QWidget()
        card_layout = QHBoxLayout(card)

        image_label = QLabel()
        image_label.setFixedSize(120, 120)

        pixmap = QPixmap(product["image_path"])

        if pixmap.isNull():
            image_label.setText("Нет фото")
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            image_label.setPixmap(pixmap.scaled(120, 120))

        info_text = (
            f"Категория: {product['category_name']}\n"
            f"Название: {product['product_name']}\n"
            f"Описание: {product['description']}\n"
            f"Производитель: {product['manufacturer_name']}\n"
            f"Поставщик: {product['supplier_name']}\n"
            f"Цена: {product['price']} руб.\n"
            f"Единица измерения: {product['unit']}\n"
            f"Количество: {product['stock_quantity']}"
        )

        info_label = QLabel(info_text)
        info_label.setWordWrap(True)

        discount_label = QLabel(str(product["discount"]) + "%")

        card_layout.addWidget(image_label)
        card_layout.addWidget(info_label)
        card_layout.addWidget(discount_label)

        card.setStyleSheet("QWidget {border: 1px solid black;}")
        image_label.setStyleSheet("border: 1px solid black;")
        info_label.setStyleSheet("border: 1px solid black;")
        discount_label.setStyleSheet("border: 1px solid black;")
        discount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        return card

    def setup_role(self):

        if self.role == ROLE_GUEST:
            self.labelUser.setText("Вы вошли как Гость")

        elif self.role == ROLE_CLIENT:
            self.labelUser.setText(self.full_name)

        elif self.role == ROLE_MANAGER:
            self.labelUser.setText(f"{self.full_name} (Менеджер)")
            self.enable_manager_features()

        elif self.role == ROLE_ADMIN:
            self.labelUser.setText(f"{self.full_name} (Админ)")
            self.enable_manager_features()
            self.enable_admin_features()

    def enable_manager_features(self):
        self.searchEdit.setVisible(True)
        self.filterBox.setVisible(True)
        self.sortBox.setVisible(True)
        self.ordersButton.setVisible(True)


    def enable_admin_features(self):
        self.enable_manager_features()
        self.deleteButton.setVisible(True)

    def delete_product(self):
        print("Удаление товара (позже сделаем SQL)")

    def go_back(self):
        self.login = LoginWindow()
        self.login.show()
        self.close()

    def open_orders(self):

        self.orders_window = OrdersWindow(self.role)
        self.orders_window.show()

    def load_suppliers(self):

        sql = """
        SELECT supplier_name
        FROM suppliers
        """

        cursor.execute(sql)
        suppliers = cursor.fetchall()

        self.filterBox.clear()
        self.filterBox.addItem("Все поставщики")

        for supplier in suppliers:
            self.filterBox.addItem(supplier["supplier_name"])

class OrdersWindow(QMainWindow):
    def __init__(self, role):
        super().__init__()

        uic.loadUi("orders.ui", self)

        self.role = role

        self.load_orders()
        self.backButton.clicked.connect(self.go_back)
        if self.role != ROLE_ADMIN:
            self.deleteButton.setVisible(False)

    def go_back(self):
        self.close()

    def load_orders(self):

        sql = """
        SELECT 
            order_id,
            code,
            order_date,
            delivery_date,
            status
        FROM orders
        """

        cursor.execute(sql)
        orders = cursor.fetchall()

        self.ordersList.clear()

        for order in orders:
            text = (
                f"Заказ № {order['order_id']} | "
                f"Дата заказа: {order['order_date']} | "
                f"Дата доставки: {order['delivery_date']} | "
                f"Код: {order['code']} | "
                f"Статус: {order['status']}"
            )

            self.ordersList.addItem(text)

app = QApplication(sys.argv)
window = LoginWindow()
window.show()
sys.exit(app.exec())