export default {
    install: (app, options) => {
        // https://www.gnu.org/software/gettext/manual/gettext.html#Plural-forms
        // http://docs.translatehouse.org/projects/localization-guide/en/latest/l10n/pluralforms.html
        console.log("Installing i18n");
        if (localStorage.getItem('language')) {
            options.language = localStorage.getItem('language');
        }
        else {
            localStorage.setItem('language', 'en');
            options.language = 'en';
        }
        function format(fmt) {
            const args = arguments;
            console.log(args);
            console.log(fmt);
            return fmt
                .replace(/%%/g, '%% ')
                .replace(/%(\d+)/g, function (str, p1) {
                    return args[p1];
                })
                .replace(/%% /g, '%')
        }
        function gettext(msgid) {
            const args = arguments;
            console.log(options)
            // get the string from the translation and format
            let lang = options.language;
            if (options.translations[lang]) {
                if (options.translations[lang][msgid] && options.translations[lang][msgid].msgstr) {
                    console.log("Found translation");
                    args[0] = options.translations[lang][msgid].msgstr;
                }
            }
            return format(...args)
        }
        function ngettext(msgid, msgid_plural, n) {
            const args = arguments;
            // not implemented yet.
        }
        function setlanguage(lang) {
            options.language = lang;
            console.log(`Setting language to ${lang}`);
            localStorage.setItem('language', lang);
            return getlanguage();
        }
        function getlanguage() {
            return options.language;
        }
        app.config.globalProperties.$gettext = gettext;
        app.config.globalProperties.$ngettext = ngettext;
        app.config.globalProperties.$setlanguage = setlanguage;
        app.config.globalProperties.$getlanguage = getlanguage;
    }
}
