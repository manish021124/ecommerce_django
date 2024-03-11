# Django Ecommerce Site

Welcome to our Django Ecommerce Site! This README document will guide you through setting up and using to our project.


## Installation

To install and run our Django Ecommerce Site, follow these steps:

1. Clone the repository to your local machine.
git clone https://github.com/manish021124/ecommerce_django.git

2. Navigate to the project directory:
cd django_ecommerce_site

3. Create a virtual environment:
python -m venv venv

4. Activate the virtual environment:
-**On Windows:**
venv\Scripts\activate

-**On macOS and Linux:**
source venv/bin/activate

5. Install dependencies
pip install -r requirements.txt

6. Perform database migrations
python manage.py migrate

7. Create a superuser (admin account) for the Django admin interface:
python manage.py createsuperuser

8. Start the development server:
python manage.py runserver

9. Open your web browser and navigte to 'http://localhost:8000' to access the site.


## Usage

### Our Django Ecommerce Site provides the following functionalites:
- **User Authentication:** Users can sign up, log in and log out as both customer and store owners.
- **Social Authentication:** Users can sign up, log in and log out as both customer and store owners using Google authentication.
- **Product Management:** Store owners can add, edit and delete products, managin their inventory efficiently.
- **Shopping Cart:** Users can add products to their shopping cart, review their selections, and proceed to checkout seamlessly.
- **Order Management:** Both store owners and customers can manage orders, view order details and easily cancel orders if necessary.
- **Payment Gateway Integration:** Seamlessly integrate the popular payment gateway eSewa to facilitate secure online transactions.


## Contact

If you have any questions or suggestions regarding our Django Ecommerce Site, feel free to contact us at maneeshbalami@gmail.com.


**Frontend:** https://manish021124.github.io/gyapu-e-commerce_site/