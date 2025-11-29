using System;
using System.Collections.Generic;
using System.Linq;

namespace MultiLocker.Gui
{
    public class LockManager
    {
        readonly Options _opts;
        readonly NamedPipeServer _pipe;
        readonly List<LockerForm> _forms = new();

        int _failed = 0;
        DateTime? _lockoutUntil = null;
        readonly object _sync = new();

        public LockManager(Options opts, NamedPipeServer pipe)
        {
            _opts = opts;
            _pipe = pipe;
            _pipe.OnUnlockRequest += HandlePipeUnlock;
        }

        public void RegisterForm(LockerForm f) { lock (_sync) { _forms.Add(f); } }

        public void EnterGlobalLock()
        {
            Logger.LogInfo("EnterGlobalLock called");
            lock (_sync)
            {
                foreach (var f in _forms) f.EnterLockMode();
            }
        }

        public bool TryUnlock(string attemptPlain)
        {
            lock (_sync)
            {
                if (_lockoutUntil.HasValue && _lockoutUntil.Value > DateTime.UtcNow)
                {
                    Logger.LogWarn("Unlock attempt during lockout");
                    return false;
                }

                if (Utils.Verify(attemptPlain, _opts.PasswordHash))
                {
                    Logger.LogEvent("unlock_success");
                    foreach (var f in _forms.ToList()) f.RequestExit();
                    return true;
                }
                else
                {
                    _failed++;
                    Logger.LogEvent("unlock_failed", new { failed = _failed });
                    if (_failed >= _opts.MaxAttempts)
                    {
                        _lockoutUntil = DateTime.UtcNow.AddSeconds(_opts.LockoutSeconds);
                        _failed = 0;
                        foreach (var f in _forms) f.NotifyLockout(_lockoutUntil.Value);
                        Logger.LogWarn($"Global lockout until {_lockoutUntil.Value:O}");
                    }
                    return false;
                }
            }
        }

        void HandlePipeUnlock(string token)
        {
            Logger.LogInfo("Pipe unlock requested");
            _ = System.Threading.Tasks.Task.Run(() =>
            {
                var ok = TryUnlock(token);
                Logger.LogInfo("Pipe unlock result: " + ok);
            });
        }
    }
}
