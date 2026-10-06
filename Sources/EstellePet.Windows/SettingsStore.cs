using System.IO;
using System.Text.Json;

namespace EstellePet.WindowsApp;

internal sealed class PetSettings
{
    public double PetSize { get; set; } = 230;
    public double WalkingSpeed { get; set; } = 18;
    public bool MovesAcrossScreen { get; set; } = true;
    public int? WindowLeft { get; set; }
    public int? WindowTop { get; set; }
}

internal static class SettingsStore
{
    private static readonly string DirectoryPath = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
        "EstellePet");

    private static readonly string FilePath = Path.Combine(DirectoryPath, "settings.json");

    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        WriteIndented = true,
    };

    public static PetSettings Load()
    {
        try
        {
            if (!File.Exists(FilePath))
            {
                return new PetSettings();
            }

            return JsonSerializer.Deserialize<PetSettings>(File.ReadAllText(FilePath), JsonOptions)
                   ?? new PetSettings();
        }
        catch
        {
            return new PetSettings();
        }
    }

    public static void Save(PetSettings settings)
    {
        try
        {
            Directory.CreateDirectory(DirectoryPath);
            var temporaryPath = FilePath + ".tmp";
            File.WriteAllText(temporaryPath, JsonSerializer.Serialize(settings, JsonOptions));
            File.Move(temporaryPath, FilePath, overwrite: true);
        }
        catch
        {
            // Preferences are helpful, but failure to save must not stop the pet.
        }
    }
}
