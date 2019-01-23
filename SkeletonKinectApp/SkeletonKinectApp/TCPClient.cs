using System;
using System.Net.Sockets;
using System.Configuration;

public class TCPClient
{
	Int32 port = int.Parse(ConfigurationManager.AppSettings["portClient"]);
	String address = ConfigurationManager.AppSettings["ipClient"];
	TcpClient client = null;
	Byte[] data = new Byte[256];
	String responseData = String.Empty;
	NetworkStream stream = null;
	public string error = null;

	public TCPClient()
	{
		try
		{
			this.client = new TcpClient(address, port);
			this.stream = client.GetStream();
			this.Connect();
		}
		catch (Exception e)
		{
			this.error = e.Message;
		}
	}

	public void Connect()
	{
		try
		{
			if (this.client != null && this.stream != null)
			{
				// Create a TcpClient.
				// Note, for this client to work you need to have a TcpServer 
				// connected to the same address as specified by the server, port
				// combination.

				string manifest = "";

				// wait hello
				data = new Byte[256];
				Int32 bytes = stream.Read(data, 0, data.Length);
				responseData = System.Text.Encoding.ASCII.GetString(data, 0, bytes);

				// send manifest
				try
				{
					manifest = System.IO.File.ReadAllText("manifest.json");
					data = System.Text.Encoding.ASCII.GetBytes(manifest);
					stream.Write(data, 0, data.Length);
				}
				catch (Exception ex)
				{
					throw new Exception(ex.Message);
				}

				// wait hello
				data = new Byte[256];
				bytes = stream.Read(data, 0, data.Length);
				responseData = System.Text.Encoding.ASCII.GetString(data, 0, bytes);
			}
		}
		catch (ArgumentNullException e)
		{
			throw new Exception(e.Message);
		}
		catch (SocketException e)
		{
			throw new Exception(e.Message);
		}
	}

	public void Close ()
	{
		if (this.client != null && this.stream != null)
		{
			stream.Close();
			client.Close();
		}
	}
}