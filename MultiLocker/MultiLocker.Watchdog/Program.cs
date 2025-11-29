using System;
using System.Diagnostics;
using System.Linq;
using System.Threading;

namespace MultiLocker.Watchdog
{
    internal class Program
    {
        static int Main(string[] args)
        {
            var exe = args.Length > 0 ? args[0] : "MultiLocker.Gui.exe";
            var exeName = System.IO.Path.GetFileNameWithoutExtension(exe);
            while (true)
            {
                try
                {
                    var p = Process.GetProcessesByName(exeName).FirstOrDefault();
                    if (p == null)
                    {
                        Console.WriteLine($"{DateTime.Now}: Starting {exe} ...");
                        try { Process.Start(exe); }
                        catch (Exception ex) { Console.WriteLine("Start failed: " + ex.Message); }
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine("Watchdog error: " + ex.Message);
                }
                Thread.Sleep(3000);
            }
        }
    }
}
