using System;
using System.IO;
using System.IO.Pipes;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

namespace MultiLocker.Gui
{
    // Формат команд: "UNLOCK <plainPassword>"
    public class NamedPipeServer
    {
        readonly Options _opts;
        bool _running = false;
        CancellationTokenSource? _cts;

        public event Action<string>? OnUnlockRequest;

        public NamedPipeServer(Options opts) => _opts = opts;

        public void Start()
        {
            _cts = new CancellationTokenSource();
            _running = true;
            Task.Run(() => Loop(_cts.Token));
            Logger.LogInfo("NamedPipeServer started");
        }

        public void Stop()
        {
            _cts?.Cancel();
            _running = false;
            Logger.LogInfo("NamedPipeServer stopped");
        }

        async Task Loop(CancellationToken ct)
        {
            while (!ct.IsCancellationRequested)
            {
                try
                {
                    using var server = new NamedPipeServerStream("MultiLockerPipe", PipeDirection.InOut, 1, PipeTransmissionMode.Message, PipeOptions.Asynchronous);
                    await server.WaitForConnectionAsync(ct);
                    using var sr = new StreamReader(server, Encoding.UTF8);
                    using var sw = new StreamWriter(server, Encoding.UTF8) { AutoFlush = true };
                    var line = await sr.ReadLineAsync();
                    if (line != null)
                    {
                        Logger.LogInfo($"Pipe received: {line}");
                        if (line.StartsWith("UNLOCK "))
                        {
                            var token = line.Substring("UNLOCK ".Length);
                            OnUnlockRequest?.Invoke(token);
                            await sw.WriteLineAsync("OK");
                        }
                        else await sw.WriteLineAsync("ERR unknown");
                    }
                }
                catch (OperationCanceledException) { break; }
                catch (Exception ex) { Logger.LogError("Pipe loop error: " + ex.Message); await Task.Delay(500); }
            }
        }
    }
}
