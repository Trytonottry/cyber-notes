using System;
using System.IO;

namespace MultiLocker.Gui
{
    public class Options
    {
        public string PasswordPlain { get; private set; }
        public string PasswordHash { get; private set; }
        public int MaxAttempts { get; private set; }
        public int LockoutSeconds { get; private set; }
        public int AutoLockSeconds { get; private set; }
        public string Lang { get; private set; }
        public string LogPath { get; private set; }

        public Options(string[] args)
        {
            PasswordPlain = "demo123";
            MaxAttempts = 5;
            LockoutSeconds = 60;
            AutoLockSeconds = 5;
            Lang = "ru";
            LogPath = Path.Combine(Path.GetTempPath(), "winlocker_log.json");

            foreach (var a in args)
            {
                if (a.StartsWith("--pwd=")) PasswordPlain = a.Substring("--pwd=".Length);
                if (a.StartsWith("--maxAttempts=") && int.TryParse(a.Substring("--maxAttempts=".Length), out var ma)) MaxAttempts = ma;
                if (a.StartsWith("--lockoutSeconds=") && int.TryParse(a.Substring("--lockoutSeconds=".Length), out var ls)) LockoutSeconds = ls;
                if (a.StartsWith("--autoLockSeconds=") && int.TryParse(a.Substring("--autoLockSeconds=".Length), out var al)) AutoLockSeconds = al;
                if (a.StartsWith("--lang=")) Lang = a.Substring("--lang=".Length);
                if (a.StartsWith("--log=")) LogPath = a.Substring("--log=".Length);
            }

            PasswordHash = Utils.Hash(PasswordPlain);
        }
    }
}
