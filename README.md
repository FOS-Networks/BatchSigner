BatchSigner是一个基于Windows Kits开发工具App Certification Kit中signtool的批量签名工具

使用了多线程，可以快速对大量可执行文件进行签名，在我的电脑上实测可以每分钟签署2000个文件。


使用前置条件:

1.安装Windows Kits工具；

2.在系统环境变量中添加App Certification Kit的路径；

3.确保在cmd中可以直接使用signtool工具；


使用方法：

1.直接下载releases中的程序或者下载源码中的py代码和config.ini配置文件；

2.配置config.ini中的证书信息，以及签名文件路径；

![image](https://github.com/FOS-Networks/BatchSigner/assets/26571768/cd420f3c-85ac-4cb7-91af-065ccba250f5)

3.双击运行exe程序，或者python运行py脚本；

![image](https://github.com/FOS-Networks/BatchSigner/assets/26571768/f1e66505-3099-4bb6-821a-8e145ae310b4)

4.程序会显示签名进度以及速度，签名完成后会弹出提示，至此即可完成批量签名；
