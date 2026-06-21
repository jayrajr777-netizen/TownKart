from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import timedelta
from .models import *
import razorpay
from django.conf import settings
from django.db.models import Q
import re
from .models import User
from .models import Shop
from django.http import HttpResponse, JsonResponse
from .models import Shop, Product, Category
from.models import Product
from itertools import chain
from .models import SubProduct




def seller_profile(request):
    if 'log_id' not in request.session or request.session.get('log_role') != 'Shop':
        messages.error(request, "Only Sellers can view this page.")
        return redirect('/login')

    user_id = request.session['log_id']

    try:
        user_data = User.objects.get(id=user_id)
        shop_data = Shop.objects.filter(user=user_data).first()

        return render(request, 'seller_profile.html', {'user_data': user_data, 'shop_data': shop_data})
    except User.DoesNotExist:
        return redirect('/login')


def update_seller_profile(request):
    if request.method == 'POST':
        user_id = request.session.get('log_id')

        if user_id:
            user = User.objects.get(id=user_id)


            user.name = request.POST.get('user_name')
            user.email = request.POST.get('user_email')

            user.contact_no = request.POST.get('user_contact')


            if 'profile_image' in request.FILES:
                user.profile_image = request.FILES['profile_image']
            user.save()
            shop = Shop.objects.filter(user=user).first()

            if not shop:

                state, created = State.objects.get_or_create(name="Gujarat")
                city, created = City.objects.get_or_create(name="Ahmedabad", state=state)
                default_location, created = Location.objects.get_or_create(name="Default Area", city=city)

                shop = Shop(user=user, location=default_location)


            shop.shop_name = request.POST.get('shop_name')
            shop.email = request.POST.get('shop_email')
            shop.contact_no = request.POST.get('shop_contact')
            shop.address = request.POST.get('shop_address')
            shop.save()


            request.session['log_name'] = user.name
            if user.profile_image:
                request.session['log_image'] = str(user.profile_image)

            messages.success(request, "Your Seller Profile & Shop details are updated!")
            return redirect('/seller_profile')

    return redirect('/')
def myprofile(request):
    if 'log_id' not in request.session:
        messages.error(request, "Please log in to view your profile.")
        return redirect('/login')

    user_id = request.session['log_id']

    try:
        user_data = User.objects.get(id=user_id)
        return render(request, 'myprofile.html', {'user_data': user_data})
    except User.DoesNotExist:
        return redirect('/login')


def update_profile(request):
    if request.method == 'POST':
        user_id = request.session.get('log_id')

        if user_id:
            user = User.objects.get(id=user_id)


            user.name = request.POST.get('user_name')
            user.email = request.POST.get('email')
            user.contact_no = request.POST.get('contact_no')
            user.gender = request.POST.get('gender')


            dob = request.POST.get('dob')
            user.dob = dob if dob else None


            user.address = request.POST.get('address')
            user.city = request.POST.get('city')
            user.state = request.POST.get('state')
            user.pincode = request.POST.get('pincode')


            if 'profile_image' in request.FILES:
                user.profile_image = request.FILES['profile_image']


            user.save()


            request.session['log_name'] = user.name
            if user.profile_image:
                request.session['log_image'] = str(user.profile_image)

            messages.success(request, "Your profile details have been updated successfully!")
            return redirect('/myprofile')

    return redirect('/')

def change_password(request):
    if request.method == 'POST':
        user_id = request.session.get('log_id')

        if user_id:
            user = User.objects.get(id=user_id)
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')


            if user.password != old_password:
                messages.error(request, "Incorrect old password. Please try again.")
                return redirect('/myprofile')


            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
                return redirect('/myprofile')


            user.password = new_password
            user.save()

            messages.success(request, "Your password has been changed successfully!")
            return redirect('/myprofile')

    return redirect('/')


def update_cart_wishlist_session(request, user_id):

    try:

        cart_items = Cart.objects.filter(user_id=user_id, status=True)
        cart_count = cart_items.count()
        cart_total = sum(item.total_amount for item in cart_items)


        wishlist_count = Wishlist.objects.filter(user_id=user_id).count()


        request.session['cart_count'] = cart_count
        request.session['cart_total'] = float(cart_total)
        request.session['wishlist_count'] = wishlist_count
    except Exception as e:
        print("Error updating session counts:", e)




