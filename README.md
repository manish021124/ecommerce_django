# Django Ecommerce Site

Welcome to our Django Ecommerce Site! This README document will guide you through setting up and using to our project.


## Installation

To install and run our Django Ecommerce Site, follow these steps:

1. Clone the repository to your local machine.  
```
git clone https://github.com/manish021124/ecommerce_django.git
```

2. Navigate to the project directory:  
```
cd ecommerce_django
```

3. Create a virtual environment:  
```
python -m venv venv
```

4. Activate the virtual environment:  
- **On Windows:**  
```
venv\Scripts\activate
```

- **On macOS and Linux:**  
```
source venv/bin/activate
```

5. Install dependencies  
```
pip install -r requirements.txt
```

6. Perform database migrations  
```
python manage.py migrate
```

7. Create a superuser (admin account) for the Django admin interface:  
```
python manage.py createsuperuser
```

8. Start the development server:  
```
python manage.py runserver
```

9. Open your web browser and navigte to 'http://localhost:8000' to access the site.


## Obtain Google OAuth2 credentials

1. **Create a project in Google Developer Console**  
- Go to the [Google Developer Console](https://console.developers.google.com/).
- Create a new project or select an existing one.
- Enable the Google OAuth2 API for your project.

2. **Create a .env file**  
- Create a file named '.env' in your project directory if it doesn't already exist. 
- Add your Google OAuth2 client ID and client secret as envrionment variables in the '.env' file.
```
GOOGLE_OAUTH2_CLIENT_ID="your_client_id"
GOOGLE_OAUTH2_CLIENT_SECRET="your_client_secret"
```

3. **Activate the virtual environment and install dependencies**

4. **Start the development server**  

By following these steps, you'll have set up Google OAuth2 authentication for your Django project. Users can now authenticate using their Google accounts when accessing your application.


## Test Login Credentials of eSewa

You can use the following test credentials to log in to eSewa for testing purposes:

- **eSewa ID:** 9806800001/2/3/4/5
- **Password:** Nepal@123
- **MPIN:** 1122 (for application only)
- **Token:** 123456


## Usage

Our Django Ecommerce Site provides the following functionalites:  

- **User Authentication:** Users can sign up, log in and log out as both customer and store owners.
- **Social Authentication:** Users can sign up, log in and log out as customer using Google authentication.
- **Product Management:** Store owners can add, edit and delete products, managin their inventory efficiently.
- **Product Search:** Users can search for products by entering search queries into the serach form.
- **Shopping Cart:** Users can add products to their shopping cart, review their selections, and proceed to checkout seamlessly.
- **Order Management:** Both store owners and customers can manage orders, view order details and easily cancel orders if necessary.
- **Payment Gateway Integration:** Seamlessly integrate the popular payment gateway eSewa to facilitate secure online transactions.


## Contact

If you have any questions or suggestions regarding our Django Ecommerce Site, feel free to contact us at maneeshbalami@gmail.com.


**Frontend:** https://manish021124.github.io/gyapu-e-commerce_site/
