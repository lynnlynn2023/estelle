# 艾丝蒂尔桌宠（macOS / Windows）

一个仅供个人交流使用的桌面宠物，以《空之轨迹》的艾丝蒂尔为角色，采用 3D 质感的二维逐帧动画。项目同时提供原生 macOS 版和 Windows WPF 版，两者共用同一套角色与动画素材。

![从左向右走](Assets/Actions/从左向右走/Preview/从左向右走.gif)

## 下载

普通用户不需要下载源码，请打开 [GitHub Releases](https://github.com/lynnlynn2023/estelle/releases/latest) 下载与系统对应的压缩包。

| 系统 | 下载包 | 系统要求 |
| --- | --- | --- |
| Windows | `EstellePet-Windows-x64.zip` | 64 位 Windows 10/11 |
| macOS | `EstellePet-macOS-arm64.zip` | Apple Silicon，macOS 13 或更高版本 |

完整的安装、首次启动、SmartScreen/Gatekeeper 处理和卸载步骤见 [INSTALL.md](INSTALL.md)。

## 功能

- 从左向右缓慢行走，到达当前屏幕右侧后从同一屏幕左侧重新走入。
- 可在“走路”和“原地踏步”之间切换。
- 每次只在一块屏幕活动；拖到另一块屏幕后，松手即切换活动屏幕。
- 随机穿插两圈转棍动作。
- 鼠标拎起时气呼呼地缓慢扑腾。
- 暂停时先跳跃转到正面，再屈膝坐下打坐；继续时从坐姿跳起、空中转侧并落回走路循环。
- 打坐时想法泡泡中的约修亚头像轻微浮动。
- macOS 菜单栏或 Windows 系统托盘支持暂停、隐藏、三档尺寸和三档速度。
- 记住上次的位置、尺寸、速度和移动方式。
- 无声音、无广告、无网络请求，不安装后台服务或开机启动项。

## 从源码构建

### Windows

需要 Windows 10/11 和 [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)。在仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-windows.ps1
```

脚本会生成：

- `dist/windows-x64/EstellePet.exe`
- `release/EstellePet-Windows-x64.zip`

Windows 包是 x64 自包含程序，并随包附带 `INSTALL.md`；最终用户无需安装 .NET。GitHub Actions 会在版本标签推送时使用 Windows runner 构建，并执行启动冒烟测试。更多开发说明见 [Sources/EstellePet.Windows/README.md](Sources/EstellePet.Windows/README.md)。

### macOS

需要 macOS、Apple Command Line Tools，以及 `/opt/anaconda3/bin/python3` 中的 Pillow、NumPy 和 OpenCV（仅重新生成动画资源时需要）。

```bash
/opt/anaconda3/bin/python3 scripts/build_runtime_assets.py
/opt/anaconda3/bin/python3 scripts/build_status_icon.py
./scripts/build-app.sh
./scripts/package-release.sh
```

生成的应用位于 `dist/艾丝蒂尔桌宠.app`，分享包位于 `release/艾丝蒂尔桌宠-macOS-arm64.zip`。

## 项目结构

- `Sources/EstellePet/`：macOS AppKit/Objective-C 程序和两个平台共用的运行时 PNG 资源。
- `Sources/EstellePet.Windows/`：Windows WPF/.NET 8 程序。
- `Assets/Actions/`：已确认动作的源图、正式帧和预览。
- `Assets/Actions/从右向左走_待制作/`：保留的未完成生成草稿，当前不参与运行。
- `Assets/UI/`：macOS 菜单栏和 Windows 系统托盘使用的双马尾图标。
- `scripts/`：资源生成、macOS/Windows 构建和打包脚本。
- `.github/workflows/build-windows.yml`：Windows 自动构建、启动测试和 Release 发布流程。

## 隐私与本地数据

应用不连接网络，不读取通讯录、照片、麦克风、摄像头或定位信息。Windows 版设置位于 `%LOCALAPPDATA%\EstellePet\settings.json`；macOS 版使用系统偏好设置保存同类信息。

## 版权说明

这是非官方的个人同人项目，与原作开发商或发行商无关。《空之轨迹》及其角色、美术设定等相关权利归原权利方所有。请勿将本项目或其中的角色素材用于商业用途。

仓库不包含用户提供的原始参考图；只保留本项目生成并用于动画、界面或待制作动作的图像。
