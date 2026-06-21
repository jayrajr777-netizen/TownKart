from django.db import models
from django.utils.safestring import mark_safe



class State(models.Model):
    name = models.CharField(max_length=35)

    def __str__(self):
        return self.name


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=35)

    def __str__(self):
        return self.name


class Location(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=35)

    def __str__(self):
        return self.name





class Admin(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=25)
    password = models.CharField(max_length=20)
    contact_no = models.CharField(max_length=10)


    def __str__(self):
        return self.name



statuses = (
    ('Active', 'Active'),
    ('Inactive', 'Inactive'),
)

roles = (
    ('User', 'User'),
    ('Shop', 'Shop'),
)


class User(models.Model):
    name = models.CharField(max_length=20)
    email = models.EmailField(max_length=25)
    password = models.CharField(max_length=20)
    contact_no = models.CharField(max_length=10)
    address = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, choices=statuses, default='Active')
    role = models.CharField(max_length=20, choices=roles, default='User')
    time_stamp = models.DateTimeField(auto_now_add=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name



class Shop(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=35, null=True, blank=True)
    address = models.TextField(max_length=30)
    email = models.EmailField(max_length=16)
    contact_no = models.CharField(max_length=10)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)



class Category(models.Model):
    name = models.CharField(max_length=35)


    def __str__(self):
        return self.name




class Product(models.Model):
    TYPE_CHOICES = [
        ('New', 'New Product'),
        ('Old', 'Second Hand/Book'),

    ]
    statuses = [
        ("available", "available"),
        ("unavailable", "unavailable"),
    ]

    name = models.CharField(max_length=35)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    shop = models.ForeignKey(User, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price = models.IntegerField()
    description = models.TextField()
    sizes_available = models.CharField(max_length=100, null=True, blank=True, help_text="Enter sizes separated by comma (e.g., S,M,L or 7,8,9)")
    product_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='New')
    image = models.ImageField(upload_to="product_img/")
    status = models.CharField(max_length=20, choices=statuses)
    timestamp = models.DateTimeField(auto_now_add=True)


    @property
    def is_sub_product(self):
        return False
    def image_tag(self):
        return mark_safe(f'<img src="{self.image.url}" width="100"/>')

    def __str__(self):
        return self.name

    def get_shop_name(self):

        shop_details = self.shop.shop_set.first()
        if shop_details and shop_details.shop_name:
            return shop_details.shop_name
        return self.shop.name

    def get_location_name(self):
        shop_details = self.shop.shop_set.first()
        if shop_details and shop_details.location:
            return shop_details.location.name
        return "Unknown"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='multiple_images')
    images = models.ImageField(upload_to="product_gallery/")

    def __str__(self):
        return f"{self.product.name} Image"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE) # મેઈન પ્રોડક્ટ
    sub_product = models.ForeignKey('SubProduct', on_delete=models.CASCADE, null=True, blank=True) # નવો ઉમેરો
    selected_size = models.CharField(max_length=20, null=True, blank=True)
    cart_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="Active")
    quantity = models.PositiveIntegerField(default=1)
    total_amount = models.IntegerField(default=0)
    orderid = models.CharField(max_length=35)




class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default="Pending")
    total_amount = models.IntegerField(default=0)

    def __str__(self):
        return f"Order {self.id} by {self.user.name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price = models.IntegerField()


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    method = models.CharField(max_length=20)
    amount = models.IntegerField()
    status = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=35, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return f"{self.method} - {self.amount}"




class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    ratings = models.CharField(max_length=50)

    def __str__(self):
        return f"Feedback by {self.user.user_name}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)

    status = models.CharField(max_length=50)

    def __str__(self):
        return self.product_id


class SubProduct(models.Model):
    main_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sub_products')
    name = models.CharField(max_length=35)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    qty = models.IntegerField()
    price = models.IntegerField()
    description = models.TextField()
    sizes_available = models.CharField(max_length=100, null=True, blank=True)
    product_type = models.CharField(max_length=10, choices=Product.TYPE_CHOICES, default='New')
    image = models.ImageField(upload_to="subproduct_img/")
    status = models.CharField(max_length=20, choices=Product.statuses)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (Variation of {self.main_product.name})"


    def get_shop_name(self):
            return self.main_product.get_shop_name()

    def get_location_name(self):
            return self.main_product.get_location_name()

    @property
    def is_sub_product(self):
            return True

class SubProductImage(models.Model):
    sub_product = models.ForeignKey(SubProduct, on_delete=models.CASCADE, related_name='sub_multiple_images')
    images = models.ImageField(upload_to="subproduct_gallery/")

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name}"


