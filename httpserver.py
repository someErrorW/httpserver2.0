"""
    http server v2.0
    *IO并发处理
    *基本的request解析
    *使用类封装
"""

from socket import *
from select import select


# 将具体http server功能封装
class HTTPServer:
    def __init__(self, server_address, static_dir):
        # 添加属性
        self.server_address = server_address
        self.static_dir = static_dir
        self.rlist = []
        self.wlist = []
        self.xlist = []
        self.create_socket()
        self.bind()

    # 创建套接字
    def create_socket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    def bind(self):
        self.sockfd.bind(self.server_address)
        self.ip = self.server_address[0]
        self.port = self.server_address[1]

    def server_forever(self):
        self.sockfd.listen(5)
        print("Listen the port %d" % self.port)
        self.rlist.append(self.sockfd)
        while True:
            rs, ws, xs = select(self.rlist, self.wlist, self.xlist)
            for r in rs:
                if r is self.sockfd:
                    c, addr = r.accept()
                    print("Connect from", addr)
                    self.rlist.append(c)
                else:
                    # 处理浏览器请求
                    self.handle(r)

    # 处理客户端请求
    def handle(self, connfd):
        # 接收http请求
        request = connfd.recv(4096)
        print(request)
        # 防止浏览器断开
        if not request:
            self.rlist.remove(connfd)
            connfd.close()
            return

        # 请求解析
        request_line = request.splitlines()[0]
        info = request_line.decode().split(' ')[1]
        print(connfd.getpeername(), ":", info)

        # info分为两类---网页和其他
        if info == '/' or info[-5:] == '.html':
            self.get_html(connfd, info)
        else:  # 其他
            self.get_data(connfd, info)

        self.rlist.remove(connfd)
        connfd.close()

    # 处理网页
    def get_html(self, connfd, info):
        if info == '/':
            # 网页文件
            filename = self.static_dir + '/index.html'
        else:
            filename = self.static_dir + info
        try:
            fd = open(filename)
        except Exception:
            # 没有网页
            responseHeaders = "HTTP/1.1 404 Not Found\r\n"
            responseHeaders += '\r\n'
            responseBody = "<h1>Sorry,Not Found the page</h1>"
        else:
            responseHeaders = "HTTP/1.1 200 OK\r\n"
            responseHeaders += '\r\n'
            responseBody = fd.read()
        finally:
            response = responseHeaders + responseBody
            connfd.send(response.encode())

        # 如何使用HTTPServer类

    #其他情况
    def get_data(self,connfd,info):
        responseHeaders = "HTTP/1.1 200 OK\r\n"
        responseHeaders += '\r\n'
        responseBody = "<h1>Waiting httpserver 3.0</h1>"
        response = responseHeaders + responseBody
        connfd.send(response.encode())


if __name__ == '__main__':
    # 用户自己决定： 地址，内容
    server_addr = ('0.0.0.0', 8080)  # 服务器地址
    static_dir = "./static"  # 网页存放位置

    httpd = HTTPServer(server_addr, static_dir)  # 生成实例对象
    httpd.server_forever()  # 启动服务
