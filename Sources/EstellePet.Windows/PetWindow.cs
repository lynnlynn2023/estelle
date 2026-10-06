using System.ComponentModel;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Interop;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Threading;
using Icon = System.Drawing.Icon;
using SystemIcons = System.Drawing.SystemIcons;
using Forms = System.Windows.Forms;

namespace EstellePet.WindowsApp;

internal sealed class PetWindow : Window
{
    private enum MotionMode
    {
        Walking,
        StaffSpin,
    }

    private enum DisplayMode
    {
        None,
        Walking,
        StaffSpin,
        Struggle,
        Meditate,
    }

    private const double PetSizeSmall = 180;
    private const double PetSizeMedium = 230;
    private const double PetSizeLarge = 290;
    private const double WalkingSpeedVerySlow = 10;
    private const double WalkingSpeedSlow = 18;
    private const double WalkingSpeedLeisurely = 28;
    private const double WalkFrameDuration = 0.22;
    private const double MeditateFrameDuration = 0.10;

    private static readonly double[] ActionFrameDurations =
    [
        0.250, 0.070, 0.070, 0.085, 0.085, 0.230,
        0.072, 0.072, 0.072, 0.072, 0.072, 0.072, 0.072, 0.072,
        0.072, 0.072, 0.072, 0.072, 0.072, 0.072, 0.072, 0.072,
        0.260,
        0.160, 0.085, 0.085, 0.085, 0.075, 0.120,
    ];

    private static readonly int[] StruggleFrameSequence = [0, 1, 2, 3, 2, 1];
    private static readonly double[] StruggleFrameDurations = [0.190, 0.180, 0.160, 0.180, 0.160, 0.180];

    private readonly PetSettings _settings;
    private readonly Grid _dragSurface;
    private readonly System.Windows.Controls.Image _petImage;
    private readonly BitmapSource[] _walkFrames;
    private readonly BitmapSource[] _actionFrames;
    private readonly BitmapSource[] _struggleFrames;
    private readonly BitmapSource[] _meditateFrames;
    private readonly DispatcherTimer _timer;
    private readonly Stopwatch _clock = Stopwatch.StartNew();

    private Forms.NotifyIcon _notifyIcon = null!;
    private Icon _trayIcon = null!;
    private Forms.ToolStripMenuItem _pauseMenuItem = null!;
    private Forms.ToolStripMenuItem _visibilityMenuItem = null!;
    private Forms.ToolStripMenuItem _walkingMenuItem = null!;
    private Forms.ToolStripMenuItem _steppingMenuItem = null!;
    private readonly List<Forms.ToolStripMenuItem> _sizeMenuItems = [];
    private readonly List<Forms.ToolStripMenuItem> _speedMenuItems = [];

    private nint _handle;
    private Forms.Screen? _activityScreen;
    private MotionMode _motionMode = MotionMode.Walking;
    private DisplayMode _displayMode = DisplayMode.None;
    private int _displayFrameIndex = -1;
    private int _actionFrameIndex;
    private int _struggleStepIndex;
    private double _lastUpdate;
    private double _animationTime;
    private double _actionElapsed;
    private double _struggleElapsed;
    private double _meditationTime;
    private double _timeUntilAction = 5.0;
    private double _movementX;
    private double _petSize;
    private double _walkingSpeed;
    private int _dragOffsetX;
    private int _dragOffsetY;
    private bool _movesAcrossScreen;
    private bool _dragging;
    private bool _paused;
    private bool _hidden;
    private bool _exiting;

