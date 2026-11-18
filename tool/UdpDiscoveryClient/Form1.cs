using System;
using System.Net;
using System.Net.Sockets;
using System.Net.NetworkInformation;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace UdpDiscoveryClient
{
    public partial class Form1 : Form
    {
        private UdpClient udpClient;
        private const int PORT = 8842;

        private Button btnDiscover;
        private ListBox listBox;
        private ComboBox comboInterfaces;

        public Form1()
        {
            InitializeComponent();
            InitUI();
            LoadInterfaces();
        }

        private void InitUI()
        {
            this.Text = "UDP Device Discovery";
            this.Width = 600;
            this.Height = 400;

            btnDiscover = new Button();
            btnDiscover.Text = "Discover Devices";
            btnDiscover.Top = 10;
            btnDiscover.Left = 10;
            btnDiscover.Click += BtnDiscover_Click;
            this.Controls.Add(btnDiscover);

            comboInterfaces = new ComboBox();
            comboInterfaces.Top = 10;
            comboInterfaces.Left = 150;
            comboInterfaces.Width = 420;
            this.Controls.Add(comboInterfaces);

            listBox = new ListBox();
            listBox.Top = 50;
            listBox.Left = 10;
            listBox.Width = 560;
            listBox.Height = 300;
            this.Controls.Add(listBox);
        }

        private void LoadInterfaces()
        {
            comboInterfaces.Items.Clear();

            foreach (var ni in NetworkInterface.GetAllNetworkInterfaces())
            {
                if (ni.OperationalStatus != OperationalStatus.Up)
                    continue;

                if (ni.NetworkInterfaceType == NetworkInterfaceType.Loopback)
                    continue;

                var ipProps = ni.GetIPProperties();

                foreach (var addr in ipProps.UnicastAddresses)
                {
                    if (addr.Address.AddressFamily == AddressFamily.InterNetwork)
                    {
                        comboInterfaces.Items.Add(new InterfaceItem
                        {
                            Name = $"{ni.Name} - {addr.Address}",
                            IP = addr.Address,
                            Mask = addr.IPv4Mask
                        });
                    }
                }
            }

            if (comboInterfaces.Items.Count > 0)
                comboInterfaces.SelectedIndex = 0;
        }

        class InterfaceItem
        {
            public string Name;
            public IPAddress IP;
            public IPAddress Mask;

            public override string ToString() => Name;
        }

        private IPAddress GetBroadcast(IPAddress ip, IPAddress mask)
        {
            byte[] ipBytes = ip.GetAddressBytes();
            byte[] maskBytes = mask.GetAddressBytes();
            byte[] broadcast = new byte[4];

            for (int i = 0; i < 4; i++)
            {
                broadcast[i] = (byte)(ipBytes[i] | (~maskBytes[i]));
            }

            return new IPAddress(broadcast);
        }

        private async void BtnDiscover_Click(object sender, EventArgs e)
        {
            listBox.Items.Clear();

            var selected = comboInterfaces.SelectedItem as InterfaceItem;
            if (selected == null)
                return;

            try
            {
                udpClient?.Close();

                udpClient = new UdpClient();
                udpClient.EnableBroadcast = true;

                // Bind to selected interface
                udpClient.Client.Bind(new IPEndPoint(selected.IP, 0));

                IPAddress broadcastIP = GetBroadcast(selected.IP, selected.Mask);
                var broadcastEP = new IPEndPoint(broadcastIP, PORT);

                // byte[] data = Encoding.UTF8.GetBytes("DISCOVER");
				byte[] data = Encoding.ASCII.GetBytes("!@#$\0");
                await udpClient.SendAsync(data, data.Length, broadcastEP);

                listBox.Items.Add($"Using Interface: {selected.IP}");
                listBox.Items.Add($"Broadcast Address: {broadcastIP}");
                listBox.Items.Add("Waiting for responses...\n");

                _ = ReceiveResponses();
            }
            catch (Exception ex)
            {
                listBox.Items.Add("Error: " + ex.Message);
            }
        }

        private async Task ReceiveResponses()
        {
            try
            {
                while (true)
                {
                    var result = await udpClient.ReceiveAsync();

                    string msg = Encoding.UTF8.GetString(result.Buffer);

                    string display = $"{result.RemoteEndPoint.Address} -> {msg}";

                    this.Invoke(new Action(() =>
                    {
                        listBox.Items.Add(display);
                    }));
                }
            }
            catch (ObjectDisposedException)
            {
                // socket closed
            }
			catch (SocketException ex)
			{
				this.Invoke(new Action(() =>
				{
					listBox.Items.Add("Socket closed: " + ex.Message);
				}));
			}
            catch (Exception ex)
            {
                this.Invoke(new Action(() =>
                {
                    listBox.Items.Add("Error: " + ex.Message);
                }));
            }
        }
    }
}