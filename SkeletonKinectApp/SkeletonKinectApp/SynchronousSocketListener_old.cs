using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

public class SynchronousSocketListener_old
{
	public Socket socket { get; set; }
	public dynamic msgToSend { get; set; }

	private readonly IPEndPoint localEndPoint = null;

	public SynchronousSocketListener_old(int port)
	{
		IPHostEntry ipHostInfo = Dns.GetHostEntry(Dns.GetHostName());
		IPAddress ipAddress = ipHostInfo.AddressList[3];
		this.localEndPoint = new IPEndPoint(ipAddress, port);

		// Create a TCP/IP socket.  
		this.socket = new Socket(ipAddress.AddressFamily,
			SocketType.Stream, ProtocolType.Tcp);
	}

	public void StartListening()
	{
		// Data buffer for incoming data.  
		byte[] bytes = new Byte[1024];

		// Bind the socket to the local endpoint and   
		// listen for incoming connections.  
		try
		{
			socket.Bind(localEndPoint);
			socket.Listen(10);

			// Start listening for connections.  
			while (true)
			{
				Socket handler = socket.Accept();

				byte[] msg = Encoding.ASCII.GetBytes(this.msgToSend);

				handler.Send(msg);
				handler.Shutdown(SocketShutdown.Both);
				handler.Close();
			}

		}
		catch (Exception e)
		{
			Console.WriteLine(e.ToString());
		}
	}
}