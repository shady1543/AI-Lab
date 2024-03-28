# 中国象棋



#### 文件介绍

* `main.py`是main函数的程序，实现红黑双方（用参数指定）博弈对抗。

* 其他`.py`文件都是程序运行所需要的类，包括`ChessBoard`、`Game`等。

* `images`文件夹是可视化界面所需的图片。
* 对手AI在`ChessAI.py`中实现，对手AI类已被`pyarmor`加密，需要安装`pyarmor`库才能运行此py文件。这里用的是`win`系统下的加密版本。
* `MyAI.py`已经实现搜索算法。如果想要以更大的概率打败对手AI，建议修改奖励值。（**TODO**）
* 最终评估方法：与对手AI共博弈2次，其中先手、后手各评估一次（在`main.py`中未实现算法的红黑机指定代码，需自行实现）。积分规则：胜一局记3分，平一局记1分，负一局记0分。



#### 代码运行

用命令行运行程序时，借助`--red`和`--black`指定先后手。

```shell
python main.py --red ['MyAI', 'Human', 'SuperAI'] --black ['MyAI', 'Human', 'SuperAI']
```

例如：

```shell
python main.py --red MyAI --black SuperAI
```

如果不想用命令行，也可以在`main.py`中修改`default`选项：

```py
def parse_arguments():
    parser = argparse.ArgumentParser(description='Game mode settings')
    parser.add_argument('--red', choices=['MyAI', 'Human', 'SuperAI'], default='MyAI',
                        help='选择红色方（先手方）')
    parser.add_argument('--black', choices=['MyAI', 'Human', 'SuperAI'], default='SuperAI',
                        help='选择黑色方（后手方）')
    return parser.parse_args()
```
