using System.Collections.Generic;

namespace MultiLocker.Gui
{
    public static class Localization
    {
        static Dictionary<string, Dictionary<string, string>> dict = new()
        {
            ["ru"] = new() {
                ["info"] = "Учебный киоск-режим. Введите пароль для выхода.",
                ["unlock_button"] = "Выйти"
            },
            ["en"] = new() {
                ["info"] = "Demo kiosk mode. Enter password to unlock.",
                ["unlock_button"] = "Unlock"
            }
        };

        static string lang = "ru";
        public static void SetLang(string l) { if (dict.ContainsKey(l)) lang = l; }
        public static string T(string key) => dict.ContainsKey(lang) && dict[lang].ContainsKey(key) ? dict[lang][key] : key;
    }
}
