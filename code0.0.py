# 模拟键盘操作
from selenium.webdriver.common.keys import Keys
# 使用超级鹰识别验证需要的模块
import requests
from hashlib import md5
# 利用selenium模块实现自动化模拟登录
from selenium import webdriver
from selenium.webdriver import ChromeOptions
from selenium.webdriver import ActionChains
# 实现对验证图片的处理
from time import sleep
from PIL import Image
# 获取当前日期
import datetime
## 超级鹰提供的代码
class Chaojiying_Client(object):

    def __init__(self, username, password, soft_id):
        self.username = username
        password =  password.encode('utf8')
        self.password = md5(password).hexdigest()
        self.soft_id = soft_id
        self.base_params = {
            'user': self.username,
            'pass2': self.password,
            'softid': self.soft_id,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0)',
        }

    def PostPic(self, im, codetype):
        """
        im: 图片字节
        codetype: 题目类型 参考 http://www.chaojiying.com/price.html
        """
        params = {
            'codetype': codetype,
        }
        params.update(self.base_params)
        files = {'userfile': ('ccc.jpg', im)}
        r = requests.post('http://upload.chaojiying.net/Upload/Processing.php', data=params, files=files, headers=self.headers)
        return r.json()

    def ReportError(self, im_id):
        """
        im_id:报错题目的图片ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://upload.chaojiying.net/Upload/ReportError.php', data=params, headers=self.headers)
        return r.json()
# 获得滑块轨迹，实现滑块验证，因为滑块速度过快会被检测出来
def get_track(distance):
    track=[]
    v=80
    t=0.2
    mid=distance*4/5
    current=0
    while current<distance:
        if current<mid:
            a=20
        else:
            a=10
        v0=v
        v=v0+a*t
        move=v0*t+1/2*a*t*t
        current+=move
        track.append(round(move))
    return track
if __name__=='__main__':
    # 实现selenium规避被检测到的风险
    option = ChromeOptions()
    option.add_argument("--disable-blink-features=AutomationControlled")
    option.add_experimental_option('excludeSwitches', ['enable-automation'])
    bro = webdriver.Chrome(executable_path='D:/project2/chromedriver.exe', options=option)
    # 让浏览器发起一个指定url对应请求
    bro.get('https://kyfw.12306.cn/otn/leftTicket/init?linktypeid=dc')
    sleep(2)
    # 将弹出窗口关闭
    btn=bro.find_element_by_id('gb_closeDefaultWarningWindowDialog_id')
    btn.click()
    sleep(2)
    # 输入出发地：铜仁南
    input_chufa=bro.find_element_by_id('fromStationText')
    input_chufa.click()
    input_chufa.send_keys('铜仁南',Keys.ENTER)
    # 输入目的地：北京西
    input_mudi=bro.find_element_by_id('toStationText')
    input_mudi.click()
    input_mudi.send_keys('北京西',Keys.ENTER)
    # 点击学生票
    btn=bro.find_element_by_id('sf2')
    btn.click()
    sleep(1)
    # 获取当前日期
    now_year = datetime.datetime.now().year
    now_month = datetime.datetime.now().month
    now_day = datetime.datetime.now().day
    then_year = input('请输入出发日年份（按回车键结束）:')
    then_month=input('请输入出发日月份（按回车键结束）:')
    then_day=input('请输入出发日（按回车键结束）：')
    year=int(then_year)
    month=int(then_month)
    day=int(then_day)
    d1=datetime.datetime(now_year,now_month,now_day)
    d2=datetime.datetime(year,month,day)
    dis=(d2-d1).days
    if dis<0:
        print('输入日期有误')
    elif dis>14:
        print('未开始出售')
    else:
        btn=bro.find_element_by_xpath('//*[@id="date_range"]/ul/li['+str(dis+1)+']')
        btn.click()
        # 点击查询
        btn=bro.find_element_by_id('query_ticket')
        btn.click()
        sleep(2)
        # 点击预订
        btn=bro.find_element_by_class_name('btn72')
        btn.click()
        sleep(2)
        # 把窗口转换到当前窗口
        windows = bro.window_handles
        bro.switch_to.window(windows[-1])
        sleep(1)
        # 点击账户登录
        btn=bro.find_element_by_class_name('login-hd-account')
        btn.click()
        sleep(2)
        # 输入用户名
        input_name=bro.find_element_by_id('J-userName')
        input_name.send_keys('12306账号')
        # 输入密码
        input_keys=bro.find_element_by_id('J-password')
        input_keys.send_keys('12306密码')
        """验证码图片处理"""
        # 进行全局的截图和保存
        bro.save_screenshot('aaa.png')
        # 进行局部区域裁剪
        # 确定验证码图片左上角和右上角的坐标（裁剪区域的确定）
        code_img_ele = bro.find_element_by_xpath('//*[@id="J-loginImgArea"]')
        location = code_img_ele.location  # 验证码左上角的坐标 x,y
        size = code_img_ele.size  # 验证码标签对应的长和宽
        rangle = (
            int(location['x']), int(location['y']), int(location['x'] + size['width']),
            int(location['y'] + size['height'])
        )
        # 图片的裁剪
        # 第一步实例化一个img对象
        i = Image.open('./aaa.png')
        code_img_name = './code.png'
        # crop根据指定区域进行裁剪
        frame = i.crop(rangle)
        frame.save(code_img_name)
        # 将验证码提交给超级鹰
        chaojiying = Chaojiying_Client('超级鹰账号', '超级鹰密码', '软件ID')  # 用户中心>>软件ID 生成一个替换 96001
        im = open('code.png', 'rb').read()  # 本地图片文件路径 来替换 a.jpg 有时WIN系统须要//
        a = chaojiying.PostPic(im, 9004)['pic_str'].split('|')
        x = []
        y = []
        for m in a:
            x.append(m.split(',')[0])
            y.append(m.split(',')[1])
        count = len(x)
        for l in range(count):
            x1 = int(x[l])
            y1 = int(y[l])
            ActionChains(bro).move_to_element_with_offset(code_img_ele, x1, y1).click().perform()
            sleep(2)
        btn_log = bro.find_element_by_id('J-login')
        btn_log.click()
        sleep(2)
        # 滑块验证
        code_img_ele = bro.find_element_by_xpath('//*[@id="nc_1__scale_text"]/span')
        size = code_img_ele.size
        distance = int(size['width'])
        track = []
        slider = bro.find_element_by_id('nc_1_n1z')
        track = get_track(distance)
        ActionChains(bro).click_and_hold(slider).perform()
        for i in track:
            ActionChains(bro).move_by_offset(xoffset=i, yoffset=0).perform()
        ActionChains(bro).release()
        sleep(2)
        # 把窗口转换到当前窗口
        windows = bro.window_handles
        bro.switch_to.window(windows[-1])
        sleep(1)
        # 点击乘客
        btn=bro.find_element_by_xpath('//*[@id="normalPassenger_0"]')
        btn.click()
        sleep(1)
        # 点击确认
        btn=bro.find_element_by_id('dialog_xsertcj_ok')
        btn.click()
        sleep(2)
        # 点击提交订单
        btn=bro.find_element_by_id('submitOrder_id')
        btn.click()
        sleep(2)
        # 选择座位
        btn=bro.find_element_by_id('1D')
        btn.click()
        sleep(2)
        # 点击确认
        btn=bro.find_element_by_id('qr_submit_id')
        btn.click()
        sleep(2)
        print('预订成功，请在半小时内登录12306支付款项。感谢您的配合')



