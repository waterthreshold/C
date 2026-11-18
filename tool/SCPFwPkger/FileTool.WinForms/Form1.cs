using System;
using System.Windows.Forms;
using FileTool.Core;

namespace FileTool.WinForms
{
    public partial class Form1 : Form
    {
        private Button btnSelect;
        private Button btnStart;
		private Button btnZip;
        private TextBox txtPath;
        private DataGridView grid;
        private ProgressBar progressBar;

        private string selectedDir;

        public Form1()
        {
            InitUI();
        }

        private void InitUI()
        {
            this.Text = "File Tool";
            this.Width = 800;
            this.Height = 600;

            txtPath = new TextBox() { Left = 10, Top = 10, Width = 500 };
            btnSelect = new Button() { Left = 520, Top = 8, Width = 70, Text = "Select" };
            btnStart = new Button() { Left = 600, Top = 8, Width = 70, Text = "Start" };
			btnZip = new Button() { Left = 680, Top = 8, Width = 70, Text = "Zip" };
			
            progressBar = new ProgressBar()
            {
                Left = 10,
                Top = 40,
                Width = 760,
                Height = 20
            };

            grid = new DataGridView()
            {
                Left = 10,
                Top = 70,
                Width = 760,
                Height = 480
            };

            grid.Columns.Add("Path", "Path");
            grid.Columns.Add("Size", "Size");
            grid.Columns.Add("CRC32", "CRC32");

            btnSelect.Click += BtnSelect_Click;
            btnStart.Click += BtnStart_Click;
			btnZip.Click += BtnZip_Click;

            this.Controls.Add(txtPath);
            this.Controls.Add(btnSelect);
            this.Controls.Add(btnStart);
			this.Controls.Add(btnZip);
            this.Controls.Add(progressBar);
            this.Controls.Add(grid);
        }

        private void BtnSelect_Click(object sender, EventArgs e)
        {
            using var dlg = new FolderBrowserDialog();

            if (dlg.ShowDialog() == DialogResult.OK)
            {
                selectedDir = dlg.SelectedPath;
                txtPath.Text = selectedDir;
            }
        }

        private async void BtnStart_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(selectedDir))
            {
                MessageBox.Show("Please select a folder first.");
                return;
            }

            grid.Rows.Clear();
            progressBar.Value = 0;

            var files = await System.Threading.Tasks.Task.Run(() =>
                FileProcessor.Scan(selectedDir, (i, total, file) =>
                {
                    this.Invoke(new Action(() =>
                    {
                        progressBar.Value = i * 100 / total;
                    }));
                }));

            foreach (var f in files)
            {
                grid.Rows.Add(f.Path, f.Size, f.CRC32);
            }

            // string zip = FileProcessor.CreateZip(selectedDir);
			 // MessageBox.Show($"ZIP created:\n{zip}");	
			string manifestPath = FileProcessor.GenerateManifest(selectedDir, files);

			MessageBox.Show($"ZIP created\nManifest:\n{manifestPath}");
           
			 // MessageBox.Show($"ZIP created:\n{zip}");
        }
		
		private async void BtnZip_Click(object sender, EventArgs e)
        {
            if (string.IsNullOrEmpty(selectedDir))
            {
                MessageBox.Show("Please select a folder first.");
                return;
            }

            grid.Rows.Clear();
            progressBar.Value = 0;
			FileProcessor.addManifest(selectedDir);
            var files = await System.Threading.Tasks.Task.Run(() =>
                FileProcessor.Scan(selectedDir, (i, total, file) =>
                {
                    this.Invoke(new Action(() =>
                    {
                        progressBar.Value = i * 100 / total;
                    }));
                }));

            foreach (var f in files)
            {
                grid.Rows.Add(f.Path, f.Size, f.CRC32);
            }

            string zip = FileProcessor.CreateZip(selectedDir);
			 MessageBox.Show($"ZIP created:\n{zip}");	
			// string manifestPath = FileProcessor.GenerateManifest(selectedDir, files);

			// MessageBox.Show($"ZIP created\nManifest:\n{manifestPath}");
           
			 // MessageBox.Show($"ZIP created:\n{zip}");
        }
    }
}