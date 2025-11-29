using System;
using System.Collections.Concurrent;
using System.IO;
using System.Text.Json;
using System.Threading;

namespace MultiLocker.Gui
{
    public static class Logger
    {
        static string _path = Path.Combine(Path.GetTempPath(), "winlocker_log.json");
        static BlockingCollection<LogEntry> _queue = new();
        static Thread? _worker;

        public static void Init(string path)
        {
            _path = path;
            _worker = new Thread(Worker) { IsBackground = true };
            _worker.Start();
            LogInfo($"Logger initialized to {_path}");
        }

        public static void LogInfo(string message) => Enqueue("info", message);
        public static void LogWarn(string message) => Enqueue("warn", message);
        public static void LogError(string message) => Enqueue("error", message);
        public static void LogEvent(string evt, object? payload = null) => Enqueue("event", $"{evt} {JsonSerializer.Serialize(payload)}");

        static void Enqueue(string level, string message)
        {
            _queue.Add(new LogEntry { Timestamp = DateTime.UtcNow, Level = level, Message = message });
        }

        static void Worker()
        {
            try
            {
                using var fs = new FileStream(_path, FileMode.Append, FileAccess.Write, FileShare.Read);
                using var sw = new StreamWriter(fs);
                foreach (var e in _queue.GetConsumingEnumerable())
                {
                    var line = JsonSerializer.Serialize(e);
                    sw.WriteLine(line);
                    sw.Flush();
                }
            }
            catch
            {
                // best-effort
            }
        }

        public record LogEntry
        {
            public DateTime Timestamp { get; init; }
            public string Level { get; init; } = "";
            public string Message { get; init; } = "";
        }
    }
}
