🌸 Flower Shop E-Commerce Platform
Python
Django
MySQL

A full-featured e-commerce platform for selling flowers, built with Django and MySQL. Features include user authentication, shopping cart management, email verification, and Alipay integration.

🔗 Live Demo: https://jycicy.top/index/

📂 Project Structure
text

Flower/
├── flower/                 # Project Root
│   ├── flower/             # Project Configuration (settings, urls)
│   ├── orderapp/           # Order & Payment Logic
│   ├── ... (other apps)
│   ├── media/              # Static & User Uploaded Media
│   ├── manage.py           # Django CLI utility
│   └── ...
├── requirements.txt        # Project Dependencies
└── README.md               # Documentation
🛠️ Prerequisites
Before you begin, ensure you have the following installed:

Python 3.12 or higher
MySQL 8.0
Ngrok (Required for exposing local server for Alipay callbacks)
Alipay Sandbox Account (For payment testing)
🚀 Installation & Setup Guide
1. Clone the Repository
Bash

git clone https://github.com/jycicy/Flower.git
cd Flower
# Ensure you are in the outer directory containing the 'flower' folder
2. Environment Setup
Create and activate a virtual environment, then install dependencies.

Bash

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
3. Database & Email Configuration
Edit the flower/flower/settings.py file (sometimes named setting.py in your repo):

Database: Update the DATABASES dictionary with your local MySQL credentials (NAME, USER, PASSWORD, HOST, PORT).
Email: Configure the SMTP settings (Host, Port, User, Password) to enable verification code emails.
4. Alipay Sandbox & Ngrok Setup (Crucial)
Since Alipay requires a public URL to send payment notifications, follow these steps carefully:

Start Ngrok:
Run ngrok to expose your local port (default 8000).

Bash

ngrok http 8000
Copy the HTTPS URL generated (e.g., https://xxxx-xxxx.ngrok-free.app).

Configure settings.py:

Set ALIPAY_PUBLIC_KEY and APP_PRIVATE_KEY using keys from your Alipay Sandbox.
Replace any hardcoded base URL with your Ngrok URL.
Update Callback URLs:
Open flower/orderapp/utils.py.
Find the return_url and notify_url variables and update them:

Python

# Example
return_url = "https://your-ngrok-url/order/return/"
notify_url = "https://your-ngrok-url/order/notify/"
5. Database Initialization
Create the database and apply migrations.

Create a database named flower in MySQL.
Run migrations:
Bash

python manage.py makemigrations
python manage.py migrate
6. Data Seeding (Adding Products)
The database is initially empty. You need to manually add product data for the site to function correctly.

Prepare Images:
Move your product images to this directory:
flower/media/flowers/uploadpic/newpic/

Insert Data:
You can use the Django shell (python manage.py shell) or a SQL client.
Important: The image_url field must include the relative path as shown below:

SQL

-- Example SQL Insert
INSERT INTO goods (name, price, image_url, ...)
VALUES ('Rose Bouquet', 99.00, 'flower/media/flowers/uploadpic/newpic/rose.jpg', ...);
7. Run the Server
Bash

python manage.py runserver
Visit http://127.0.0.1:8000/ in your browser.

效果展示传送门https://jycicy.top/index/

----------------------------------------------
跑本地:

1.从仓库拉取整个项目根目录是flower

2.准备python3.12或者更高版本,配置一个虚拟环境,安装依赖(requirements.txt)

3.查看配置文件setting.py(位置flower/flower/setting.py),根据你的情况配置数据库信息,准一个邮箱账号来发送验证码,并修改setting.py的邮箱配置信息,支付信息需要跨域,去申请一个支付宝沙箱账号,修改沙箱的公钥,私钥,需要用到ngrok将你的本地服务暴露为公网,然后将这个公网url替换在你的setting.py 中的相应位置,还有异步回调地址(位置:flower/orderapp/utils.py----->return_url和notify_url)

4.数据库MySQL8.0,创建一个数据库(如:flower),setting.py的信息要和你数据库的信息一致(端口,密码等)

5.数据迁移,虚拟环境执行python manage.py makemigrations, python manage.py migrate,此时数据库和表应该都会给你搭建好,现在就可以启动项目了(虚拟环境下py manage.py runserver),但是现在数据库中是没有商品数据的,你可以手动在goods表中添加几个数据,image_url写相对路径,提前把图片放到flower\media\flowers\uploadpic\newpic\下,这样数据库中的image_url字段,添加的就是’flower\media\flowers\uploadpic\newpic\图片名’