    public PetWindow()
    {
        _settings = SettingsStore.Load();
        _petSize = ValidChoice(_settings.PetSize, [PetSizeSmall, PetSizeMedium, PetSizeLarge], PetSizeMedium);
        _walkingSpeed = ValidChoice(
            _settings.WalkingSpeed,
            [WalkingSpeedVerySlow, WalkingSpeedSlow, WalkingSpeedLeisurely],
            WalkingSpeedSlow);
        _movesAcrossScreen = _settings.MovesAcrossScreen;

        Title = "艾丝蒂尔桌宠";
        Width = _petSize;
        Height = _petSize;
        Left = 80;
        Top = 80;
        WindowStartupLocation = WindowStartupLocation.Manual;
        WindowStyle = WindowStyle.None;
        ResizeMode = ResizeMode.NoResize;
        AllowsTransparency = true;
        Background = System.Windows.Media.Brushes.Transparent;
        Topmost = true;
        ShowInTaskbar = false;
        ShowActivated = false;
        Focusable = false;
        UseLayoutRounding = true;

        _petImage = new System.Windows.Controls.Image
        {
            Stretch = Stretch.Uniform,
            HorizontalAlignment = System.Windows.HorizontalAlignment.Stretch,
            VerticalAlignment = System.Windows.VerticalAlignment.Stretch,
            IsHitTestVisible = false,
            SnapsToDevicePixels = true,
        };
        RenderOptions.SetBitmapScalingMode(_petImage, BitmapScalingMode.HighQuality);

        _dragSurface = new Grid
        {
            Background = System.Windows.Media.Brushes.Transparent,
        };
        _dragSurface.Children.Add(_petImage);
        Content = _dragSurface;

        _walkFrames = LoadFrames("walk-square-right", 4, oneBased: true);
        _actionFrames = LoadFrames("action", 29, oneBased: true, twoDigit: true);
        _struggleFrames = LoadFrames("struggle", 4, oneBased: true, twoDigit: true);
        _meditateFrames = LoadFrames("meditate", 24, oneBased: true, twoDigit: true);
        ShowWalkFrame(0);

        CreateTrayIcon();

        _dragSurface.MouseLeftButtonDown += BeginDragging;
        _dragSurface.MouseMove += ContinueDragging;
        _dragSurface.MouseLeftButtonUp += FinishDragging;

        SourceInitialized += OnSourceInitialized;
        Loaded += OnLoaded;
        Closing += OnClosing;
        Closed += OnClosed;

        _timer = new DispatcherTimer(DispatcherPriority.Render)
        {
            Interval = TimeSpan.FromSeconds(1.0 / 30.0),
        };
        _timer.Tick += Tick;
    }

    private static double ValidChoice(double candidate, double[] choices, double fallback)
    {
        return choices.Any(choice => Math.Abs(candidate - choice) < 0.1) ? candidate : fallback;
    }

    private static BitmapSource[] LoadFrames(string stem, int count, bool oneBased, bool twoDigit = false)
    {
        var frames = new BitmapSource[count];
        for (var index = 0; index < count; index++)
        {
            var number = oneBased ? index + 1 : index;
            var suffix = twoDigit ? number.ToString("00") : number.ToString();
            var uri = new Uri($"pack://application:,,,/Resources/{stem}-{suffix}.png", UriKind.Absolute);
            var bitmap = new BitmapImage();
            bitmap.BeginInit();
            bitmap.UriSource = uri;
            bitmap.CacheOption = BitmapCacheOption.OnLoad;
            bitmap.CreateOptions = BitmapCreateOptions.PreservePixelFormat;
            bitmap.EndInit();
            bitmap.Freeze();
            frames[index] = bitmap;
        }

        return frames;
    }

    private void OnSourceInitialized(object? sender, EventArgs args)
    {
        _handle = new WindowInteropHelper(this).Handle;
        var extendedStyle = GetWindowLongPtr(_handle, GwlExStyle);
        SetWindowLongPtr(_handle, GwlExStyle, extendedStyle | WsExToolWindow | WsExNoActivate);
    }

    private void OnLoaded(object sender, RoutedEventArgs args)
    {
        PlaceAtSavedPosition();
        _lastUpdate = _clock.Elapsed.TotalSeconds;
        _timer.Start();
    }

    private void Tick(object? sender, EventArgs args)
    {
        var now = _clock.Elapsed.TotalSeconds;
        var delta = Math.Min(Math.Max(now - _lastUpdate, 0), 0.1);
        _lastUpdate = now;

        if (_hidden)
        {
            return;
        }

        if (_dragging)
        {
            AdvanceStruggle(delta);
            return;
        }

        if (_paused)
        {
            AdvanceMeditation(delta);
            return;
        }

        if (_motionMode == MotionMode.StaffSpin)
        {
            AdvanceStaffSpin(delta);
            return;
        }

        _animationTime += delta;
        var frameIndex = (int)Math.Floor(_animationTime / WalkFrameDuration) % _walkFrames.Length;
        ShowWalkFrame(frameIndex);

        _timeUntilAction -= delta;
        if (_timeUntilAction <= 0)
        {
            StartStaffSpin();
            return;
        }

        if (!_movesAcrossScreen || !TryGetWindowRect(out var windowRect))
        {
            return;
        }

        var screen = _activityScreen ?? ScreenForWindow();
        _activityScreen = screen;
        var workingArea = screen.WorkingArea;
        _movementX += _walkingSpeed * delta;
        var rightEdge = workingArea.Right - windowRect.Width;
        if (_movementX >= rightEdge)
        {
            _movementX = workingArea.Left - windowRect.Width;
            _animationTime = 0;
            ShowWalkFrame(0);
        }

        SetWindowPosition((int)Math.Round(_movementX), windowRect.Top);
    }