def index(request):
    all_products = Product.objects.all()

    context = {
        'product': all_products,
    }
    return render(request, 'index.html', context)



def register(request):
    if request.method == "POST":
        user_name = request.POST.get("user_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        contact_no = request.POST.get("contact_no")
        address = request.POST.get("address")
        role = request.POST.get("role")

        if User.objects.filter(email=email).exists():
            messages.error(request, "This Email address is already registered. Please login or use a different email.")
            return redirect('/register')

        if User.objects.filter(contact_no=contact_no).exists():
            messages.error(request, "This Contact Number is already registered. Please use a different number.")
            return redirect('/register')

        if User.objects.filter(name=user_name).exists():
            messages.error(request, "This Username is already taken. Please choose another one.")
            return redirect('/register')


        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(password_pattern, password):
            messages.error(request, "Registration Failed! Password must contain at least 8 characters, including 1 uppercase, 1 lowercase, 1 number, and 1 special character.")
            return redirect('/register')

        User.objects.create(
            name=user_name,
            email=email,
            password=password,
            contact_no=contact_no,
            address=address,
            role=role,
            status="Active"
        )

        messages.success(request, "Registration Done Successfully!")
        return redirect('/')

    return render(request, "register.html")

def login(request):
    return render(request, "login.html")


def logindata(request):
    if request.method == "POST":
        user_name = request.POST.get("user_name").strip()
        password = request.POST.get("password").strip()

        userdata = User.objects.filter(
            Q(name=user_name) | Q(email=user_name),
            password=password
        ).first()

        if userdata:
            request.session["log_id"] = userdata.id
            request.session["log_name"] = userdata.name
            request.session["log_email"] = userdata.email
            request.session["log_role"] = userdata.role

            if userdata.profile_image:
                request.session["log_image"] = str(userdata.profile_image)
            elif "log_image" in request.session:
                del request.session["log_image"]


            update_cart_wishlist_session(request, userdata.id)

            messages.success(request, "Login Successful")
            return redirect("/")
        else:
            messages.error(request, "Invalid Username or Password")
            return redirect("/login")


def logout(request):
    try:
        del (request.session["log_id"])
        del (request.session["log_name"])
        del (request.session["log_email"])
        del (request.session["log_role"])
        del (request.session["cart_count"])
        del (request.session["wishlist_count"])
        del (request.session["cart_total"])

        if "log_image" in request.session:
            del (request.session["log_image"])

    except:
        pass
    return redirect("/")

def forgot_password(request):
    return render(request, "forgot_password.html")


def update_password(request):
    if request.method == "POST":
        email = request.POST.get("email").strip()
        new_password = request.POST.get("new_password").strip()
        confirm_password = request.POST.get("confirm_password").strip()


        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        if not re.match(password_pattern, new_password):
            messages.error(request, "Password is too weak! Please follow the strong password rules.")
            return redirect("/forgot-password")


        user = User.objects.filter(email=email).first()

        if user:
            if new_password == confirm_password:
                user.password = new_password
                user.save()
                messages.success(request, "Password changed successfully! Old password is no longer valid.")
                return redirect("/login")
            else:
                messages.error(request, "New passwords do not match.")
                return redirect("/forgot-password")
        else:
            messages.error(request, "No account found with this email.")
            return redirect("/forgot-password")

    return redirect("/forgot-password")


def contact(request):
    return render(request, "contact.html")


def product(request):
    category = Category.objects.all()
    product = Product.objects.all()
    context = {"category": category, "product": product}
    return render(request, "singleproduct.html", context)


def addproduct(request):
    fetcdata = Category.objects.all()
    context = {"data": fetcdata}
    return render(request, "addproduct.html", context)


def insertproductdata(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        qty = int(request.POST.get('qty', 0))
        price = request.POST.get('price')
        description = request.POST.get('description')
        product_type = request.POST.get('product_type')
        image = request.FILES.get('image')
        status = request.POST.get('status')
        sizes_available = request.POST.get('sizes_available', '')


        extra_images = request.FILES.getlist('extra_images')

        log_id = request.session.get("log_id")

        if not log_id:
            messages.error(request, "You must be logged in to add a product.")
            return redirect('/login')

        try:
            custom_user = User.objects.get(id=log_id)
        except User.DoesNotExist:
            messages.error(request, "Error: Could not find your profile.")
            return redirect('/login')


        insertquery = Product.objects.create(
            name=name,
            category=Category.objects.get(id=category_id),
            qty=qty,
            price=price,
            description=description,
            product_type=product_type,
            image=image,
            status=status,
            sizes_available=sizes_available,
            shop=custom_user
        )


        for img in extra_images:
            ProductImage.objects.create(product=insertquery, images=img)




        for i in range(1, 16):

            suffix = '' if i == 1 else f'_{i}'

            sub_name = request.POST.get(f'sub_name{suffix}')


            if sub_name and sub_name.strip():
                sub_category_id = request.POST.get(f'sub_category{suffix}')
                sub_qty = request.POST.get(f'sub_qty{suffix}')
                sub_price = request.POST.get(f'sub_price{suffix}')
                sub_desc = request.POST.get(f'sub_description{suffix}')
                sub_type = request.POST.get(f'sub_product_type{suffix}')
                sub_status = request.POST.get(f'sub_status{suffix}')
                sub_sizes = request.POST.get(f'sub_sizes_available{suffix}')
                sub_img = request.FILES.get(f'sub_image{suffix}')

                sub_product = SubProduct.objects.create(
                    main_product=insertquery,
                    name=sub_name.strip(),
                    category=Category.objects.get(id=sub_category_id) if sub_category_id else Category.objects.get(
                        id=category_id),
                    qty=int(sub_qty) if sub_qty else 0,
                    price=int(sub_price) if sub_price else 0,
                    description=sub_desc if sub_desc else '',
                    product_type=sub_type if sub_type else 'New',
                    image=sub_img,
                    status=sub_status if sub_status else 'available',
                    sizes_available=sub_sizes if sub_sizes else ''
                )


                sub_extra_images = request.FILES.getlist(f'sub_extra_images{suffix}')
                for simg in sub_extra_images:
                    SubProductImage.objects.create(sub_product=sub_product, images=simg)

        messages.success(request, "Product and Variations Added Successfully!")
        return redirect('/addproduct')

    return render(request, "addproduct.html")


def shop(request):
    all_products = Product.objects.all()
    all_sub_products = SubProduct.objects.all()

    query = request.GET.get('query')
    category_id = request.GET.get('category')
    location_query = request.GET.get('location')

    if query:
        all_products = all_products.filter(name__icontains=query)
        all_sub_products = all_sub_products.filter(name__icontains=query)

    if category_id and category_id != 'all':
        if category_id.isdigit():
            all_products = all_products.filter(category_id=category_id)
            all_sub_products = all_sub_products.filter(category_id=category_id)
        else:
            all_products = all_products.filter(category__name__iexact=category_id)
            all_sub_products = all_sub_products.filter(category__name__iexact=category_id)

    if location_query:
        matching_shops = Shop.objects.filter(
            Q(location__name__icontains=location_query) |
            Q(location__city__name__icontains=location_query) |
            Q(address__icontains=location_query)
        )
        seller_ids = matching_shops.values_list('user_id', flat=True)

        all_products = all_products.filter(
            Q(shop__id__in=seller_ids) |
            Q(shop__city__icontains=location_query) |
            Q(shop__address__icontains=location_query)
        ).distinct()

        all_sub_products = all_sub_products.filter(
            Q(main_product__shop__id__in=seller_ids) |
            Q(main_product__shop__city__icontains=location_query) |
            Q(main_product__shop__address__icontains=location_query)
        ).distinct()


    combined_products = list(chain(all_products, all_sub_products))

    context = {
        "product": combined_products,
        "categories": Category.objects.all(),
        "search_query": query,
        "selected_category": category_id,
        "location_query": location_query
    }

    return render(request, "shop.html", context)


def singleproduct(request, id):
    single = Product.objects.get(id=id)
    sizes = [s.strip() for s in single.sizes_available.split(',') if s.strip()] if single.sizes_available else []


    product_images = single.multiple_images.all()

    related_products = Product.objects.filter(category=single.category).exclude(id=id)[:4]

    context = {
        "data": single,
        "sizes": sizes,
        "product_images": product_images ,
        "related_products": related_products
    }
    return render(request, "singleproduct.html", context)


def manageproduct(request):
    if 'log_id' not in request.session or request.session.get('log_role') != 'Shop':
        messages.error(request, "Please login as a seller to manage products.")
        return redirect('/login')

    user_id = request.session['log_id']

    try:
        current_user = User.objects.get(id=user_id)

        fetcdata = Product.objects.filter(shop=current_user)
    except User.DoesNotExist:
        fetcdata = []

    context = {"data": fetcdata}
    return render(request, "manageproduct.html", context)


def removeproduct(request, id):
    if 'log_id' not in request.session or request.session.get('log_role') != 'Shop':
        return redirect('/login')

    try:
        current_user = User.objects.get(id=request.session['log_id'])

        product = Product.objects.get(id=id, shop=current_user)
        product.delete()
        messages.success(request, "Product Removed successfully.")
    except Product.DoesNotExist:
        messages.error(request, "You are not authorized to delete this product or it doesn't exist.")

    return redirect("/manageproduct")


def editproduct(request, id):

    if 'log_id' not in request.session or request.session.get('log_role') != 'Shop':
        return redirect('/login')

    try:
        current_user = User.objects.get(id=request.session['log_id'])
        product = Product.objects.get(id=id, shop=current_user)
        categories = Category.objects.all()


        if request.method == "POST":


            product.name = request.POST.get('name')
            product.price = request.POST.get('price')
            product.qty = request.POST.get('qty')
            product.status = request.POST.get('status')


            desc = request.POST.get('desc')
            if hasattr(product, 'description'):
                product.description = desc
            elif hasattr(product, 'desc'):
                product.desc = desc


            cat_id = request.POST.get('category')
            if cat_id:
                product.category = Category.objects.get(id=cat_id)

            if 'image' in request.FILES:
                product.image = request.FILES['image']


            product.save()


            extra_images = request.FILES.getlist('extra_images[]')

            for img in extra_images:

                ProductImage.objects.create(product=product, images=img)


            messages.success(request, "Product and extra images updated successfully!")
            return redirect("/manageproduct")


        context = {
            "categories": categories,
            "product": product
        }
        return render(request, "editproduct.html", context)

    except Product.DoesNotExist:
        messages.error(request, "You are not authorized to edit this product.")
        return redirect("/manageproduct")

def updateproduct(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        name = request.POST.get('name')
        category_id = request.POST.get('category')
        qty = int(request.POST.get('qty', 0))
        price = request.POST.get('price')
        description = request.POST.get('description')
        product_type = request.POST.get('product_type')
        status = request.POST.get('status')
        sizes_available = request.POST.get('sizes_available', '')

        productdetails = Product.objects.get(id=product_id)

        productdetails.name = name
        productdetails.price = price
        productdetails.description = description
        productdetails.status = status
        productdetails.qty = qty
        productdetails.product_type = product_type
        productdetails.category_id = category_id
        productdetails.sizes_available = sizes_available

        if "image" in request.FILES:
            productdetails.image = request.FILES["image"]

        productdetails.product_type = request.POST.get('product_type')
        productdetails.save()


        extra_images = request.FILES.getlist('extra_images')
        for img in extra_images:
            ProductImage.objects.create(product=productdetails, images=img)

        messages.success(request, "PRODUCT UPDATED SUCCESSFULLY....")
        return redirect("/manageproduct")

    return redirect("/manageproduct")



def removesubproduct(request, id):

    if 'log_id' not in request.session or request.session.get('log_role') != 'Shop':
        return redirect('/login')

    try:
        current_user = User.objects.get(id=request.session['log_id'])

        sub_product = SubProduct.objects.get(id=id, main_product__shop=current_user)
        sub_product.delete()
        messages.success(request, "Variation removed successfully.")
    except SubProduct.DoesNotExist:
        messages.error(request, "Unauthorized or variation not found.")

    return redirect("/manageproduct")



def editsubproduct(request, id):

    if 'log_id' not in request.session or request.session.get('log_role') != 'Shop':
        return redirect('/login')

    try:
        current_user = User.objects.get(id=request.session['log_id'])

        sub_product = SubProduct.objects.get(id=id, main_product__shop=current_user)
        categories = Category.objects.all()


        if request.method == "POST":
            sub_product.name = request.POST.get('name')
            sub_product.price = request.POST.get('price')
            sub_product.qty = request.POST.get('qty')
            sub_product.status = request.POST.get('status')


            desc = request.POST.get('desc')
            if hasattr(sub_product, 'description'):
                sub_product.description = desc
            elif hasattr(sub_product, 'desc'):
                sub_product.desc = desc


            cat_id = request.POST.get('category')
            if cat_id:
                sub_product.category = Category.objects.get(id=cat_id)


            if 'image' in request.FILES:
                sub_product.image = request.FILES['image']

            sub_product.save()
            messages.success(request, "Variation updated successfully!")
            return redirect("/manageproduct")


        context = {
            "categories": categories,
            "product": sub_product,
        }
        return render(request, "editproduct.html", context)

    except SubProduct.DoesNotExist:
        messages.error(request, "Unauthorized access.")
        return redirect("/manageproduct")



def insertintocart(request):
    if request.method == "POST":
        userid = request.session["log_id"]
        productid = request.POST.get("productid")
        sub_product_id = request.POST.get("sub_product_id")
        cart_date = request.POST.get("cart_date")
        price = float(request.POST.get("price"))
        quantity = int(request.POST.get("quantity"))
        selected_size = request.POST.get("size", "")


        product_instance = Product.objects.get(id=productid)
        if sub_product_id:
            sub_prod_instance = SubProduct.objects.get(id=sub_product_id)
            available_qty = sub_prod_instance.qty
        else:
            sub_prod_instance = None
            available_qty = product_instance.qty


        if quantity > available_qty:
            messages.error(request, f"Sorry, only {available_qty} items available in stock!")
            return redirect(request.META.get('HTTP_REFERER', '/shop/'))

        if sub_product_id:
            item = Cart.objects.filter(user_id=userid, product_id=productid, sub_product_id=sub_product_id, selected_size=selected_size, status=True).first()
        else:
            item = Cart.objects.filter(user_id=userid, product_id=productid, sub_product__isnull=True, selected_size=selected_size, status=True).first()

        if item:

            if (item.quantity + quantity) > available_qty:
                messages.error(request, f"Cannot add more! Only {available_qty} items available in stock.")
                return redirect(request.META.get('HTTP_REFERER', '/shoppingcart/'))

            item.quantity += quantity
            item.total_amount += (quantity * price)
            item.save()
            messages.success(request, "Product quantity updated!")
        else:
            total_amount = quantity * price
            Cart.objects.create(
                user_id=userid,
                product_id=productid,
                sub_product=sub_prod_instance,
                cart_date=cart_date,
                status=True,
                quantity=quantity,
                total_amount=total_amount,
                orderid=0,
                selected_size=selected_size
            )
            messages.success(request, "Product added to cart!")

        update_cart_wishlist_session(request, userid)
        return redirect('/shoppingcart/')

def shoppingcart(request):
    if "log_id" not in request.session:
        messages.error(request, "Please login to view your cart.")
        return redirect("/login")

    userid = request.session["log_id"]
    data = Cart.objects.filter(user_id=userid, status=True)
    total = sum(i.total_amount for i in data)

    context = {"data": data, "total": total}
    return render(request, "shoppingcart.html", context)


def deletecart(request, id):
    userid = request.session.get("log_id")
    Cart.objects.get(id=id).delete()


    if userid: update_cart_wishlist_session(request, userid)

    messages.success(request, "Product Removed from Cart")
    return redirect("/shoppingcart/")


def increase(request, id):
    userid = request.session.get("log_id")
    fetchdata = Cart.objects.get(id=id)


    if fetchdata.sub_product:
        available_qty = fetchdata.sub_product.qty
        item_price = fetchdata.sub_product.price
    else:
        available_qty = fetchdata.product.qty
        item_price = fetchdata.product.price

    if fetchdata.quantity < available_qty:
        fetchdata.quantity += 1
        fetchdata.total_amount += item_price
        fetchdata.save()
    else:
        messages.error(request, f"Maximum limit reached! Only {available_qty} in stock.")

    if userid: update_cart_wishlist_session(request, userid)
    return redirect("/shoppingcart/")

def decrease(request, id):
    userid = request.session.get("log_id")
    fetchdata = Cart.objects.get(id=id)


    if fetchdata.sub_product:
        item_price = fetchdata.sub_product.price
    else:
        item_price = fetchdata.product.price

    if fetchdata.quantity <= 1:
        fetchdata.delete()
    else:
        fetchdata.quantity -= 1
        fetchdata.total_amount -= item_price
        fetchdata.save()

    if userid: update_cart_wishlist_session(request, userid)
    return redirect("/shoppingcart/")


def placeorder(request):
    user = request.session["log_id"]


    status = request.POST.get("status", "Pending")


    raw_amount = request.POST.get("total_amount", 0)
    totalamount = int(float(raw_amount))
    amount = int(float(raw_amount))

    order = request.POST.get("order")
    method = request.POST.get("payment")
    transaction_id = request.POST.get("transaction_id", "")


    cart_items = Cart.objects.filter(user_id=user, status=True)


    if method == "Cash on Delivery":

        storedata = Order(user=User(id=user), status="Pending", total_amount=totalamount)
        storedata.save()

        storedata1 = Payment(order=storedata, method=method, amount=amount, status=True,
                             user=User(id=user), transaction_id=transaction_id)
        storedata1.save()

        messages.success(request, "Order Placed Successfully....")

        lastid = storedata.id


        for item in cart_items:
            if item.sub_product:
                item.sub_product.qty -= item.quantity
                item.sub_product.save()
            else:
                item.product.qty -= item.quantity
                item.product.save()


        cart_items.update(
            status="Ordered",
            orderid=str(lastid)
        )

        update_cart_wishlist_session(request, user)


        return redirect("/orderhistory")

    else:

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        order_amount = amount * 100

        razorpay_order = client.order.create({
            "amount": order_amount,
            "currency": "INR",
            "receipt": f"order_rcptid_{user}",
            "payment_capture": "1",
        })

        storedata = Order.objects.create(
            user=User(id=user),
            status="Pending",
            total_amount=amount
        )

        storedata1 = Payment(
            order=storedata,
            method="Online",
            amount=amount,
            status=True,
            user=User(id=user),
            transaction_id=transaction_id,
            razorpay_order_id=razorpay_order['id']
        )
        storedata1.save()

        lastid = storedata.id


        for item in cart_items:
            if item.sub_product:
                item.sub_product.qty -= item.quantity
                item.sub_product.save()
            else:
                item.product.qty -= item.quantity
                item.product.save()


        cart_items.update(
            status="Ordered",
            orderid=str(lastid)
        )

        update_cart_wishlist_session(request, user)

        return render(request, "payment.html", {
            "razorpay_order_id": razorpay_order['id'],
            "amount": order_amount,
            "key": settings.RAZORPAY_KEY_ID,
            "currency": "INR",
        })
def add_to_wishlist(request, id):
    if "log_id" not in request.session:
        messages.error(request, "Please login to save items.")
        return redirect("/login")

    userid = request.session["log_id"]
    product = Product.objects.get(id=id)

    item, created = Wishlist.objects.get_or_create(
        user_id=userid,
        product_id=product,
        defaults={'status': 'Active'}
    )

    if created:
        messages.success(request, f"{product.name} added to your wishlist!")
    else:
        messages.info(request, "This item is already in your wishlist.")


    update_cart_wishlist_session(request, userid)

    return redirect("/shop")


def wishlist(request):
    if "log_id" not in request.session:
        messages.error(request, "Please login to view your wishlist.")
        return redirect("/login")

    items = Wishlist.objects.filter(user_id=request.session["log_id"])
    return render(request, "wishlist.html", {"wishlist_items": items})


def remove_from_wishlist(request, id):
    if "log_id" in request.session:
        userid = request.session["log_id"]
        Wishlist.objects.filter(id=id, user_id=userid).delete()
        messages.success(request, "Item removed from wishlist.")


        update_cart_wishlist_session(request, userid)

    return redirect("/wishlist")


def feedback(request):
    all_feedbacks = Feedback.objects.all().order_by('-id')
    return render(request, "feedback.html", {"feedbacks": all_feedbacks})


def submit_feedback(request):
    if request.method == "POST":
        if "log_id" not in request.session:
            messages.error(request, "Please login to submit your feedback.")
            return redirect("/login")

        user_id = request.session.get("log_id")
        user_obj = User.objects.get(id=user_id)
        rating_val = request.POST.get("rating")
        message_val = request.POST.get("message")

        Feedback.objects.create(
            user=user_obj,
            comment=message_val[:35],
            ratings=str(rating_val)
        )

        messages.success(request, "Thank you! Your feedback has been submitted.")
        return redirect("/feedback/")

    return redirect("/feedback/")


def viewfeedback(request):
    if "log_id" not in request.session or request.session.get("log_role") != "Shop":
        messages.error(request, "Only Admin/Shop can view this page.")
        return redirect("/login")

    all_feedbacks = Feedback.objects.all().order_by('-id')
    return render(request, "viewfeedback.html", {"feedbacks": all_feedbacks})


def deletefeedback(request, id):
    try:
        feedback_obj = Feedback.objects.get(id=id)
        feedback_obj.delete()
        messages.success(request, "Feedback removed from records successfully.")
    except Feedback.DoesNotExist:
        messages.error(request, "Feedback not found.")

    return redirect("/viewfeedback/")


def payment_success(request):
    return redirect("shop.html")


def about(request):
    return render(request, "about.html")


def orderhistory(request):
    if "log_id" not in request.session:
        messages.error(request, "Please login to view your order history.")
        return redirect("/login")

    userid = request.session["log_id"]
    user_orders = Order.objects.filter(user_id=userid).order_by('-order_date')
    context = {"orders": user_orders}

    return render(request, "orderhistory.html", context)


def orderdetails(request, id):
    if "log_id" not in request.session:
        return redirect("/login")

    userid = request.session["log_id"]

    try:
        order = Order.objects.get(id=id, user_id=userid)
        order_items = Cart.objects.filter(user_id=userid, orderid=str(order.id))
        context = {"order": order, "order_items": order_items}
        return render(request, "orderdetails.html", context)

    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect("/orderhistory")


def manageorders(request):
    if "log_id" not in request.session or request.session.get("log_role") != "Shop":
        messages.error(request, "Only Shop owners can manage orders.")
        return redirect("/login")

    seller_id = request.session["log_id"]

    try:
        current_user = User.objects.get(id=seller_id)

        seller_products = Product.objects.filter(shop=current_user)


        seller_order_ids = Cart.objects.filter(product__in=seller_products).exclude(orderid='0').values_list('orderid',
                                                                                                             flat=True)


        all_orders = Order.objects.filter(id__in=seller_order_ids).order_by('-order_date')
    except Exception:
        all_orders = []

    context = {"orders": all_orders}
    return render(request, "manageorders.html", context)


def updateorderstatus(request):
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")

        try:
            order = Order.objects.get(id=order_id)
            order.status = new_status
            order.save()
            messages.success(request, f"Order #ORD-{order_id} status updated to {new_status}!")
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")

        return redirect("/manageorders")

    return redirect("/manageorders")

def singlesubproduct(request, id):
    sub = SubProduct.objects.get(id=id)
    sizes = [s.strip() for s in sub.sizes_available.split(',') if s.strip()] if sub.sizes_available else []
    product_images = sub.sub_multiple_images.all()

    main_prod = sub.main_product
    other_subs = SubProduct.objects.filter(main_product=main_prod).exclude(id=id)


    related_products = Product.objects.filter(category=sub.category).exclude(id=main_prod.id)[:4]

    context = {
        "data": sub,
        "sizes": sizes,
        "product_images": product_images,
        "main_prod": main_prod,
        "other_subs": other_subs,
        "related_products": related_products
    }
    return render(request, "singlesubproduct.html", context)

def invoice(request, id):

    order = Order.objects.get(id=id)
    order_items = Cart.objects.filter(orderid=str(order.id))
    return render(request, 'invoice.html', {'order': order, 'order_items': order_items})



def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")


        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )


        messages.success(request,
                         "Thank you! Your message has been sent. Our team will get back to you within 24 hours.")
        return redirect("/contact/")

    return render(request, "contact.html")


