
# XCOM简单介绍

- 无下载安装，点击快捷方式即可，本体在文件夹中。

# 串口设置 

软件启动后，会自动搜索可用的串口，可以显示详细的串口信息，由于兼容性原因某些电脑可能不会显示。

超高波特率接收，在硬件设别支持的情况下，可自定义波特率，点“自定义”即可输入您想要的波特率，不过需要在串口关闭的情况下，才能修改。

默认可选波特率为1200bps-1382400bps，可以选择为“1、1.5、2”三种停止位，可以选择“5、6、7、8”四种数据长度，可选奇，偶校验，或无校验。

一般默认115200/9600,1停止位，8数据长度，无校验。

支持串口随时插拔，对于某些硬件设别，由于驱动兼容性的原因可能不支持，实测CH340无问题，建议手动关闭串口。

# 显示设置 

16进制显示，勾选后将显示16进制的字节，如果之前接收到了数据，会自动转换。

显示模式设置，默认为黑色背景，绿色字体。勾选“白底黑字”可以将背景设置为白色，字体为黑色。

通过勾选”RTS”,”DTR”可以控制当前串口的RTS和DTR输出。

勾选“时间戳”选项，可以加入时间戳显示，需要注意的是，时间戳是以换行回车断帧，所以，当接收到的数据不含“rn”换行回车时，此选项无效。

可以保存接收窗口为任意格式的文件，默认为txt格式的文件。

点击清除接收按钮，可以清除窗口显示的内容，并且清除发送和接收字节计数。

# 单条发送

可以在发送区，发送您发送的任意字符，

支持16进制发送，勾选16进制发送的时候将对发送区的内容进行16进制和字符互转，输入16进制的时候，支持字节自动拆分，不需要每输入一个字节就输入一个空格。

勾选发送新行，将会在发送内容后加入换行回车。

支持定时发送，可以自定义发送周期。

支持发送任意格式的文件，可以随时终止文件的发送，可以通过下面的进度条查看发送进度。

点击发送按钮，即可发送内容，支持快捷键“Ctrl+Enter”发送。

点击清除发送按钮，可以清除发送区的内容，并且清除发送和接收字节计数。

在状态栏，可以看到发送和接收的字节数，可以读取当前串口“CTS,DSR,DCD”的状态，可以显示当前的系统时间。在状态栏的最左边，有一个开始按钮，可以调出系统计算器，可以恢复软件的默认设置。也可以从这里退出软件。

# 多条发送 

多条发送, 适合有多条指令需要发送的场合, 比如支持AT指令的设备, 蓝牙, GSM, GPS, WIFI等等。

一共有四页，可以通过“首页，上一页，下一页，尾页”按钮来进行页面的切换。

勾选发送新行，将会在发送内容后加入换行回车。

勾选16进制发送，可以支持16进制发送，但是需要注意的是，这里没有进行16进制验证，如果包含非16进制字符，将会导致发送失败。

勾选关联数字键盘，发送条目0-9将会关联到数字键0-9，在键盘上按下响应的按键即可发送。

支持自动循环发送，可自定义发送周期，需要注意的是，没有勾选的发送条目将不会被发送。