    private void StartStaffSpin()
    {
        _motionMode = MotionMode.StaffSpin;
        _actionFrameIndex = 0;
        _actionElapsed = 0;
        ShowActionFrame(0);
    }

    private void AdvanceStaffSpin(double delta)
    {
        _actionElapsed += delta;
        while (_actionFrameIndex < ActionFrameDurations.Length &&
               _actionElapsed >= ActionFrameDurations[_actionFrameIndex])
        {
            _actionElapsed -= ActionFrameDurations[_actionFrameIndex];
            _actionFrameIndex++;
        }

        if (_actionFrameIndex >= ActionFrameDurations.Length)
        {
            _motionMode = MotionMode.Walking;
            _animationTime = 3 * WalkFrameDuration;
            _timeUntilAction = RandomActionDelay();
            ShowWalkFrame(3);
            return;
        }

        ShowActionFrame(_actionFrameIndex);
    }

    private void AdvanceStruggle(double delta)
    {
        _struggleElapsed += delta;
        while (_struggleElapsed >= StruggleFrameDurations[_struggleStepIndex])
        {
            _struggleElapsed -= StruggleFrameDurations[_struggleStepIndex];
            _struggleStepIndex = (_struggleStepIndex + 1) % StruggleFrameSequence.Length;
        }

        ShowStruggleFrame(StruggleFrameSequence[_struggleStepIndex]);
    }

    private void AdvanceMeditation(double delta)
    {
        _meditationTime += delta;
        var frameIndex = (int)Math.Floor(_meditationTime / MeditateFrameDuration) % _meditateFrames.Length;
        ShowMeditateFrame(frameIndex);
    }

    private static double RandomActionDelay() => 11.0 + Random.Shared.NextDouble() * 7.0;

    private void ShowWalkFrame(int index) => ShowFrame(DisplayMode.Walking, _walkFrames, index);
    private void ShowActionFrame(int index) => ShowFrame(DisplayMode.StaffSpin, _actionFrames, index);
    private void ShowStruggleFrame(int index) => ShowFrame(DisplayMode.Struggle, _struggleFrames, index);
    private void ShowMeditateFrame(int index) => ShowFrame(DisplayMode.Meditate, _meditateFrames, index);

    private void ShowFrame(DisplayMode mode, BitmapSource[] frames, int index)
    {
        var safeIndex = Math.Clamp(index, 0, frames.Length - 1);
        if (_displayMode == mode && _displayFrameIndex == safeIndex)
        {
            return;
        }

        _displayMode = mode;
        _displayFrameIndex = safeIndex;
        _petImage.Source = frames[safeIndex];
    }

    private void BeginDragging(object sender, MouseButtonEventArgs args)
    {
        if (args.ChangedButton != MouseButton.Left ||
            !GetCursorPos(out var cursor) ||
            !TryGetWindowRect(out var windowRect))
        {
            return;
        }

        _dragging = true;
        _motionMode = MotionMode.Walking;
        _struggleStepIndex = 0;
        _struggleElapsed = 0;
        _timeUntilAction = RandomActionDelay();
        _dragOffsetX = cursor.X - windowRect.Left;
        _dragOffsetY = cursor.Y - windowRect.Top;
        ShowStruggleFrame(StruggleFrameSequence[0]);
        Mouse.Capture(_dragSurface, CaptureMode.Element);
        args.Handled = true;
    }

    private void ContinueDragging(object sender, System.Windows.Input.MouseEventArgs args)
    {
        if (!_dragging)
        {
            return;
        }

        if (args.LeftButton != MouseButtonState.Pressed)
        {
            CompleteDrag();
            return;
        }

        if (GetCursorPos(out var cursor))
        {
            SetWindowPosition(cursor.X - _dragOffsetX, cursor.Y - _dragOffsetY);
        }

        args.Handled = true;
    }

