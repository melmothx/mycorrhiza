package Amusecompile::Model::BookCover::Token;

use utf8;
use strict;
use warnings;
use Types::Standard qw/Str Object/;
use Moo;
use Text::Amuse::Functions qw/muse_to_object muse_format_line/;
use Business::ISBN;
use PDF::API2;

has name => (is => 'ro', isa => Str, required => 1);
has type => (is => 'ro', isa => Str, required => 1);
has desc => (is => 'ro', isa => Str, required => 1);
has value => (is => 'rw', isa => Str, required => 0);
has wd => (is => 'ro', isa => Object);

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
                      file =>  qr{[0-9a-z-]+\.(?:png|jpe?g)},
                      isbn => qr{[0-9-]{10,}},
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
                     if ($fname =~ m/\A([A-Za-z0-9-]+\.(png|jpe?g))\z/) {
                         return $1;
                     }
                     return '';
                 },
                 isbn => sub {
                     return $self->create_isbn_pdf($_[0]);
                 },
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

sub create_isbn_pdf {
    my ($self, $code) = @_;
    return unless $self->wd;
    if (my $isbn = Business::ISBN->new($code)) {
        if ($isbn->is_valid) {
            my $isbn = my $barcode = $isbn->as_string;
            $barcode =~ s/\D//ga;
            my $pdf = PDF::API2->new(-compress => 0);
            my $page = $pdf->page;
            my $gfx = $page->gfx;
            $page->mediabox(114,96);
            my $xo = $pdf->xo_ean13(-code => $barcode,
                                    -font => $pdf->corefont('Helvetica'),
                                    -umzn => 20,
                                    -lmzn => 8,
                                    -zone => 52,
                                    -quzn => 4,
                                    -fnsz => 10,
                                   );
            $gfx->formimage($xo, 0, 0);
            my $text = $page->text;
            $text->font($pdf->corefont('Helvetica'), 9);
            $text->fillcolor('black');
            $text->translate(57, 86);
            $text->text_center("ISBN $isbn");
            my $dest = $self->wd->child("isbn-$isbn.pdf");
            $pdf->save("$dest");
            return $dest->basename;
        }
    }
    return '';
}
1;
