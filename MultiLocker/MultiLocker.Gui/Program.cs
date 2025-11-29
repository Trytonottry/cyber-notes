using System;
using System.Linq;
using System.Threading;
using System.Windows.Forms;

namespace MultiLocker.Gui
{
    internal static class Program
    {
        [STAThread]
        static void Main(string[] args)
        {
            ApplicationConfiguration.Initialize();

            var options = new Options(args);

            Logger.Init(options.LogPath);
            Logger.LogInfo($"Starting MultiLocker v1 — args: {string.Join(' ', args)}");

            var pipeServer = new NamedPipeServer(options);
            pipeServer.Start();

            var manager = new LockManager(options, pipeServer);

            // Set language if provided
            Localization.SetLang(options.Lang);

            // Create and show forms for each screen
            var screens = Screen.AllScreens;
            foreach (var s in screens)
            {
                var f = new LockerForm(manager, s, options);
                f.Show();
            }

            if (options.AutoLockSeconds > 0)
            {
                var t = new System.Threading.Timer(_ => { manager.EnterGlobalLock(); }, null, options.AutoLockSeconds * 1000, Timeout.Infinite);
            }

            Application.Run();

            pipeServer.Stop();
            Logger.LogInfo("MultiLocker exiting");
        }
    }
}
