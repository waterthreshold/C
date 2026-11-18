using System;
using System.Drawing;
using System.Windows.Forms;
using Renci.SshNet;
using System.IO;
using System.Threading.Tasks;

using System.IO.Compression;
using System.Text.Json;

using System.IO.Hashing;
using System.Collections.Generic;

namespace ScpTransferTool
{
public class Manifest
{
    public List<string> pre_command { get; set; }
    public List<string> post_command { get; set; }
    public List<FileItem> files { get; set; }
}

public class FileItem
{
    public string src { get; set; }
    public string dst { get; set; }
	public string crc32 { get; set; }
	public string size { get; set; }
}

public class Root
{
    public List<FileItem> files { get; set; }
}

    public class Form1 : Form
    {
        // Controls
        TextBox txtHost, txtUser, txtPassword, txtLocalFile, txtRemotePath;
        Button btnBrowse, btnUpload, btnDownload;
        ProgressBar progressBar;
        Label lblStatus;
		MenuStrip menuStrip;
		
        public Form1()
        {
            InitializeUI();
        }

        private void InitializeUI()
        {
            this.Text = "scpc64";
            this.Size = new Size(500, 350);
            this.StartPosition = FormStartPosition.CenterScreen;
			// this.Icon = new Icon("Resources/favicon.ico");
			
            int labelX = 20;
            int inputX = 150;
            int y = 40;
            int gap = 30;
				
			// menuStrip
			menuStrip = new MenuStrip();
			// Top-level menu
			ToolStripMenuItem helpMenu = new ToolStripMenuItem("Help");

			// Sub item: About
			ToolStripMenuItem aboutItem = new ToolStripMenuItem("About");
			aboutItem.Click += AboutItem_Click;

			// Add hierarchy
			helpMenu.DropDownItems.Add(aboutItem);
			menuStrip.Items.Add(helpMenu);

			// Add to form
			this.MainMenuStrip = menuStrip;
			this.Controls.Add(menuStrip);
			
            // Host
            Controls.Add(new Label() { Text = "Host:", Location = new Point(labelX, y) });
            txtHost = new TextBox() { Location = new Point(inputX, y), Width = 250 , Text = "192.168.100.20" };
            Controls.Add(txtHost);

            y += gap;

            // User
            Controls.Add(new Label() { Text = "Username:", Location = new Point(labelX, y) });
            txtUser = new TextBox() { Location = new Point(inputX, y), Width = 250 , Text = "root" };
            Controls.Add(txtUser);

            y += gap;

            // Password
            Controls.Add(new Label() { Text = "Password:", Location = new Point(labelX, y) });
            txtPassword = new TextBox() { Location = new Point(inputX, y), Width = 250, PasswordChar = '*' };
            Controls.Add(txtPassword);

            y += gap;

            // Local File
            Controls.Add(new Label() { Text = "Local File:", Location = new Point(labelX, y) });
            txtLocalFile = new TextBox() { Location = new Point(inputX, y), Width = 180 };
            Controls.Add(txtLocalFile);

            btnBrowse = new Button()
            {
                Text = "Browse",
                Location = new Point(inputX + 190, y),
                Width = 60
            };
            btnBrowse.Click += BtnBrowse_Click;
            Controls.Add(btnBrowse);

            y += gap;

            // Remote Path
            Controls.Add(new Label() { Text = "Remote Path:", Location = new Point(labelX, y) });
            txtRemotePath = new TextBox() { Location = new Point(inputX, y), Width = 250 };
            Controls.Add(txtRemotePath);

            y += gap + 10;

            // Buttons
            btnUpload = new Button()
            {
                Text = "Upload",
                Location = new Point(inputX, y),
                Width = 100
            };
            btnUpload.Click += BtnUpload_Click;
            Controls.Add(btnUpload);

            btnDownload = new Button()
            {
                Text = "Download",
                Location = new Point(inputX + 120, y),
                Width = 100
            };
            btnDownload.Click += BtnDownload_Click;
            Controls.Add(btnDownload);

            y += gap + 10;

            // Progress bar
            progressBar = new ProgressBar()
            {
                Location = new Point(inputX, y),
                Width = 250
            };
            Controls.Add(progressBar);

            y += gap;

            // Status
            lblStatus = new Label()
            {
                Text = "Ready",
                Location = new Point(inputX, y),
                Width = 300
            };
            Controls.Add(lblStatus);
        }

        // ===== Events =====

        private void BtnBrowse_Click(object sender, EventArgs e)
        {
            using (OpenFileDialog ofd = new OpenFileDialog())
            {
                if (ofd.ShowDialog() == DialogResult.OK)
                {
                    txtLocalFile.Text = ofd.FileName;
                }
            }
        }
		
