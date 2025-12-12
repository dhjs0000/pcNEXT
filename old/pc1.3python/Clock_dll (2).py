# !/urs/bin/ python
# _*_ coding: utf-8
# !/usr/bin/env python
# -*- coding:utf-8 -*-
import turtle
import datetime
 
 
# 移动一段距离
def skip(distance):
    """
    移动乌龟一段距离，不留痕迹
    :param distance: 像素
    :return:
    """
    turtle.penup()
    turtle.forward(distance)
    turtle.pendown()
 
 
def draw_clock():
    # 先画表盘
    # 先画点
    # 移动一段距离，画一个点，然后退回
    # 转动6°，再移动一段距离，画一个点，然后退回
    # 循环 60次
    # 让乌龟的方向默认向上
    turtle.reset()
    turtle.hideturtle()
    for i in range(60):
 
        skip(160)
        # 根据 5格一个时钟
        if i % 5 == 0:
            turtle.pensize(7)
            # 画时钟
            turtle.forward(20)
            if i == 0:
                turtle.write(12, align='center', font=('Courier', 14, 'bold'))
            elif i == 25 or i == 30 or i == 35:
                skip(25)
                turtle.write(int(i / 5), align='center', font=('Courier', 14, 'bold'))
                skip(-25)
 
            else:
                turtle.write(int(i / 5), align='center', font=('Courier', 14, 'bold'))
            skip(-20)
        else:
            turtle.pensize(1)
            turtle.dot()
        skip(-160)
        turtle.right(6)
 
 
def get_week(t):
    week = ['星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日']
    return week[t.weekday()]
 
 
def create_hand(length, name):
    turtle.reset()
    skip(-length * 0.1)
    turtle.begin_poly()
    turtle.forward(length * 1.1)
    turtle.end_poly()
    # 注册
    turtle.register_shape(name, turtle.get_poly())
    hand = turtle.Turtle()
    hand.shape(name)
    hand.shapesize(1, 1, 3)
    return hand
 
 
def run():
    # 不停的获取时间
    t = datetime.datetime.today()
    bob.forward(65)
    bob.write(get_week(t), align='center', font=('Courier', 14, 'bold'))
    bob.back(130)
    bob.write(t.strftime('%Y-%m-%d'), align='center', font=('Courier', 14, 'bold'))
    bob.home()
    # 指针移动
    second = t.second + t.microsecond * 0.000001
    minute = t.minute + second / 60
    hour = t.hour + minute / 60
    turtle.tracer(True)
    second_hand.setheading(6 * second)
    minute_hand.setheading(6 * minute)
    hour_hand.setheading(30 * hour)
    turtle.ontimer(run, 200)
 
 
if __name__ == '__main__':
    # 画秒针,分针，时针
    turtle.mode('logo')
    turtle.hideturtle()
    global second_hand, minute_hand, hour_hand, bob
 
    second_hand = create_hand(135, 'second_hand')
    minute_hand = create_hand(125, 'minute_hand')
    hour_hand = create_hand(90, 'hour_hand')
    # 创建一个新的turtle对象，去循环的操作
    bob = turtle.Turtle()
    bob.hideturtle()
    bob.penup()
 
    turtle.tracer(False)
    draw_clock()
    run()
 
    turtle.mainloop()
