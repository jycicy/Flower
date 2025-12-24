# Flower

效果展示传送门https://jycicy.top/index/

1.从仓库拉取整个项目根目录是flower

2.准备python3.12或者更高版本,配置一个虚拟环境,安装依赖(requirements.txt)

3.查看配置文件setting.py(位置flower/flower/setting.py),根据你的情况配置数据库信息,准一个邮箱账号来发送验证码,并修改setting.py的邮箱配置信息,支付信息需要跨域,去申请一个支付宝沙箱账号,修改沙箱的公钥,私钥,需要用到ngrok将你的本地服务暴露为公网,然后将这个公网url替换在你的setting.py 中的相应位置,还有异步回调地址(位置:flower/orderapp/utils.py----->return_url和notify_url)

4.数据库MySQL8.0,创建一个数据库(如:flower),setting.py的信息要和你数据库的信息一致(端口,密码等)

5.数据迁移,虚拟环境执行python manage.py makemigrations, python manage.py migrate,此时数据库和表应该都会给你搭建好,现在就可以启动项目了(虚拟环境下py manage.py runserver),但是现在数据库中是没有商品数据的,你可以手动在goods表中添加几个数据,image_url写相对路径,提前把图片放到flower\media\flowers\uploadpic\newpic\下,这样数据库中的image_url字段,添加的就是’flower\media\flowers\uploadpic\newpic\图片名’
