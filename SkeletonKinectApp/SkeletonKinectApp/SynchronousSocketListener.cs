﻿using Newtonsoft.Json;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class SynchronousSocketListener
{
	private static int port { get; set; }
	public static Socket socket { get; set; }
	public static dynamic msgToSend { get; set; }

	private static IPEndPoint localEndPoint = null;

	public SynchronousSocketListener(int port)
	{
		IPHostEntry ipHostInfo = Dns.GetHostEntry(Dns.GetHostName());
		IPAddress ipAddress = ipHostInfo.AddressList[3];
		localEndPoint = new IPEndPoint(ipAddress, port);

		// Create a TCP/IP socket.  
		socket = new Socket(ipAddress.AddressFamily,
			SocketType.Stream, ProtocolType.Tcp);
	}

	public static void StartListening()
	{
		try
		{
			socket.Bind(localEndPoint);
			socket.Listen(10);

			WaitRequest();
		}
		catch (Exception) { }
	}

	public static void WaitRequest()
	{
		socket.BeginAccept(
					new AsyncCallback(AcceptCallback),
					socket);
	}

	public static void AcceptCallback(IAsyncResult ar)
	{
		// Get the socket that handles the client request.  
		Socket listener = (Socket)ar.AsyncState;
		Socket handler = listener.EndAccept(ar);
		Send(handler);
	}

	private static void Send(Socket handler)
	{
		try
		{
			while(true)
			{
				if (msgToSend == null)
				{
					msgToSend = "None"; // "There might be no bodies in a front of the kinect.";
				}
				string jsonData = JsonConvert.SerializeObject(msgToSend);
				byte[] byteData = Encoding.ASCII.GetBytes(jsonData);

				// Begin sending the data to the remote device.  
				handler.BeginSend(byteData, 0, byteData.Length, 0,
					new AsyncCallback(SendCallback), handler);

				Thread.Sleep(2000);
			}
		}
		catch (Exception)
		{
			WaitRequest();
		}
	}

	private static void SendCallback(IAsyncResult ar)
	{
		try
		{
			// Retrieve the socket from the state object.  
			Socket handler = (Socket)ar.AsyncState;

			// Complete sending the data to the remote device.  
			int bytesSent = handler.EndSend(ar);
		}
		catch (Exception)
		{
			WaitRequest();
		}
	}

	private static void CloseAll()
	{
		socket.Shutdown(SocketShutdown.Both);
		socket.Close();
	}
}