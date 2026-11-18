using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace AppTitleLister
{
    public partial class Form1 : Form
    {
        private TextBox txtSearch;
        private ListBox listBoxApps;
        private Button btnRefresh;

        // Hold all retrieved items for filtering
        private List<AppInfo> allApps = new List<AppInfo>();

        // Helper class to store process details alongside the display name
        private class AppInfo
        {
            public string DisplayText { get; set; }
            public int ProcessId { get; set; }
            public string WindowTitle { get; set; }

            public override string ToString() => DisplayText;
        }

        // Win32 API to bring window to front / activate it
        [DllImport("user32.dll")]
        private static extern bool SetForegroundWindow(IntPtr hWnd);

        [DllImport("user32.dll")]
        private static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

        private const int SW_RESTORE = 9;

        public Form1()
        {
            InitializeComponentCustom();
        }

        private void InitializeComponentCustom()
        {
            this.Text = "Running Apps Lister & Switcher";
            this.Width = 550;
            this.Height = 450;

            // Search Box (Top)
            txtSearch = new TextBox();
            txtSearch.Dock = DockStyle.Top;
            txtSearch.Font = new System.Drawing.Font("Segoe UI", 10F);
            txtSearch.TextChanged += new EventHandler(txtSearch_TextChanged);

            // ListBox (Middle)
            listBoxApps = new ListBox();
            listBoxApps.Dock = DockStyle.Fill;
            listBoxApps.Font = new System.Drawing.Font("Segoe UI", 9.5F);
            listBoxApps.DoubleClick += new EventHandler(listBoxApps_DoubleClick);

            // Refresh Button (Bottom)
            btnRefresh = new Button();
            btnRefresh.Text = "List Running Apps";
            btnRefresh.Dock = DockStyle.Bottom;
            btnRefresh.Height = 40;
            btnRefresh.Click += new EventHandler(btnRefresh_Click);

            // Add controls to form (Dock order matters: Top, Bottom, Fill)
            this.Controls.Add(listBoxApps);
            this.Controls.Add(txtSearch);
            this.Controls.Add(btnRefresh);

            // Optional placeholder text hint above search box
            ToolTip toolTip = new ToolTip();
            toolTip.SetToolTip(txtSearch, "Type here to filter running apps...");
        }

        private void btnRefresh_Click(object sender, EventArgs e)
        {
            LoadRunningApps();
        }

        private void LoadRunningApps()
        {
            allApps.Clear();
            Process[] processList = Process.GetProcesses();

            foreach (Process process in processList)
            {
                if (!string.IsNullOrEmpty(process.MainWindowTitle))
                {
                    allApps.Add(new AppInfo
                    {
                        WindowTitle = process.MainWindowTitle,
                        ProcessId = process.Id,
                        DisplayText = $"{process.MainWindowTitle} ({process.ProcessName}, ID: {process.Id})"
                    });
                }
            }

            FilterAndDisplayApps();
        }

        private void FilterAndDisplayApps()
        {
            listBoxApps.Items.Clear();
            string keyword = txtSearch.Text.Trim().ToLower();

            int count = 0;
            foreach (var app in allApps)
            {
                // Check if the window title or display text contains the search input
                if (string.IsNullOrEmpty(keyword) || app.DisplayText.ToLower().Contains(keyword))
                {
                    listBoxApps.Items.Add(app);
                    count++;
                }
            }

            this.Text = $"Running Apps Found: {count}";
        }

        private void txtSearch_TextChanged(object sender, EventArgs e)
        {
            FilterAndDisplayApps();
        }

        private void listBoxApps_DoubleClick(object sender, EventArgs e)
        {
            if (listBoxApps.SelectedItem is AppInfo selectedApp)
            {
                try
                {
                    Process proc = Process.GetProcessById(selectedApp.ProcessId);
                    IntPtr hWnd = proc.MainWindowHandle;

                    if (hWnd != IntPtr.Zero)
                    {
                        // If minimized, restore it first
                        ShowWindow(hWnd, SW_RESTORE);
                        // Bring window to the foreground
                        SetForegroundWindow(hWnd);
                    }
                    else
                    {
                        MessageBox.Show("Could not find a valid window handle for this application.", "Activation Failed", MessageBoxButtons.OK, MessageBoxIcon.Warning);
                    }
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Unable to activate application: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            }
        }
    }
}