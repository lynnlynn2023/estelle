using System.IO;
using System.Threading;
using System.Windows;
using System.Windows.Threading;

namespace EstellePet.WindowsApp;

internal static class Program
{
    private const string MutexName = @"Local\EstellePetDesktopPet";

    [STAThread]
    public static void Main()
    {
        using var mutex = new Mutex(initiallyOwned: true, MutexName, out var ownsMutex);
        if (!ownsMutex)
        {
            System.Windows.MessageBox.Show("艾丝蒂尔桌宠已经在运行。", "艾丝蒂尔桌宠", MessageBoxButton.OK, MessageBoxImage.Information);
            return;
        }

        var application = new System.Windows.Application
        {
            ShutdownMode = ShutdownMode.OnExplicitShutdown,
        };
        application.DispatcherUnhandledException += OnUnhandledException;

        var window = new PetWindow();
        application.Run(window);
    }

    private static void OnUnhandledException(object sender, DispatcherUnhandledExceptionEventArgs args)
    {
        try
        {
            var directory = Path.Combine(
                Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                "EstellePet");
            Directory.CreateDirectory(directory);
            File.AppendAllText(
                Path.Combine(directory, "error.log"),
                $"[{DateTimeOffset.Now:O}] {args.Exception}\n\n");
        }
        catch
        {
            // Reporting must never hide the original error dialog.
        }

        System.Windows.MessageBox.Show(
            "艾丝蒂尔桌宠遇到了一个错误。详细信息已写入 %LOCALAPPDATA%\\EstellePet\\error.log。",
            "艾丝蒂尔桌宠",
            MessageBoxButton.OK,
            MessageBoxImage.Error);
        args.Handled = true;
    }
}
