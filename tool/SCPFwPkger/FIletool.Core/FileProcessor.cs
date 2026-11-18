using System;
using System.Collections.Generic;
using System.IO;
using System.IO.Compression;
using System.IO.Hashing;
using System.Text.Json;

namespace FileTool.Core
{
	public class Manifest
    {
        public List<string> pre_command { get; set; } = new();
        public List<ManifestFile> files { get; set; } = new();
        public List<string> post_command { get; set; } = new();
    }

    public class ManifestFile
    {
        public string src { get; set; }
        public string dst { get; set; }
        public string crc32 { get; set; }
        public string size { get; set; }
    }
	
    public class FileInfoResult
    {
        public string Path { get; set; }
        public long Size { get; set; }
        public string CRC32 { get; set; }
    }

    public static class FileProcessor
    {
        public static List<FileInfoResult> Scan(string dir, Action<int, int, string> progress = null)
        {
            var files = Directory.GetFiles(dir, "*", SearchOption.AllDirectories);
            var result = new List<FileInfoResult>();

            for (int i = 0; i < files.Length; i++)
            {
                string file = files[i];

                result.Add(new FileInfoResult
                {
                    Path = file,
                    Size = new FileInfo(file).Length,
                    CRC32 = GetCRC32(file)
                });

                progress?.Invoke(i + 1, files.Length, file);
            }

            return result;
        }

        public static string CreateZip(string dir)
        {
            string zipPath = Path.Combine(
                Directory.GetParent(dir).FullName,
                Path.GetFileName(dir) + ".zip"
            );

            if (File.Exists(zipPath))
                File.Delete(zipPath);

            ZipFile.CreateFromDirectory(dir, zipPath);

            return zipPath;
        }

        private static string GetCRC32(string file)
        {
            using var stream = File.OpenRead(file);
            var crc = new Crc32();
            crc.Append(stream);
            return crc.GetCurrentHashAsUInt32().ToString("X");
        }
		
		private static string MapDestination(string relative)
		{
			if (relative.EndsWith(".sh"))
				return "/usr/local/bin/" + Path.GetFileName(relative);

			if (relative.EndsWith(".lua"))
				return "/etc/ext_scripts/" + Path.GetFileName(relative);

			return "/tmp/" + Path.GetFileName(relative);
		}
		
		public static bool addManifest(string dir){
			string manifestPath = Path.GetRelativePath(dir, "manifest.json");
			Manifest manifest;
			string Size;
			string CRC32;
			if (File.Exists(manifestPath))
			{
				string json = File.ReadAllText(manifestPath);

				manifest = JsonSerializer.Deserialize<Manifest>(json)
							?? new Manifest();
				Size = "";
                CRC32 = GetCRC32(manifestPath);
				
			}
			else
			{
				return false;
			}
			ManifestFile newFile = new  ManifestFile
			{
				src = "cec_init.sh",
				dst = "",
				crc32 = CRC32,
				size = Size
			};
			// 2. Append new item
			manifest.files.Add(newFile);

			// 3. Save back
			var options = new JsonSerializerOptions
			{
				WriteIndented = true
			};

			File.WriteAllText(manifestPath,
				JsonSerializer.Serialize(manifest, options));
			return true;
		}
		
		public static string GenerateManifest(string dir, List<FileInfoResult> files)
		{
			var manifest = new Manifest();

			foreach (var f in files)
			{
				string relative = Path.GetRelativePath(dir, f.Path);

				manifest.files.Add(new ManifestFile
				{
					src = relative.Replace("\\", "/"),
					dst = MapDestination(relative), 
					crc32 = f.CRC32,
					size = f.Size.ToString()
				});
			}

			string json = JsonSerializer.Serialize(manifest, new JsonSerializerOptions
			{
				WriteIndented = true
			});

			string output = Path.Combine(dir, "manifest.json");
			File.WriteAllText(output, json);

			return output;
		}
    }
}