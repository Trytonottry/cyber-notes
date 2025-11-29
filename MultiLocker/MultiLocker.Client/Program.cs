using System;
using System.IO;
using System.IO.Pipes;
using System.Text;
using System.Threading.Tasks;

namespace MultiLocker.Client
{
    internal class Program
    {
        static async Task<int> Main(string[] args)
        {
            if (args.Length < 1)
            {
                Console.WriteLine("Usage: MultiLocker.Client \"UNLOCK <password>\"");
                return 1;
            }

            var cmd = string.Join(' ', args);
            try
            {
                using var client = new NamedPipeClientStream(".", "MultiLockerPipe", PipeDirection.InOut, PipeOptions.Asynchronous);
                await client.ConnectAsync(2000);
                using var sw = new StreamWriter(client, Encoding.UTF8) { AutoFlush = true };
                using var sr = new StreamReader(client, Encoding.UTF8);
                await sw.WriteLineAsync(cmd);
                var resp = await sr.ReadLineAsync();
                Console.WriteLine("Server: " + resp);
                return 0;
            }
            catch (TimeoutException)
            {
                Console.WriteLine("Timeout connecting to pipe. Is MultiLocker running?");
                return 2;
            }
            catch (Exception ex)
            {
                Console.WriteLine("Error: " + ex.Message);
                return 3;
            }
        }
    }
}
