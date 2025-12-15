from .string_help import gen_vcode  # 添加点号表示相对导入
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr,formataddr

import smtplib
#格式化编码,防止乱码
def _format_addr(s):
  name, addr = parseaddr(s)
  return formataddr((Header(name, 'utf-8').encode(),addr))

#构建返送邮件对象
def gen_vcode_msg(vcode, from_addr, to_addr):
  """
    vcode:验证码
    from_addr:发送方邮件
    to_addr:接收方邮件
    return:返回含有发送验证码的MIMEText对象
  """
  text = f'您的验证码是:{vcode},有效时间20分钟.'
  msg = MIMEText(text, 'plain', 'utf-8')
  msg['From'] = _format_addr('网上花店<%s>' %from_addr)
  msg['To'] = _format_addr('新用户<%s>' % to_addr)
  msg['Subject'] = Header('网上花店注册验证码','utf-8').encode()
  return msg

def send_vcode(smtp_server, from_addr,password, to_addr):
    """
        smtp_server: 当前使用smtp,163服务器
        from_addr: 发送方邮箱
        password: 发送方邮箱密码（授权码）
        to_addr: 接收方邮箱
        
    """
    # 构建一个 smtp 对象
    server = smtplib.SMTP_SSL(smtp_server, 465)
    # 设置一个调试级别（上线可以关闭）
    server.set_debuglevel(1)
    # 登录
    server.login(from_addr, password)
    # 构造要发送邮件的内容
    vcode = gen_vcode() # 验证码
    msg = gen_vcode_msg(vcode, from_addr, to_addr) # 邮件对象
    # 发送邮件
    server.sendmail(from_addr, [to_addr],msg.as_string()) 
    server.quit() # 退出
    return vcode

if __name__ == '__main__':
    from_addr = 'jycicy412@163.com'
    to_addr = '3549564430@qq.com'
    password = 'KKTBH8YPDDX7LtSu'
    smtp_server = 'smtp.163.com'
    code = send_vcode(smtp_server,from_addr, password, to_addr)
    print('发送的验证码：',code)