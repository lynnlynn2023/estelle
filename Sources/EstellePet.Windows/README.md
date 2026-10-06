# Windows 版

这是与 macOS 版共用动画资源的 WPF/.NET 8 实现。

## 本机构建

在 Windows 10/11 上安装 .NET 8 SDK，然后从仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\build-windows.ps1
```

生成的自包含 x64 压缩包位于 `release/艾丝蒂尔桌宠-Windows-x64.zip`，用户无需另行安装 .NET。

## 本地数据

用户设置保存在 `%LOCALAPPDATA%\EstellePet\settings.json`。程序不安装服务、驱动或开机启动项。
