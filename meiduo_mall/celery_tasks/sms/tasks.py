from libs.yuntongxun.sms import CCP
from celery_tasks.main import app

@app.task
def send_sms_code(mobile,sms_code):
    '''
    发送短信异步任务
    :param mobile:
    :param sms_code:
    :return: 成功0或失败1
    '''

    result = CCP().send_template_sms('13914070562',[sms_code,5],1)
    print('当前验证码是:', sms_code)
    return result