    private void FinishDragging(object sender, MouseButtonEventArgs args)
    {
        if (!_dragging || args.ChangedButton != MouseButton.Left)
        {
            return;
        }

        CompleteDrag();
        args.Handled = true;
    }

    private void CompleteDrag()
    {
        if (!_dragging)
        {
            return;
        }

        _dragging = false;
        if (Mouse.Captured == _dragSurface)
        {
            Mouse.Capture(null);
        }

        _activityScreen = ScreenForWindow();
        ClampToScreen(_activityScreen);
        if (TryGetWindowRect(out var windowRect))
        {
            _movementX = windowRect.Left;
        }
        SavePosition();

        if (_paused)
        {
            var frame = (int)Math.Floor(_meditationTime / MeditateFrameDuration) % _meditateFrames.Length;
            ShowMeditateFrame(frame);
        }
        else
        {
            var frame = (int)Math.Floor(_animationTime / WalkFrameDuration) % _walkFrames.Length;
            ShowWalkFrame(frame);
        }
    }

    private void CreateTrayIcon()
    {
        _trayIcon = LoadTrayIcon();
        _notifyIcon = new Forms.NotifyIcon
        {
            Icon = _trayIcon,
            Text = "艾丝蒂尔桌宠",
            Visible = true,
        };

        var menu = new Forms.ContextMenuStrip();

        _pauseMenuItem = new Forms.ToolStripMenuItem("暂停");
        _pauseMenuItem.Click += (_, _) => OnUi(TogglePause);
        menu.Items.Add(_pauseMenuItem);

        _visibilityMenuItem = new Forms.ToolStripMenuItem("隐藏艾丝蒂尔");
        _visibilityMenuItem.Click += (_, _) => OnUi(ToggleVisibility);
        menu.Items.Add(_visibilityMenuItem);
        menu.Items.Add(new Forms.ToolStripSeparator());

        var sizeRoot = new Forms.ToolStripMenuItem("大小");
        AddChoice(sizeRoot, _sizeMenuItems, "小", PetSizeSmall, _petSize, ChangeSize);
        AddChoice(sizeRoot, _sizeMenuItems, "中", PetSizeMedium, _petSize, ChangeSize);
        AddChoice(sizeRoot, _sizeMenuItems, "大", PetSizeLarge, _petSize, ChangeSize);
        menu.Items.Add(sizeRoot);

        var movementRoot = new Forms.ToolStripMenuItem("移动方式");
        _walkingMenuItem = new Forms.ToolStripMenuItem("走路") { Checked = _movesAcrossScreen };
        _walkingMenuItem.Click += (_, _) => OnUi(() => ChangeMovementMode(true));
        movementRoot.DropDownItems.Add(_walkingMenuItem);
        _steppingMenuItem = new Forms.ToolStripMenuItem("原地踏步") { Checked = !_movesAcrossScreen };
        _steppingMenuItem.Click += (_, _) => OnUi(() => ChangeMovementMode(false));
        movementRoot.DropDownItems.Add(_steppingMenuItem);
        menu.Items.Add(movementRoot);

        var speedRoot = new Forms.ToolStripMenuItem("行走速度");
        AddChoice(speedRoot, _speedMenuItems, "很慢", WalkingSpeedVerySlow, _walkingSpeed, ChangeSpeed);
        AddChoice(speedRoot, _speedMenuItems, "慢（默认）", WalkingSpeedSlow, _walkingSpeed, ChangeSpeed);
        AddChoice(speedRoot, _speedMenuItems, "悠闲", WalkingSpeedLeisurely, _walkingSpeed, ChangeSpeed);
        menu.Items.Add(speedRoot);

        var returnItem = new Forms.ToolStripMenuItem("回到主屏幕底部");
        returnItem.Click += (_, _) => OnUi(ReturnToMainScreen);
        menu.Items.Add(returnItem);
        menu.Items.Add(new Forms.ToolStripSeparator());

        var quitItem = new Forms.ToolStripMenuItem("退出");
        quitItem.Click += (_, _) => OnUi(ExitApplication);
        menu.Items.Add(quitItem);

        _notifyIcon.ContextMenuStrip = menu;
        _notifyIcon.DoubleClick += (_, _) => OnUi(ToggleVisibility);
    }