        private async void BtnUpload_Click(object sender, EventArgs e)
        {
			
			
            string zipPath = txtLocalFile.Text;
			// string extractPath = Path.Join(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Documents");
			// Console.WriteLine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile));
			
			lblStatus.Text = "Uploading...";
			// if (Directory.Exists(extractPath))
			// {
				// Directory.Delete(extractPath, true);
			// }

			// 建立資料夾（可選）
			// Directory.CreateDirectory(extractPath);

			// 解壓
			// ZipFile.ExtractToDirectory(zipPath, extractPath);
			
			// must instead 
			string extractPath =Path.Join(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Documents" ,"larnaca2");
			// if (Directory.Exists(extractPath))
			// {
				// Directory.Delete(extractPath, true);
			// }
			// 建立資料夾（可選）
			// Directory.CreateDirectory(extractPath);
			
			// string manifestPath = Path.Join(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Documents" ,"larnaca2", "manifest.json");
			string jsonString = "";
			// Console.WriteLine(jsonString);
			using (ZipArchive archive = ZipFile.Open(zipPath, ZipArchiveMode.Update))
            {
                ZipArchiveEntry entry = archive.GetEntry("manifest.json");
				if ( entry != null) {
					using (StreamReader Reader = new StreamReader(entry.Open()))
					{
						jsonString=Reader.ReadToEnd();
						// writer.WriteLine("append line to file");
					}
				} else {
					lblStatus.Text = "Manifest got something wrong!!";
					return;
				}
                
            }
			
			var manifest = JsonSerializer.Deserialize<Manifest>(jsonString);
			Console.WriteLine(jsonString);
			
			//Root
			await Task.Run(() =>
			{
				try
				{
					using (var mysshClient = new SshClient(txtHost.Text, txtUser.Text, txtPassword.Text))
					{
						mysshClient.Connect();
						foreach (var parsecmd in manifest.pre_command)
						{
							 Console.WriteLine("PRE: " + parsecmd);
							var cmd = mysshClient.CreateCommand(parsecmd);
							var result = cmd.Execute();
					
							Console.WriteLine("Output:");
							Console.WriteLine(result);

							if (!string.IsNullOrEmpty(cmd.Error))
							{
								Console.WriteLine("Error:");
								Console.WriteLine(cmd.Error);
							}
						}
						mysshClient.Disconnect();
					}
					using (var client = new ScpClient(txtHost.Text, txtUser.Text, txtPassword.Text))
					{
						client.Uploading += (s, ev) =>
						{
							Invoke(new Action(() =>
							{
								progressBar.Maximum = (int)Math.Min(ev.Size, int.MaxValue);
								progressBar.Value = (int)Math.Min(ev.Uploaded, int.MaxValue);

								lblStatus.Text = $"Uploading {ev.Uploaded}/{ev.Size}";
							}));
						};

						client.Connect();
						
						
						
						foreach (var file in manifest.files)
						{
							lblStatus.Text=file.dst;
							txtRemotePath.Text=file.dst;
							// Console.WriteLine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile));
							
							// using (var fs = new FileStream(Path.Join(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Documents" ,"larnaca2",file.src), FileMode.Open))
							// {
								
								// client.Upload(fs, file.dst);
							// }
							
							using (ZipArchive archive = ZipFile.OpenRead(zipPath))
							{
								
								foreach (ZipArchiveEntry entry in archive.Entries)
								{
									if (entry.FullName.Equals("manifest.json", StringComparison.OrdinalIgnoreCase)) break;
									
									if (entry.FullName.Equals(file.src, StringComparison.OrdinalIgnoreCase))
									{
										// Gets the full path to ensure that relative segments are removed.
										string destinationPath = Path.GetFullPath(Path.Combine(extractPath, entry.FullName));
										
										
										Console.WriteLine(destinationPath);
										// Ordinal match is safest, case-sensitive volumes can be mounted within volumes that
										// are case-insensitive.
										if (destinationPath.StartsWith(extractPath, StringComparison.Ordinal))
											entry.ExtractToFile(destinationPath,true);
										using (var fs = new FileStream(destinationPath, FileMode.Open))
										{	
										
											var crc32 = new Crc32();
											crc32.Append(fs);
											var crcText = crc32.GetCurrentHashAsUInt32().ToString("X");
											
											Console.WriteLine(crcText);
											fs.Seek(0, SeekOrigin.Begin);
											if (crcText.Equals( file.crc32 ,StringComparison.OrdinalIgnoreCase))
											{
												Console.WriteLine("file crc32:" + file.crc32);
												client.Upload(fs, file.dst);
											}
										}
									}
								}
							}
							// client.Upload(fs, txtRemotePath.Text);
						}
						
						
						client.Disconnect();
					}
					using (var mysshClient = new SshClient(txtHost.Text, txtUser.Text, txtPassword.Text))
					{
						mysshClient.Connect();
						foreach (var parsecmd in manifest.post_command)
						{
							 Console.WriteLine("POST: " + parsecmd);
							var cmd = mysshClient.CreateCommand(parsecmd);
							var result = cmd.Execute();
					
							Console.WriteLine("Output:");
							Console.WriteLine(result);

							if (!string.IsNullOrEmpty(cmd.Error))
							{
								Console.WriteLine("Error:");
								Console.WriteLine(cmd.Error);
							}
						}
						mysshClient.Disconnect();
					}
					Invoke(new Action(() =>
					{
						lblStatus.Text = "Upload complete";
					}));
				}
				catch (Exception ex)
				{
					Invoke(new Action(() =>
					{
						lblStatus.Text = "Error: " + ex.Message;
					}));
				}
			});
        }

        private void BtnDownload_Click(object sender, EventArgs e)
        {
            lblStatus.Text = "Download clicked (hook your SCP here)";
        }
		private void AboutItem_Click(object sender, EventArgs e)
		{
			MessageBox.Show(
				"scpc64\n" +
				"Version: 0.3 (Beta)\n\n" +
				"Features:\n" +
				"- Upload / Download via SCP\n" +
				"- Larana2 light weight firmware upgrade support\n\n" +
				"Author: Jeff Chiang@CEC \n" +
				"date: " + DateTime.Now.ToString("yyyy-MMⓒ"),
				"About",
				MessageBoxButtons.OK,
				MessageBoxIcon.Information
			);
		}
    }
}