# 艾丝蒂尔桌宠（macOS）

一个仅供个人交流使用的原生 macOS 桌面宠物，以《空之轨迹》的艾丝蒂尔为角色，采用 3D 质感的二维逐帧动画，无声音、无网络请求、无 Dock 图标。

![从左向右走](Assets/Actions/从左向右走/Preview/从左向右走.gif)

## 功能

- 从左向右缓慢行走，到达当前屏幕右侧后从同一屏幕左侧重新走入。
- 菜单栏可在“走路”和“原地踏步”之间切换。
- 每次只在一块屏幕活动；拖到另一块屏幕后，松手即切换活动屏幕。
- 随机穿插两圈转棍动作。
- 鼠标拎起时气呼呼地缓慢扑腾。
- 暂停时盘腿打坐，想法泡泡中的约修亚头像轻微浮动。
- 菜单栏支持暂停、隐藏、三档尺寸和三档速度。
- 记住桌宠上次放置的位置。

## 安装

面向普通用户的完整步骤见 [INSTALL.md](INSTALL.md)。

简要步骤：

1. 下载 `release/艾丝蒂尔桌宠-macOS-arm64.zip`。
2. 解压后将 `艾丝蒂尔桌宠.app` 拖进“应用程序”。
3. 首次启动时右键应用并选择“打开”。

当前构建支持 Apple Silicon Mac，要求 macOS 13 或更高版本。应用使用本机临时签名，没有 Apple Developer ID 公证，因此朋友首次打开时可能看到 macOS 安全提示。

## 从源码构建

需要 macOS、Apple Command Line Tools，以及 `/opt/anaconda3/bin/python3` 中的 Pillow、NumPy 和 OpenCV（仅重新生成动画资源时需要）。

```bash
/opt/anaconda3/bin/python3 scripts/build_runtime_assets.py
/opt/anaconda3/bin/python3 scripts/build_status_icon.py
./scripts/build-app.sh
```

生成的应用位于 `dist/艾丝蒂尔桌宠.app`。

创建分享压缩包：

```bash
./scripts/package-release.sh
```

## 目录

- `Sources/EstellePet/`：AppKit/Objective-C 程序和运行时资源。
- `Assets/Actions/从左向右走/`：当前正式走路动作。
- `Assets/Actions/原地转棍/`：当前两圈转棍动作。
- `Assets/Actions/被鼠标提起_气呼呼挣扎/`：当前鼠标拎起动作。
- `Assets/Actions/坐下打坐/`：当前暂停动作、生成母图和正式帧。
- `Assets/Actions/从右向左走_待制作/`：完整保留的未完成人体与动作草稿，当前不参与运行。
- `Assets/UI/`：菜单栏双马尾头像图标。
- `scripts/`：资源生成、构建和打包脚本。
- `Support/`：应用配置。

## 隐私

应用不连接网络，不读取通讯录、照片、麦克风、摄像头或定位信息。它只保存大小、速度、移动方式和上次桌面位置等本地偏好设置。

## 版权说明

这是非官方的个人同人项目，与原作开发商或发行商无关。《空之轨迹》及其角色、美术设定等相关权利归原权利方所有。请勿将本项目或其中的角色素材用于商业用途。

仓库不包含用户提供的原始参考图；只保留本项目生成并用于动画、界面或待制作动作的图像。
