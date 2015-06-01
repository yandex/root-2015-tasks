using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using Catalogizer.Core;
using dnAnalytics.Math;

public delegate void TCPClientHandler(TcpClient client);

public class TCPServer {
    private TcpListener server;

    public TCPServer(int port) {
        this.server = new TcpListener(IPAddress.Any, port);
    }

    public void Do(TCPClientHandler handler) {
        this.server.Start();
        while (true) {
            try {
                handler(this.server.AcceptTcpClient());
            }
            catch {
                Console.WriteLine(":(");
            }
        }
    }

    ~TCPServer() {
        if (this.server != null)
            this.server.Stop();
    }
}

public class MainClass {
    delegate void ProcessCommand(string param, StreamWriter writer);

    private static void CatFile(string param, StreamWriter writer) {
        writer.WriteLine(System.IO.File.ReadAllText(param));
    }

    private static void FileSize(string param, StreamWriter writer) {
        writer.WriteLine(new FileInfo(param).Length.ToString());
    }

    private static void CalcClx(string param, StreamWriter writer) {
        var x = new Complex(param);
        var ans = ComplexMath.Pow(x, x) - x * x + 1;
        writer.WriteLine(ans.ToString());
    }

    private static void GetInfo(string param, StreamWriter writer) {
        writer.WriteLine(DB[param].Name);
    }

    private static void CalcErf(string param, StreamWriter writer) {
        var x = double.Parse(param);
        var ans = SpecialFunctions.Erf(x);
        writer.WriteLine(ans.ToString());
    }

    public static void ClientHandler(TcpClient client) {
        var d = new Dictionary<string, ProcessCommand>() {
            { "cat", CatFile },
            { "clx", CalcClx },
            { "erf", CalcErf },
            { "sz", FileSize },
            { "info", GetInfo }
        };

        while (client.Connected) {
            using (var streamReader = new StreamReader(client.GetStream()))
            using (var streamWriter = new StreamWriter(client.GetStream())) {
                var cmd = streamReader.ReadLine().Split(" ".ToCharArray(), 2);

                try {
                    d[cmd[0]](cmd[1], streamWriter);
                }
                catch {
                    streamWriter.WriteLine("Error :(");
                }
                streamWriter.Flush();
            }
        }
        client.Close();
    }

    private static void Do() {
        var server = new TCPServer(12354);
        server.Do(ClientHandler);
    }

    private static Database DB;

    private static void Prepare() {
        DB = new Database("base.dbx");
        DB.OnEndDatabaseLoad += Do;
        DB.Load();
    }

    public static void Main(string [] args) {
        Prepare();
    }
}
