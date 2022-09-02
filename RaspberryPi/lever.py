# -*- coding: utf-8 -*-
import gpiozero as io


bounce_s=.05
pull_up=True


ll = io.Button(20, pull_up=pull_up, bounce_time = bounce_s)
rl = io.Button(21, pull_up=pull_up, bounce_time = bounce_s)
