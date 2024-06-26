import sys
from PyQt6.QtWidgets import QApplication
from utils import *
import yaml

yaml_path='config.yaml'
yaml_data=None

def load_yaml():
    global yaml_data
    with open(yaml_path,'r',encoding='utf-8') as f:
        yaml_data=yaml.safe_load(f)

def get_schedule():
    activate=yaml_data['activate']
    for schedule in yaml_data['schedule']:
        if schedule['name']==activate:
            return schedule
    return None

def parse_time(schedule):
    working=schedule['working']
    to_return = [[],[],[]]
    for i in working:
        for k,v in i.items():
            t0,t1=k.split('-')
            h0,m0=[int(num) for num in t0.split(':')]
            h1,m1=[int(num) for num in t1.split(':')]
            to_return[0].append(QTime(h0,m0,0))
            to_return[1].append(QTime(h1,m1,0))
            to_return[2].append(v)
    
    # print(to_return)
    return to_return

def check_time_valid(starts,ends):
    # print(starts)
    # print(ends)
    if len(starts)!=len(ends):
        return False
    for i in range(len(starts)):
        if compare_qtime(starts[i],ends[i])>=0:
            return False
        if i != len(starts)-1 and compare_qtime(ends[i],starts[i+1])>=0:
            return False
    return True

def test():
    load_yaml()
    print(yaml_data)
    app=QApplication(sys.argv)
    time_manager=MainScheduler()
    sys.exit(app.exec())

def test2():
    # 测试一下时间解析函数
    load_yaml()
    activated_schedule = get_schedule()
    args=parse_time(activated_schedule)
    check_result= check_time_valid(args[0].args[1])
    print(yaml_data)
    print(check_result)

def main():
    app = QApplication(sys.argv)

    # global background_window, overlay_window
    # background_window= BackgroundWindow()
    # background_window.show()

    # overlay_window = OverlayWindow()
    # overlay_window.show()
    
    load_yaml()
    activated_schedule = get_schedule()
    starts,ends,texts=parse_time(activated_schedule)
    check_result= check_time_valid(starts,ends)
    if not check_result:
        print('Error in your Schedule time. Make sure you made it right.')
        return
    
    # print(yaml_data)
    # print(check_result)
    
    scheduler=MainScheduler({'start_timepoints':starts,'end_timepoints':ends,'texts':texts,'img_dir':activated_schedule['img_dir']})
    sys.exit(app.exec())


# 软件流程梳理：
# 1、先读取yaml，然后根据所选的是那个schedule，处理时间表格
# 2、如果当前在时间范围内，则在timer中表明当前时间，以及倒计时时间，以及text
# 3、如果当前时间不在范围内，则创建background window，然后定时杀掉
##### 因此，主程序应该是一个timer，然后它又两个子窗口

if __name__ == "__main__":
    main()
    # test2()