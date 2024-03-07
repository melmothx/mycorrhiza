#!/usr/bin/env perl
use strict;
use warnings;
use Locale::PO;
use File::Find;
use Data::Dumper::Concise;
use Path::Tiny;
use Getopt::Long;
use DateTime; 
use DateTime::Format::Strptime;

my $pot_file;
my $now = DateTime::Format::Strptime->new(pattern => '%T %R%z')->format_datetime(DateTime->now);

GetOptions('pot=s' => \$pot_file) or die;

my @dirs = @ARGV;
die unless @dirs;

my @files;

find(sub { push @files, $File::Find::name if -f && /\.vue$/ }, @dirs);

print Dumper(\@files);

my %po_objects;

foreach my $f (@files) {
    my $body = path($f)->slurp_utf8;
    local $_ = $body;
    pos($_) = 0;
    my $line = 1;
    # stolen from https://metacpan.org/dist/Locale-Maketext-Lexicon/source/lib/Locale/Maketext/Extract/Plugin/Generic.pm#L29
    my $quoted = '(?:\')(?:[^\\\']*(?:\\.[^\\\']*)*)(?:\')|(?:\")(?:[^\\\"]*(?:\\.[^\\\"]*)*)(?:\")';
    while (m/
                \G
                (
                    .*?
                    (
                        \$gettext\(
                        \s*($quoted)
                        (.*?)
                        \)
                    )
                )
            /smogx) {
        my ($context, $str) = ($2, $3);
        $line += ( () = ( $1 =~ /\n/g ) );
        print "$str ($context $f:$line)\n";
        add_entry(msgid => $str,
                  reference => [ "$f:$line" ],
                  automatic => [ $context ],
                 );
    }
    $line = 1;
    pos($_) = 0;
    while (m/
                \G
                (
                    .*?
                    (
                        \$ngettext\(
                        \s*
                        ($quoted)
                        \s*,\s*
                        ($quoted)
                        (.*?)
                        \)
                    )
                )
            /smogx) {
        my ($context, $singular, $plural) = ($2, $3, $4);
        $line += ( () = ( $1 =~ /\n/g ) );
        print "$singular - $plural ($context $f:$line)\n";
        my @pieces;
        add_entry(msgid => $singular,
                  msgid_plural => $plural,
                  reference => [ "$f:$line" ],
                  automatic => [ $context ],
                 );
    }
}

# print Dumper(\%po_objects);
my @pos = (
           Locale::PO->new(
                           -msgid => "",
                           -msgstr => "Project-Id-Version: Mycorrhiza 0.01\n"
                                      . "POT-Creation-Date: $now\n"
                                      . "PO-Revision-Date: $now\n"
                                      . "Last-Translator: FULL NAME <EMAIL\@ADDRESS>\n"
                                      . "Language-Team: LANGUAGE <LL\@localhost>\n"
                                      . "MIME-Version: 1.0\n"
                                      . "Content-Type: text/plain; charset=UTF-8\n"
                                      . "Content-Transfer-Encoding: 8bit\n",
                          ),
          );
foreach my $k (sort keys %po_objects) {
    my $data = $po_objects{$k};
    my %constructor = (
                       $data->{msgid_plural} ? (-msgstr_n => { 0 => '' }) : (-msgstr => ''),
                      );
    foreach my $k (keys %$data) {
        $constructor{"-$k"} = ref($data->{$k}) ? join(' ', @{$data->{$k}}) : $data->{$k};
    }
    # print Dumper(\%constructor);
    my $po = Locale::PO->new(%constructor);
    push @pos, $po;
}

if ($pot_file) {
    Locale::PO->save_file_fromarray($pot_file, \@pos, 'utf8');
}

sub add_entry {
    my %po = @_;
    return unless $po{msgid};
    foreach my $i (qw/msgid msgid_plural/) {
        if (my $v = $po{$i}) {
            $v = substr($v, 1, -1);
            $v =~ s/\\(["'])/$1/g;
            $po{$i} = $v;
        }
    }
    return unless $po{msgid};
    if (my $exists = $po_objects{$po{msgid}}) {
        if (my $plural = $po{msgid_plural}) {
            $exists->{msgid_plural} ||= $plural;
        }
        foreach my $k (qw/automatic reference/) {
            if ($po{$k}) {
                $exists->{$k} ||= [];
                push @{$exists->{$k}}, @{$po{$k}};
            }
        }
    }
    else {
        $po_objects{$po{msgid}} = \%po;
    }
}
