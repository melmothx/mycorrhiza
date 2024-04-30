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
        const plural_functions = {
            ach: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            af: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ak: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            am: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            an: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            anp: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ar: function(n) { let plural; let nplurals; nplurals=6; plural=(n==0 ? 0 : n==1 ? 1 : n==2 ? 2 : n%100>=3 && n%100<=10 ? 3 : n%100>=11 ? 4 : 5); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            arn: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            as: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ast: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ay: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            az: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            be: function(n) { let plural; let nplurals; nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            bg: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            bn: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            bo: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            br: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            brx: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            bs: function(n) { let plural; let nplurals; nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ca: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            cgg: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            cs: function(n) { let plural; let nplurals; nplurals=3; plural=(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            csb: function(n) { let plural; let nplurals; nplurals=3; plural=(n==1) ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            cy: function(n) { let plural; let nplurals; nplurals=4; plural=(n==1) ? 0 : (n==2) ? 1 : (n != 8 && n != 11) ? 2 : 3; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            da: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            de: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            doi: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            dz: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            el: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            en: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            eo: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            es: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            es: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            et: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            eu: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            fa: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ff: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            fi: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            fil: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            fo: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            fr: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            fur: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            fy: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ga: function(n) { let plural; let nplurals; nplurals=5; plural=n==1 ? 0 : n==2 ? 1 : (n>2 && n<7) ? 2 :(n>6 && n<11) ? 3 : 4; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            gd: function(n) { let plural; let nplurals; nplurals=4; plural=(n==1 || n==11) ? 0 : (n==2 || n==12) ? 1 : (n > 2 && n < 20) ? 2 : 3; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            gl: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            gu: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            gun: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ha: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            he: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            hi: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            hne: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            hr: function(n) { let plural; let nplurals; nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            hu: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            hy: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ia: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            id: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            is: function(n) { let plural; let nplurals; nplurals=2; plural=(n%10!=1 || n%100==11); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            it: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ja: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            jbo: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            jv: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 0); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ka: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            kk: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            kl: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            km: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            kn: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ko: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ku: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            kw: function(n) { let plural; let nplurals; nplurals=4; plural=(n==1) ? 0 : (n==2) ? 1 : (n == 3) ? 2 : 3; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ky: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            lb: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ln: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            lo: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            lt: function(n) { let plural; let nplurals; nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && (n%100<10 || n%100>=20) ? 1 : 2); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            lv: function(n) { let plural; let nplurals; nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n != 0 ? 1 : 2); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            mai: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            me: function(n) { let plural; let nplurals; nplurals=3; plural=n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            mfe: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            mg: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            mi: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            mk: function(n) { let plural; let nplurals; nplurals=2; plural= n==1 || n%10==1 ? 0 : 1; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ml: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            mn: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            mni: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            mnk: function(n) { let plural; let nplurals; nplurals=3; plural=(n==0 ? 0 : n==1 ? 1 : 2); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            mr: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ms: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            mt: function(n) { let plural; let nplurals; nplurals=4; plural=(n==1 ? 0 : n==0 || ( n%100>1 && n%100<11) ? 1 : (n%100>10 && n%100<20 ) ? 2 : 3); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            my: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            nah: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            nap: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            nb: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ne: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            nl: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            nn: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            no: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            nso: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            oc: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            or: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            pa: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            pap: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            pl: function(n) { let plural; let nplurals; nplurals=3; plural=(n==1 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            pms: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ps: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            pt: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            pt: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            rm: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ro: function(n) { let plural; let nplurals; nplurals=3; plural=(n==1 ? 0 : (n==0 || (n%100 > 0 && n%100 < 20)) ? 1 : 2); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ru: function(n) { let plural; let nplurals; nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            rw: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            sah: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            sat: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            sco: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            sd: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            se: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            si: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            sk: function(n) { let plural; let nplurals; nplurals=3; plural=(n==1) ? 0 : (n>=2 && n<=4) ? 1 : 2; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            sl: function(n) { let plural; let nplurals; nplurals=4; plural=(n%100==1 ? 0 : n%100==2 ? 1 : n%100==3 || n%100==4 ? 2 : 3); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            so: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            son: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            sq: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            sr: function(n) { let plural; let nplurals; nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            su: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            sv: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            sw: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ta: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            te: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            tg: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            th: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ti: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            tk: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            tr: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            tt: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ug: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            uk: function(n) { let plural; let nplurals; nplurals=3; plural=(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<10 || n%100>=20) ? 1 : 2); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            ur: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            uz: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            vi: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            wa: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            wo: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            yo: function(n) { let plural; let nplurals; nplurals=2; plural=(n != 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            zh: function(n) { let plural; let nplurals; nplurals=1; plural=0; return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
            zh: function(n) { let plural; let nplurals; nplurals=2; plural=(n > 1); return { "nplurals": nplurals, "plural": (plural === true ? 1 : plural ? plural : 0)  } },
        };
        function format(fmt) {
            const args = arguments;
            // console.log(args);
            // console.log(fmt);
            if (typeof fmt === 'string' || fmt instanceof String) {
                return fmt
                    .replace(/%%/g, '%% ')
                    .replace(/%(\d+)/g, function (str, p1) {
                        return args[p1];
                    })
                    .replace(/%% /g, '%')
            }
            else {
                return fmt
            }
        }
        function gettext(msgid) {
            const args = arguments;
            if (!(typeof args[0] === 'string' || args[0] instanceof String)) {
                return args[0];
            }
            // console.log(options)
            // get the string from the translation and format
            let lang = options.language;
            let found = false;
            if (options.translations[lang]) {
                if (options.translations[lang][msgid] && options.translations[lang][msgid].msgstr) {
                    // console.log("Found translation");
                    args[0] = options.translations[lang][msgid].msgstr;
                    found = true;
                }
            }
            // special case. We don't want uppercase placeholder to
            // show verbatim. Look in the 'en' language, otherwise return 0.
            // console.log(args[0]);
            if (!found && args[0] && args[0].match(/^[A-Z_]+$/)) {
                lang = 'en';
                if (options.translations[lang] &&
                    options.translations[lang][msgid] &&
                    options.translations[lang][msgid].msgstr) {
                    args[0] = options.translations[lang][msgid].msgstr;
                }
                else {
                    console.log("Missing translation for " + args[0]);
                    return '';
                }
            }
            return format(...args)
        }
        function ngettext(msgid, msgid_plural, n, ...args) {
            console.log("Called ngettext");
            let lang = options.language;
            let msg;
            if (options.translations[lang]) {
                if (options.translations[lang][msgid] && options.translations[lang][msgid].plurals) {
                    let avail_plurals = options.translations[lang][msgid].plurals;
                    if (plural_functions[lang]) {
                        let got_plurals = plural_functions[lang](n);
                        console.log(got_plurals);
                        if (avail_plurals[got_plurals.plural]) {
                            msg = avail_plurals[got_plurals.plural];
                            console.log(`Message is ${msg}`);
                        }
                    }
                }
            }
            if (!msg) {
                if (n && n > 1) {
                    msg = msgid_plural;
                }
                else {
                    msg = msgid;
                }
            }
            return format(msg, ...args);
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
