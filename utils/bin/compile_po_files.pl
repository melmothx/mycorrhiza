#!/usr/bin/env perl

use utf8;
use strict;
use warnings;
use Locale::PO;
use Path::Tiny;
use JSON::MaybeXS;

my ($dir, $outfile) = @ARGV;
die "Usage $0 I18N-directory JSON-OUTPUT-FILE" unless $dir && $outfile;
my %all;
foreach my $f (path($dir)->children(qr{\.po$})) {
    print "$f\n";
    my $locale = $f->basename('.po');
    my $pos = Locale::PO->load_file_asarray("$f", "utf8");
    my %translations;
    foreach my $po (@$pos) {
        if (my $msgid = $po->dequote($po->msgid)) {
            if (my $msgstr= $po->dequote($po->msgstr)) {
                $translations{$msgid} ||= {
                                           # msgid => $msgid,
                                           msgstr => $msgstr,
                                           $po->msgid_plural
                                           ? (msgid_plural => $po->dequote($po->msgid_plural))
                                           : ()
                                          };
            }
            if (my $plurals = $po->msgstr_n) {
                foreach my $k (keys %$plurals) {
                    $translations{$msgid}{plurals} ||= {};
                    $translations{$msgid}{plurals}{$k} = $po->dequote($plurals->{$k});
                }
            }
        }
    }
    $all{$locale} = \%translations;
}

path($outfile)->spew_raw(JSON::MaybeXS->new(utf8 => 1,
                                            pretty => 1,
                                            canonical => 1)->encode(\%all));
