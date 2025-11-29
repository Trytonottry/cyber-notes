using System;
using System.Security.Cryptography;
using System.Text;

namespace MultiLocker.Gui
{
    public static class Utils
    {
        public static string Hash(string s)
        {
            using var sha = SHA256.Create();
            var b = Encoding.UTF8.GetBytes(s);
            var h = sha.ComputeHash(b);
            return Convert.ToBase64String(h);
        }

        public static bool Verify(string plain, string hash)
        {
            return Hash(plain) == hash;
        }
    }
}
