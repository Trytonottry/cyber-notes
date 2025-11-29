using System;
using System.Diagnostics;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace MultiLocker.Gui
{
    public partial class LockerForm : Form
    {
        readonly LockManager _manager;
        readonly Screen _screen;
        readonly Options _options;
        bool _isExiting = false;
        DateTime? _lockoutUntil = null;

        // Hook
        private const int WH_KEYBOARD_LL = 13;
        private static IntPtr _hook = IntPtr.Zero;
        private delegate IntPtr LLKPROC(int nCode, IntPtr wParam, IntPtr lParam);
        private LLKPROC _proc;

        // VK
        private const int VK_LWIN = 0x5B, VK_RWIN = 0x5C, VK_TAB = 0x09, VK_F4 = 0x73, VK_ESCAPE = 0x1B;
        private const int VK_CONTROL = 0x11, VK_SHIFT = 0x10;

        // secret combo
        bool ctrlDown = false, shiftDown = false;

        // UI
        Label _info; TextBox _pwd; Button _btn; Label _attempts;

        public LockerForm(LockManager manager, Screen screen, Options options)
        {
            _manager = manager;
            _screen = screen;
            _options = options;
            InitializeComponent();
            _manager.RegisterForm(this);
            BuildUI();
            PositionOnScreen();

            _proc = HookCallback;
            _hook = SetWindowsHookEx(WH_KEYBOARD_LL, _proc, GetModuleHandle(Process.GetCurrentProcess().MainModule.ModuleName), 0);

            this.Load += (s, e) => EnterLockMode();
            this.Activated += (s, e) => { BringToFront(); };
            this.Deactivate += (s, e) => { TopMost = true; BringToFront(); };
        }

        void BuildUI()
        {
            FormBorderStyle = FormBorderStyle.None;
            StartPosition = FormStartPosition.Manual;
            BackColor = Color.FromArgb(18, 18, 18);
            ForeColor = Color.White;

            _info = new Label
            {
                Text = Localization.T("info"),
                AutoSize = false,
                Dock = DockStyle.Top,
                Height = 120,
                TextAlign = ContentAlignment.MiddleCenter,
                Font = new Font("Segoe UI", 20)
            };

            _pwd = new TextBox { Left = 20, Top = 140, Width = 360, UseSystemPasswordChar = true };
            _btn = new Button { Text = Localization.T("unlock_button"), Left = 400, Top = 138 };
            _attempts = new Label { Text = "", Left = 20, Top = 180, AutoSize = true, ForeColor = Color.LightGray };

            _btn.Click += Btn_Click;
            Controls.Add(_info); Controls.Add(_pwd); Controls.Add(_btn); Controls.Add(_attempts);
            this.FormClosing += LockerForm_FormClosing;
        }

        private void PositionOnScreen()
        {
            var b = _screen.Bounds;
            Left = b.Left; Top = b.Top; Width = b.Width; Height = b.Height;
            TopMost = true;
        }

        public void EnterLockMode()
        {
            var rect = new RECT { left = _screen.Bounds.Left, top = _screen.Bounds.Top, right = _screen.Bounds.Right, bottom = _screen.Bounds.Bottom };
            ClipCursor(ref rect);
            Logger.LogInfo($"Lock entered on {_screen.DeviceName}");
        }

        private void Btn_Click(object? s, EventArgs e)
        {
            if (_lockoutUntil.HasValue && _lockoutUntil.Value > DateTime.UtcNow)
            {
                MessageBox.Show($"Lockout until {_lockoutUntil.Value.ToLocalTime():T}");
                return;
            }
            var txt = _pwd.Text ?? "";
            var ok = _manager.TryUnlock(txt);
            if (!ok) UpdateAttemptsUI();
        }

        public void NotifyLockout(DateTime until)
        {
            _lockoutUntil = until;
            UpdateAttemptsUI();
        }

        void UpdateAttemptsUI()
        {
            if (_lockoutUntil.HasValue && _lockoutUntil.Value > DateTime.UtcNow)
            {
                var rem = _lockoutUntil.Value - DateTime.UtcNow;
                _attempts.Text = $"Lockout: {rem.Minutes:D2}:{rem.Seconds:D2}";
                Task.Run(async () =>
                {
                    while (_lockoutUntil.HasValue && _lockoutUntil.Value > DateTime.UtcNow)
                    {
                        await Task.Delay(800);
                        try
                        {
                            Invoke(new Action(() =>
                            {
                                var r = _lockoutUntil.Value - DateTime.UtcNow;
                                _attempts.Text = $"Lockout: {r.Minutes:D2}:{r.Seconds:D2}";
                            }));
                        }
                        catch { break; }
                    }
                    try { Invoke(new Action(() => _attempts.Text = "")); } catch { }
                });
            }
            else
            {
                _attempts.Text = "";
            }
        }

        public void RequestExit()
        {
            Logger.LogInfo("RequestExit called on form");
            CleanupAndClose();
        }

        private void CleanupAndClose()
        {
            try { UnhookWindowsHookEx(_hook); ClipCursor(IntPtr.Zero); } catch { }
            _isExiting = true;
            try { Invoke(new Action(() => { Close(); })); } catch { }
        }

        private void LockerForm_FormClosing(object sender, FormClosingEventArgs e)
        {
            if (!_isExiting) e.Cancel = true;
        }

        // ---------------- Hook ----------------
        private IntPtr HookCallback(int nCode, IntPtr wParam, IntPtr lParam)
        {
            if (nCode >= 0)
            {
                int vk = Marshal.ReadInt32(lParam);

                // Block Win keys
                if (vk == VK_LWIN || vk == VK_RWIN) { Logger.LogEvent("blocked_key", vk); return (IntPtr)1; }

                // Block Alt+Tab
                if (vk == VK_TAB && (GetKeyState(0x12) & 0x8000) != 0) { Logger.LogEvent("blocked_alt_tab"); return (IntPtr)1; }

                // Block Alt+F4
                if (vk == VK_F4 && (GetKeyState(0x12) & 0x8000) != 0) { Logger.LogEvent("blocked_alt_f4"); return (IntPtr)1; }

                // Secret combo detection
                if (vk == VK_CONTROL) ctrlDown = true;
                if (vk == VK_SHIFT) shiftDown = true;
                if (vk == (int)Keys.U && ctrlDown && shiftDown)
                {
                    Logger.LogEvent("secret_combo");
                    Invoke(new Action(() =>
                    {
                        var ok = _manager.TryUnlock(_pwd.Text ?? "");
                        if (!ok) UpdateAttemptsUI();
                    }));
                    return (IntPtr)1;
                }
            }
            return CallNextHookEx(_hook, nCode, wParam, lParam);
        }

        protected override void OnKeyUp(KeyEventArgs e)
        {
            base.OnKeyUp(e);
            if (e.KeyCode == Keys.ControlKey) ctrlDown = false;
            if (e.KeyCode == Keys.ShiftKey) shiftDown = false;
        }

        #region PInvoke
        [DllImport("user32.dll")] static extern IntPtr SetWindowsHookEx(int idHook, Delegate lpfn, IntPtr hMod, uint dwThreadId);
        [DllImport("user32.dll")] static extern bool UnhookWindowsHookEx(IntPtr hhk);
        [DllImport("user32.dll")] static extern IntPtr CallNextHookEx(IntPtr hhk, int nCode, IntPtr wParam, IntPtr lParam);
        [DllImport("kernel32.dll", CharSet = CharSet.Auto)] static extern IntPtr GetModuleHandle(string lpModuleName);
        [DllImport("user32.dll")] static extern short GetKeyState(int nVirtKey);
        [DllImport("user32.dll")] static extern bool ClipCursor(ref RECT rect);
        [DllImport("user32.dll")] static extern bool ClipCursor(IntPtr lpRect);

        [StructLayout(LayoutKind.Sequential)]
        public struct RECT { public int left, top, right, bottom; }
        #endregion
    }
}
