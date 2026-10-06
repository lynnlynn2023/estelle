# Windows 版开发说明

Windows 版使用 WPF 和 .NET 8 构建，与 macOS 版共用 `Sources/EstellePet/Resources` 下的逐帧 PNG 动画资源。角色行为、动画时序和菜单选项尽量保持两个平台一致。

## 已实现功能

- 无边框、透明、始终置顶的桌宠窗口。
- 走路与原地踏步切换；走到当前显示器右边缘后从左侧重新进入。
- 拖动、跨屏切换、鼠标拎起挣扎。
- 随机两圈转棍动画。
- 暂停时循环播放打坐动画。
- 系统托盘菜单：暂停、隐藏、移动方式、大小、速度、回到主屏幕和退出。
- 保存窗口位置和用户选项；单实例运行；本地错误日志。

## 本地构建

要求：

- 64 位 Windows 10 或 Windows 11。
- [.NET 8 SDK](https://dotnet.microsoft.com/download/dotnet/8.0)。
- PowerShell。

在仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-windows.ps1
```

构建结果：

- 发布目录：`dist/windows-x64/`
- 可执行文件：`dist/windows-x64/EstellePet.exe`
- 分享包：`release/EstellePet-Windows-x64.zip`

分享包包含 `EstellePet.exe` 和 `INSTALL.md`。程序是 `win-x64` 自包含单文件发布，接收者不需要安装 .NET，也不需要管理员权限。面向普通用户的步骤见仓库根目录的 [INSTALL.md](../../INSTALL.md)。

## 自动构建与发布

`.github/workflows/build-windows.yml` 在推送 `v*` 标签时执行以下工作：

1. 在 GitHub 的 Windows runner 上发布自包含程序。
2. 启动 `EstellePet.exe` 并保持 5 秒，确认应用不会在启动阶段退出。
3. 上传 `EstellePet-Windows-x64.zip` 作为工作流产物。
4. 创建对应标签的 GitHub Release，并同时附上 Windows 与 macOS 压缩包。

也可以在 GitHub Actions 页面手动运行工作流；手动运行只生成 Windows 工作流产物，不创建版本 Release。

## 本地数据

- 设置：`%LOCALAPPDATA%\EstellePet\settings.json`
- 错误日志：`%LOCALAPPDATA%\EstellePet\error.log`

程序不创建服务、驱动或计划任务，不注册开机启动项，也不进行网络请求。