    private static Icon LoadTrayIcon()
    {
        var resource = System.Windows.Application.GetResourceStream(
            new Uri("pack://application:,,,/Resources/status-icon-twintail.ico", UriKind.Absolute));
        if (resource is null)
        {
            return (Icon)SystemIcons.Application.Clone();
        }

        using var source = new Icon(resource.Stream);
        return (Icon)source.Clone();
    }

    private static void AddChoice(
        Forms.ToolStripMenuItem parent,
        List<Forms.ToolStripMenuItem> group,
        string title,
        double value,
        double selected,
        Action<double> action)
    {
        var item = new Forms.ToolStripMenuItem(title)
        {
            Tag = value,
            Checked = Math.Abs(value - selected) < 0.1,
        };
        item.Click += (_, _) => action(value);
        parent.DropDownItems.Add(item);
        group.Add(item);
    }

    private void OnUi(Action action)
    {
        if (Dispatcher.CheckAccess())
        {
            action();
        }
        else
        {
            Dispatcher.BeginInvoke(action);
        }
    }

    private void TogglePause()
    {
        _paused = !_paused;
        _pauseMenuItem.Text = _paused ? "继续" : "暂停";
        if (_paused)
        {
            _motionMode = MotionMode.Walking;
            _meditationTime = 0;
            ShowMeditateFrame(0);
        }
        else
        {
            var frame = (int)Math.Floor(_animationTime / WalkFrameDuration) % _walkFrames.Length;
            ShowWalkFrame(frame);
            _timeUntilAction = RandomActionDelay();
        }

        _lastUpdate = _clock.Elapsed.TotalSeconds;
    }

    private void ToggleVisibility()
    {
        _hidden = !_hidden;
        if (_hidden)
        {
            Hide();
            _visibilityMenuItem.Text = "显示艾丝蒂尔";
        }
        else
        {
            Show();
            SetWindowPos(_handle, HwndTopmost, 0, 0, 0, 0, SwpNoMove | SwpNoSize | SwpNoActivate | SwpShowWindow);
            _visibilityMenuItem.Text = "隐藏艾丝蒂尔";
            _lastUpdate = _clock.Elapsed.TotalSeconds;
        }
    }

    private void ChangeSize(double size)
    {
        _petSize = size;
        foreach (var item in _sizeMenuItems)
        {
            item.Checked = item.Tag is double value && Math.Abs(value - size) < 0.1;
        }

        var screen = _activityScreen ?? ScreenForWindow();
        Width = size;
        Height = size;
        UpdateLayout();
        ClampToScreen(screen);
        if (TryGetWindowRect(out var windowRect))
        {
            _movementX = windowRect.Left;
        }
        SavePosition();
    }

    private void ChangeSpeed(double speed)
    {
        _walkingSpeed = speed;
        foreach (var item in _speedMenuItems)
        {
            item.Checked = item.Tag is double value && Math.Abs(value - speed) < 0.1;
        }
        SavePosition();
    }

    private void ChangeMovementMode(bool movesAcrossScreen)
    {
        _movesAcrossScreen = movesAcrossScreen;
        _walkingMenuItem.Checked = movesAcrossScreen;
        _steppingMenuItem.Checked = !movesAcrossScreen;
        if (TryGetWindowRect(out var windowRect))
        {
            _movementX = windowRect.Left;
        }
        _lastUpdate = _clock.Elapsed.TotalSeconds;
        SavePosition();
    }

    private void ReturnToMainScreen()
    {
        _activityScreen = Forms.Screen.PrimaryScreen ?? Forms.Screen.AllScreens.First();
        PlaceOnGround(_activityScreen);
        if (_hidden)
        {
            ToggleVisibility();
        }
        SavePosition();
    }

    private void PlaceAtSavedPosition()
    {
        if (_settings.WindowLeft is int savedLeft && _settings.WindowTop is int savedTop)
        {
            var point = new System.Drawing.Point(savedLeft, savedTop);
            _activityScreen = Forms.Screen.FromPoint(point);
            SetWindowPosition(savedLeft, savedTop);
            ClampToScreen(_activityScreen);
        }
        else
        {
            _activityScreen = Forms.Screen.PrimaryScreen ?? Forms.Screen.AllScreens.First();
            PlaceOnGround(_activityScreen);
        }

        if (TryGetWindowRect(out var windowRect))
        {
            _movementX = windowRect.Left;
        }
    }

