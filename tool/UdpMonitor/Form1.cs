using System;
using System.Collections.Generic;
using System.Drawing;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Text;
using System.Net.Http;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace UdpMonitor
{
    public partial class Form1 : Form
    {
        private const int PORT = 8842;
        private const string AUTH = "!@#$";

        private ComboBox cmbInterfaces;
        private FlowLayoutPanel devicePanel;
        private TextBox txtLog;

        private UdpClient udpClient;

        private Dictionary<string, DeviceWidget> devices =
            new Dictionary<string, DeviceWidget>();

        private System.Windows.Forms.Timer broadcastTimer;
        private System.Windows.Forms.Timer watchdogTimer;

        public Form1()
        {
            InitializeComponent();

            Width = 1000;
            Height = 700;

            InitUI();

            LoadInterfaces();

            StartReceiver();

            broadcastTimer = new  System.Windows.Forms.Timer();
            broadcastTimer.Interval = 1000;
            broadcastTimer.Tick += BroadcastTimer_Tick;
            broadcastTimer.Start();

            watchdogTimer = new  System.Windows.Forms.Timer();
            watchdogTimer.Interval = 1000;
            watchdogTimer.Tick += WatchdogTimer_Tick;
            watchdogTimer.Start();
        }

        private void InitUI()
        {
            Label lbl = new Label();
            lbl.Text = "Interface:";
            lbl.Left = 10;
            lbl.Top = 15;
            lbl.Width = 80;
            Controls.Add(lbl);

            cmbInterfaces = new ComboBox();
            cmbInterfaces.Left = 100;
            cmbInterfaces.Top = 10;
            cmbInterfaces.Width = 400;
            Controls.Add(cmbInterfaces);

            devicePanel = new FlowLayoutPanel();
            devicePanel.Left = 10;
            devicePanel.Top = 50;
            devicePanel.Width = 950;
            devicePanel.Height = 500;
            devicePanel.AutoScroll = true;
            devicePanel.WrapContents = true;
            devicePanel.FlowDirection = FlowDirection.LeftToRight;
            Controls.Add(devicePanel);

            txtLog = new TextBox();
            txtLog.Left = 10;
            txtLog.Top = 570;
            txtLog.Width = 950;
            txtLog.Height = 80;
            txtLog.Multiline = true;
            txtLog.ScrollBars = ScrollBars.Vertical;
            Controls.Add(txtLog);
        }

        private void Log(string msg)
        {
            txtLog.AppendText(
                $"[{DateTime.Now:HH:mm:ss}] {msg}\r\n");
        }

        private void LoadInterfaces()
        {
            foreach (NetworkInterface ni in
                     NetworkInterface.GetAllNetworkInterfaces())
            {
                if (ni.OperationalStatus != OperationalStatus.Up)
                    continue;

                if (ni.NetworkInterfaceType ==
                    NetworkInterfaceType.Loopback)
                    continue;

                var props = ni.GetIPProperties();

                foreach (var addr in props.UnicastAddresses)
                {
                    if (addr.Address.AddressFamily ==
                        AddressFamily.InterNetwork)
                    {
                        cmbInterfaces.Items.Add(
                            new InterfaceItem
                            {
                                Name = ni.Name,
                                IP = addr.Address,
                                Netmask = addr.IPv4Mask
                            });
                    }
                }
            }

            if (cmbInterfaces.Items.Count > 0)
                cmbInterfaces.SelectedIndex = 0;
        }

        private async void BroadcastTimer_Tick(
            object sender,
            EventArgs e)
        {
            await SendBroadcast();
        }

        private async Task SendBroadcast()
        {
            if (cmbInterfaces.SelectedItem == null)
                return;

            InterfaceItem item =
                (InterfaceItem)cmbInterfaces.SelectedItem;

            try
            {
                udpClient?.Close();

                udpClient = new UdpClient();

                udpClient.EnableBroadcast = true;

                udpClient.Client.Bind(
                    new IPEndPoint(item.IP, 0));

                IPAddress broadcast =
                    GetBroadcast(item.IP, item.Netmask);

                IPEndPoint endpoint =
                    new IPEndPoint(broadcast, PORT);

                byte[] auth =
                    Encoding.ASCII.GetBytes(AUTH);

                byte[] packet = new byte[auth.Length + 1];

                Buffer.BlockCopy(
                    auth,
                    0,
                    packet,
                    0,
                    auth.Length);

                packet[auth.Length] = 0x01;

                await udpClient.SendAsync(
                    packet,
                    packet.Length,
                    endpoint);

               // Log($"Broadcast -> {broadcast}");
            }
            catch (Exception ex)
            {
                Log(ex.Message);
            }
        }

        private async void StartReceiver()
        {
            while (true)
            {
                try
                {
                    if (udpClient == null)
                    {
                        await Task.Delay(100);
                        continue;
                    }

                    var result =
                        await udpClient.ReceiveAsync();

                    string msg =
                        Encoding.UTF8.GetString(result.Buffer);

                    string ip =
                        result.RemoteEndPoint.Address.ToString();

                    ParseDevice(ip, msg);
                }
                catch
                {
                }
            }
        }
        private string convertHostname(string ip)
        {
            string[] parts = ip.Split(".");
            int result = Int32.Parse(parts[3]);
            string Soc_type;
            
            switch (result / 10){
                case 1:
                    Soc_type ="SS";
                    break;
                case 2:
                    Soc_type ="NN";
                    break;
                case 3:
                    Soc_type ="FF";
                    break;
                default:
                    return "Unknown";
            }
            int num = result % 10;
            string hostname = $"{Soc_type}-{num}";
            return hostname;
        }

        private async Task<ShmooStatus>  GetShmooState(string ip){
            string url =
            $"http://{ip}/cgi-bin/GetShmooState.cgi";

            HttpClientHandler handler =
                new HttpClientHandler();

            handler.Credentials =
                new NetworkCredential("admin", "password");

            using (HttpClient client =
                new HttpClient(handler))
            {
                try
                {
                    string response =
                        await client.GetStringAsync(url);
                    ShmooStatus sst = new ShmooStatus();
                    string[] parts = response.Split('&');

                    foreach (string part in parts)
                    {
                        string[] kv=part.Split("=");
                        string key = kv[0];
                        string val = kv[1];
                        switch (key){
                           case "ret":
                                sst.ret = Int32.Parse(val);
                                break; 
                            case "num":
                                sst.num =Int32.Parse(val);
                                break;
                            case "total":
                                sst.total =Int32.Parse(val);
                                break;
                            case "finish":
                                sst.finish =Int32.Parse(val);
                                // Log($"{sst.finish}" );
                                break;
                            case "bst":
                                
                                if (val.Contains("pdds") &&
                                    val.Contains("dds") &&
                                    val.Contains("odt"))
                                {
                                    //string result = "";
                                    string pdds = "";
                                    string dds = "";
                                    string odt = "";
                                    string[] para = val.Split('_');

                                    foreach (string p in para)
                                    {
                                        if (p.StartsWith("pdds")) pdds = p;
                                        else if (p.StartsWith("dds")) dds = p;
                                        else if (p.StartsWith("odt")) odt = p;
                                         
                                    }
                                    if (pdds != "" && dds != "" && odt != "")
                                    {
                                        string r_str = $"{pdds}_{dds}_{odt}";
                                        Log(r_str);
                                        sst.bst = r_str;
                                    }
                                    
                                    sst.rw = "w";
                                }
                                else if (val.Contains("term") && val.Contains("ds")) {
                                     //string result = "";
                                    string term = "";
                                    string ds = "";
                                    // string odt = "";
                                    string[] para = val.Split('_');

                                    foreach (string p in para)
                                    {
                                        if (p.StartsWith("term")) term = p;
                                        else if (p.StartsWith("ds")) ds = p;
                                        // else if (p.StartsWith("odt")) odt = p;
                                         
                                    }
                                    if (term != "" && ds != "")
                                    {
                                        string r_str = $"{term}_{ds}";
                                         Log(r_str);
                                        sst.bst = r_str;
                                    }
                                    sst.rw = "r";
                                }
                                
                                break;
                            default:
                                Console.WriteLine($"{val}");
                                break;

                        }
                
                        
                    }
                    return sst;
                }
                catch (Exception ex)
                {
                    Log(ex.Message);
                }
            }
            return null;
        }
        private async Task UpdateShmooState(
            DeviceWidget dev)
        {
            try
            {
               
                    ShmooStatus resp = await GetShmooState(dev.LblIp.Text);
                    if (resp !=null )  
                        dev.LblProgress.Text = $"{resp.num} / {resp.total} ({resp.finish})\r{resp.bst} ({resp.rw})";
                        // dev.LblProgress.Text = $"{resp.bst} ({resp.rw})";
                // Log($"{dev.LblIp.Text}:{dev.LblTemp.Text}");
            }
            catch (Exception ex)
            {
                Log(ex.Message);
            }
        }
        private void ParseDevice(string ip, string msg)
        {
            if (!devices.ContainsKey(ip))
            {
                DeviceWidget widget = new DeviceWidget();

                widget.Width = 300;
                widget.Height =180;
                widget.BorderStyle = BorderStyle.FixedSingle;

                widget.LblIp = new Label();
                widget.LblIp.Left = 10;
                widget.LblIp.Top = 10;
                widget.LblIp.Width = 130;

                widget.Controls.Add(widget.LblIp);

                widget.LblHostname = new Label();
                widget.LblHostname.Left = 140;
                widget.LblHostname.Top = 10;
                widget.LblHostname.Width = 80;

                widget.Controls.Add(widget.LblHostname);

                widget.Status = new Panel();
                widget.Status.Left = 10;
                widget.Status.Top = 40;
                widget.Status.Width = 30;
                widget.Status.Height = 30;
                widget.Status.BackColor = Color.Red;

                widget.Controls.Add(widget.Status);

                widget.LblAlive = new Label();
                widget.LblAlive.Left = 50;
                widget.LblAlive.Top = 45;
                widget.LblAlive.Width = 150;

                widget.Controls.Add(widget.LblAlive);

                widget.LblTemp = new Label();
                widget.LblTemp.Left = 220;
                widget.LblTemp.Top = 45;
                widget.LblTemp.Width = 50;
                // widget.LblTemp.Text = "N/A";
                widget.Controls.Add(widget.LblTemp);


                widget.LblProgress = new Label();
                widget.LblProgress.Left = 50;
                widget.LblProgress.Top = 65;
                widget.LblProgress.Width = 300;
                 widget.LblProgress.Height = 60;
                // widget.LblTemp.Text = "N/A";
                widget.Controls.Add(widget.LblProgress);


                devices[ip] = widget;

                devicePanel.Controls.Add(widget);
            }

            DeviceWidget dev = devices[ip];

            dev.LblIp.Text = ip;
            dev.LblAlive.Text =
                DateTime.Now.ToString("HH:mm:ss");
            string hostname = convertHostname(ip);
            dev.LblHostname.Text = $"({hostname})"; 

            dev.LastAlive = DateTime.Now;

            dev.Status.BackColor = Color.LimeGreen;
            UpdateShmooState(dev);
        }

        private async Task<string>  GetTemprature(string ip){
            string url =
            $"http://{ip}/cgi-bin/GetTemprature.cgi";

            HttpClientHandler handler =
                new HttpClientHandler();

            handler.Credentials =
                new NetworkCredential("admin", "password");

            using (HttpClient client =
                new HttpClient(handler))
            {
                try
                {
                    string response =
                        await client.GetStringAsync(url);

                    string[] parts = response.Split('&');

                    foreach (string part in parts)
                    {
                        if (part.StartsWith("temp0="))
                        {
                            string temp0 = part.Substring(6);

                            return temp0;
                        }
                    }
                }
                catch (Exception ex)
                {
                    Log(ex.Message);
                }
            }
            return "";
        }
        private async Task UpdateTemperature(
            DeviceWidget dev)
        {
            try
            {
               
                    string Celsius_val = await GetTemprature(dev.LblIp.Text);
                     dev.LblTemp.Text = ($"{Celsius_val}\u00B0C");
                // Log($"{dev.LblIp.Text}:{dev.LblTemp.Text}");
            }
            catch (Exception ex)
            {
                Log(ex.Message);
            }
        }
        private  void WatchdogTimer_Tick(
            object sender,
            EventArgs e)
        {
            foreach (var dev in devices.Values)
            {
                TimeSpan diff =
                    DateTime.Now - dev.LastAlive;

                if (diff.TotalSeconds > 5)
                {
                    dev.Status.BackColor = Color.Red;
                } 
                if (dev.Status.BackColor == Color.LimeGreen ) {
                    // dev.LblTemp.Text=
                        // await GetTemprature(dev.LblIp.Text);
                    // Console.WriteLine($"{dev.LblTemp.Text}");
                     _ = UpdateTemperature(dev); 
                }
                if ( diff.TotalSeconds > 300) {
                    Log($"{dev.LblIp.Text} Power Recycle Recovery");
                }
            }
        }

        private IPAddress GetBroadcast(
            IPAddress ip,
            IPAddress mask)
        {
            byte[] ipBytes = ip.GetAddressBytes();
            byte[] maskBytes = mask.GetAddressBytes();

            byte[] broadcast = new byte[4];

            for (int i = 0; i < 4; i++)
            {
                broadcast[i] =
                    (byte)(ipBytes[i] | (~maskBytes[i]));
            }

            return new IPAddress(broadcast);
        }

        public class DeviceWidget : Panel
        {
            public Label LblAlive;
            public Label LblIp;
            public Label LblProgress;
            public Label LblTemp;
            public Label LblHostname;
            public Panel Status;
            public DateTime LastAlive;
        }
        
        public class ShmooStatus{
            public int ret;
            public int num;
            public int total;
            public string bst;
            public string rw;
            public int finish;
        }

        public class InterfaceItem
        {
            public string Name;
            public IPAddress IP;
            public IPAddress Netmask;

            public override string ToString()
            {
                return $"{Name} ({IP})";
            }
        }
    }
}