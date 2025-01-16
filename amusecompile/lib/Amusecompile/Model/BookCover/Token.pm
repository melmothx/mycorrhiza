package Amusecompile::Model::BookCover::Token;

use utf8;
use strict;
use warnings;
use Types::Standard qw/Str/;
use Moo;
use Text::Amuse::Functions qw/muse_to_object muse_format_line/;

has name => (is => 'ro', isa => Str, required => 1);
has type => (is => 'ro', isa => Str, required => 1);
has desc => (is => 'ro', isa => Str, required => 1);
has value => (is => 'rw', isa => Str, required => 0);

sub validate {
    my ($self) = @_;
    my $value = $self->value;
    return undef unless defined $value;
    if (my $type = $self->type) {
        my %checks = (
                      int =>   qr{0|[1-9][0-9]*},
                      float => qr{[0-9]+(?:\.[0-9]+)?},
                      muse_body =>  qr{.*}s,
                      muse_str =>  qr{.*}s, # we're mangling the new lines anyway
                      file =>  qr{[0-9a-z-]+\.(?:pdf|png|jpe?g)},
                      isbn => qr{isbn-[0-9-]{10,}\.pdf},
                     );
        if (my $re = $checks{$type}) {
            if ($value =~ m/\A($re)\z/) {
                my $valid = $1;
                return $valid;
            }
        }
    }
    return undef;
}

sub token_value_for_form {
    my $self = shift;
    my $validated = $self->validate;
    if ($validated and $self->type eq 'isbn') {
        $validated =~ s/isbn-([0-9-]{10,})\.pdf/$1/;
    }
    return $validated;
}

sub token_value_for_template {
    my $self = shift;
    my $validated = $self->validate;
    my $token_type = $self->type;
    my %trans = (
                 float => sub { return $_[0] },
                 int => sub { return $_[0] },
                 muse_body => sub {
                     my $str = $_[0];
                     my $latex = muse_to_object($str)->as_latex;
                     $latex =~ s/\A\s*//s;
                     $latex =~ s/\s*\z//s;
                     return $latex;
                 },
                 muse_str => sub {
                     my $str = $_[0];
                     $str =~ s/\s+/ /gs;
                     $str =~ s/<\s*br\s*\/*\s*>/ /gs;
                     my $latex = muse_format_line(ltx => $str);
                     $latex =~ s/\A\s*//s;
                     $latex =~ s/\s*\z//s;
                     return $latex;
                 },
                 file => sub {
                     my $fname = $_[0];
                     if ($fname =~ m/\A(f[0-9]+\.(pdf|png|jpe?g))\z/) {
                         return $1;
                     }
                     return '';
                 },
                 isbn => sub {
                     my $fname = $_[0];
                     if ($fname =~ m/\A(isbn-[0-9-]+\.pdf)\z/) {
                         return $1;
                     }
                     return '';
                 }
                );
    if (defined($validated)) {
        if (my $sub = $trans{$token_type}) {
            return $sub->($validated);
        }
    }
    # still here?
    if ($token_type eq 'int' or $token_type eq 'float') {
        return 0;
    }
    else {
        return '';
    }
}

1;
