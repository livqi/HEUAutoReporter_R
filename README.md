# HEUAutoReporter_R

## 哈尔滨工程大学自动报备出校_Reaests

本项目利用Github Actions在每日6点和12点自动报备出校，并通过**Server酱**推送报备结果。支持多账户报备。

这是使用requests库的版本

本项目仅供学习研究使用，请**如实**填写报备信息。
本项目已**经过不完整的测试**。


## 食用方法

1. 给我点个Star
2. Fork此项目
3. 添加secrets
4. 启动Github Actions
5. 手动执行一次Actions（给fork后的项目点击star，如果没有运行，就先unstar然后再star）

## Secrets

| SECRET_NAME | VALUE                                     |
| ----------- | ----------------------------------------- |
| STULIST     | 20202014XX password1#20200209XX password2 |
| SCKEY       | SCTzheShiwOxIAdAdewobuzhiDaoxIESha        |

STULIST:账号和密码用空格隔开，多个账号之间用“**#**”隔开。如果你的密码中含有”**#**“，请修改密码后食用

SCKEY:Server酱的内个