    private void PlaceOnGround(Forms.Screen screen)
    {
        if (!TryGetWindowRect(out var windowRect))
        {
            return;
        }

        var workingArea = screen.WorkingArea;
        SetWindowPosition(workingArea.Left + 50, workingArea.Bottom - windowRect.Height - 2);
        _movementX = workingArea.Left + 50;
    }

    private Forms.Screen ScreenForWindow()
    {
        if (!TryGetWindowRect(out var windowRect))
        {
            return Forms.Screen.PrimaryScreen ?? Forms.Screen.AllScreens.First();
        }

        return Forms.Screen.FromPoint(new System.Drawing.Point(
            windowRect.Left + windowRect.Width / 2,
            windowRect.Top + windowRect.Height / 2));
    }

    private void ClampToScreen(Forms.Screen screen)
    {
        if (!TryGetWindowRect(out var windowRect))
        {
            return;
        }

        var workingArea = screen.WorkingArea;
        var maxLeft = Math.Max(workingArea.Left, workingArea.Right - windowRect.Width);
        var maxTop = Math.Max(workingArea.Top, workingArea.Bottom - windowRect.Height);
        var left = Math.Clamp(windowRect.Left, workingArea.Left, maxLeft);
        var top = Math.Clamp(windowRect.Top, workingArea.Top, maxTop);
        SetWindowPosition(left, top);
    }

    private void SetWindowPosition(int left, int top)
    {
        if (_handle == nint.Zero)
        {
            return;
        }

        SetWindowPos(_handle, HwndTopmost, left, top, 0, 0, SwpNoSize | SwpNoActivate | SwpShowWindow);
    }

    private bool TryGetWindowRect(out NativeRect windowRect)
    {
        if (_handle != nint.Zero && GetWindowRect(_handle, out windowRect))
        {
            return true;
        }

        windowRect = default;
        return false;
    }

    private void SavePosition()
    {
        _settings.PetSize = _petSize;
        _settings.WalkingSpeed = _walkingSpeed;
        _settings.MovesAcrossScreen = _movesAcrossScreen;
        if (TryGetWindowRect(out var windowRect))
        {
            _settings.WindowLeft = windowRect.Left;
            _settings.WindowTop = windowRect.Top;
        }
        SettingsStore.Save(_settings);
    }

    private void ExitApplication()
    {
        _exiting = true;
        SavePosition();
        _timer.Stop();
        _notifyIcon.Visible = false;
        System.Windows.Application.Current.Shutdown();
    }

    private void OnClosing(object? sender, CancelEventArgs args)
    {
        if (_exiting)
        {
            return;
        }

        args.Cancel = true;
        if (!_hidden)
        {
            ToggleVisibility();
        }
    }

    private void OnClosed(object? sender, EventArgs args)
    {
        _timer.Stop();
        _notifyIcon.Visible = false;
        _notifyIcon.ContextMenuStrip?.Dispose();
        _notifyIcon.Dispose();
        _trayIcon.Dispose();
    }

    private const int GwlExStyle = -20;
    private static readonly nint HwndTopmost = new(-1);
    private static readonly nint WsExToolWindow = new(0x00000080L);
    private static readonly nint WsExNoActivate = new(0x08000000L);
    private const uint SwpNoSize = 0x0001;
    private const uint SwpNoMove = 0x0002;
    private const uint SwpNoActivate = 0x0010;
    private const uint SwpShowWindow = 0x0040;

    [StructLayout(LayoutKind.Sequential)]
    private struct NativePoint
    {
        public int X;
        public int Y;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct NativeRect
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
        public readonly int Width => Right - Left;
        public readonly int Height => Bottom - Top;
    }

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GetCursorPos(out NativePoint point);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GetWindowRect(nint window, out NativeRect rect);

    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool SetWindowPos(
        nint window,
        nint insertAfter,
        int x,
        int y,
        int width,
        int height,
        uint flags);

    [DllImport("user32.dll", EntryPoint = "GetWindowLongPtrW")]
    private static extern nint GetWindowLongPtr(nint window, int index);

    [DllImport("user32.dll", EntryPoint = "SetWindowLongPtrW")]
    private static extern nint SetWindowLongPtr(nint window, int index, nint value);
}
