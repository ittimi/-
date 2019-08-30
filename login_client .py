import socket
import sys,time
import os,json
import hashlib


def get_file_md5(file_path):
    '''
    函数功能:校验文件的md5值
    返回md5值 ：m.hexdigest().upper()
    '''
    m = hashlib.md5()

    with open(file_path, "rb") as f:
        while True:
            data = f.read(1024)
            if len(data) == 0:
                break
            m.update(data)

    return m.hexdigest().upper()




def client_reg_send():
    '''
    函数功能：用户注册
    内容：输入用户名，密码，手机号，邮箱；将以上内容以一个字符串形式发送给客户端，
    客户端将该字符串利用json转换成字典
    '''
    clientUname=input("请输入用户名：")
    clientPassword=input("请输入密码：")
    clientPhone=input("请输入手机号：")
    clientEmail=input("请输入email：")
    req='{"op":2,"args":{"uname":"clientUname","passwd":"clientPassword","phone":"clientPhone","email":"clientEmail"}}'
    #构造一个类似字典的字符转，以便服务器端将其用json转换成字典方便读取
    data_top="{:<15}".format(len(req)).encode()#15字节头文件
    sock.send(data_top)     #先发送头文件给服务器端
    sock.send(req.encode())  #再发送正文给服务器端

def client_reg_recv():
    '''
    函数功能：接收服务器端的相应消息，如果为["error_code"]=0表示注册成功；
    如果为["error_code"]=1表示注册失败
    内容：将接收的json文件通过json.loads()转换为字典
    读取字典中的["error_code"]所对应的值
    '''
    data_len = sock.recv(15).decode().rstrip()
    if len(data_len) > 0:
        data_len = int(data_len)

        recv_size = 0
        json_data = b""
        while recv_size < data_len:
            tmp = sock.recv(data_len - recv_size)
            if tmp == 0:
                break
            json_data += tmp
            recv_size += len(tmp)

        json_data = json_data.decode()#对接收到的文件进行转义
        rsp = json.loads(json_data)#将服务器端发送的文件用json转换成方便读取的字典
        if rsp["error_code"]==0:
            print('注册成功')
        else:
            print('注册失败')
def client_login_send():
    '''
    函数功能:登录服务器，服务器对用户名和密码进行校验，校验成功后才开始发送文件
    '''
    clientUname=input("请输入用户名：")
    clientPassword=input("请输入密码：")
    req='{"op":1,"args":{"uname":"clientUname","passwd":"clientPassword"}}'
    data_top="{:<15}".format(len(req)).encode()
    sock.send(data_top)
    sock.send(req.encode())



def client_login_recv():
    '''
    函数功能：用户登录成功后接受服务器端发送的文件
    '''
    data_len = sock.recv(15).decode().rstrip()
    if len(data_len) > 0:
        data_len = int(data_len)

        recv_size = 0
        json_data = b""
        while recv_size < data_len:
            tmp = sock.recv(data_len - recv_size)
            if tmp == 0:
                break
            json_data += tmp
            recv_size += len(tmp)

        json_data = json_data.decode()
        rsp = json.loads(json_data)
        if rsp["error_code"]==0:
            print('登录成功')
            while True:
                file_path = sock.recv(300).decode().rstrip()  # 接收文件夹名
                print(file_path)
                if len(file_path) == 0:  # 如果接收的数据长度是0，结束循环
                    break

                file_size = sock.recv(15).decode().rstrip()  # 接收文件的大小
                print(file_size)
                if len(file_size)==0:
                    break
                file_size = int(file_size)
                file_md5 = sock.recv(32).decode()
                print(file_path)
                print(file_size)
                print(file_md5)
                try:
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)  # 如果文件夹目录不存在就创建该文件夹目录
                except:
                    pass
                print('正在接受%s文件...' % file_path)
                f = open(file_path, 'wb')
                start_time = time.time()  # 开始时间
                recv_size = 0
                loading_proess_1 = 0
                while recv_size < file_size:  # 控制文件是否传输完
                    file_data = sock.recv(file_size - recv_size)  # 接收剩下的文件
                    if len(file_data) == 0:  # 判断接收的数据是否为空
                        break
                    f.write(file_data)  # 将接收的数据写入f
                    t0 = time.time()  # 写完第一次接收的数据的时间
                    t1 = t0 - start_time  # 数据传输开始到第一次数据写入的时间差
                    scheduled_time = ((file_size - recv_size) / len(file_data)) * t1  # 预计当前文件传输所需时间
                    recv_size += len(file_data)  # 已接收文件的大小
                    loading_proess = int(recv_size * 100 / file_size)  # 文件传输的进度百分比值
                    if loading_proess != loading_proess_1:
                        print('预计%s秒接收完当前这个文件' % scheduled_time)
                        print('接收文件\r%s%%' % loading_proess)
                    loading_proess_1 = loading_proess
                    if loading_proess == 100:
                        end_time = time.time()  # 当前文件传输完后的时间
                        t = end_time - start_time  # 一个文件传输所用的总时间
                        if t == 0:
                            print('文件过小，无法统计平均速率')
                        else:
                            average_speed = float(file_size / t)  # 文件传输的平均速度
                            print('本次接收这个文件平均速度为\r%fB每秒' % average_speed)
                        print('本次接收这个文件用时%s秒' % t)

                f.close()
                recv_file_md5 = get_file_md5(file_path)
                if recv_file_md5 == file_md5:
                    print('接收成功%s' % file_path)
                else:
                    print('接收文件%s失败' % file_path)
                    break
            sock.close()

        else:
            print('登录失败')

def client_uname_send():
    '''
    函数功能：对用户名进行校验
    '''
    clientUname=input("请输入用户名：")
    req='{"op":3,"args":{"uname":"clientUname"}}'
    data_top="{:<15}".format(len(req)).encode()
    sock.send(data_top)
    sock.send(req.encode())

def client_uname_recv():
    '''
    函数功能：接收用户名校验的结果
    '''
    data_len = sock.recv(15).decode().rstrip()
    if len(data_len) > 0:
        data_len = int(data_len)

        recv_size = 0
        json_data = b""
        while recv_size < data_len:
            tmp = sock.recv(data_len - recv_size)
            if tmp == 0:
                break
            json_data += tmp
            recv_size += len(tmp)

        json_data = json_data.decode()
        rsp = json.loads(json_data)
        if rsp["error_code"] == 0:
            print('用户不存在')
        elif rsp["error_code"] == 1:
            print('用户已存在')


server_ip = input("服务器IP地址：")
server_port = int(input("服务器端口："))
sock = socket.socket()              #创建套接字
sock.connect((server_ip, server_port))  #连接服务器ip和端口号
print('1:登录')
print('2：注册')
print('3：校验用户')
i=input("请输入你的选择")
if i=='1':
    client_login_send()
    client_login_recv()
elif i=='2':
    client_reg_send()
    client_reg_recv()
elif i=='3':
    client_uname_send()
    client_uname_recv()
else:
    exit()

