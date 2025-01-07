package Amusecompile::Model::BookCover;

use utf8;
use strict;
use warnings;
use Moo;
use Path::Tiny;
use Types::Standard qw/StrMatch ArrayRef HashRef Object CodeRef Str Int/;
use Text::Amuse::Compile::Fonts;
use Text::Amuse::Compile::Fonts::Selected;
use Text::Amuse::Utils;
use Template::Tiny;
use IPC::Run qw(run);
use Archive::Zip ();
use Cwd;
use PDF::API2;
use Amusecompile::Model::BookCover::Token;
use Data::Dumper::Concise;

# use DateTime;

# use PDF::API2;
use Business::ISBN;

has fontspec_file => (is => 'ro', required => 1);

has template_file => (is => 'ro', required => 0);

has working_dir => (is => 'ro', isa => Object, required => 1);

has working_template => (is => 'lazy', isa => Object);

has fonts => (is => 'lazy',
              isa => Object,
              handles => [qw/serif_fonts mono_fonts sans_fonts all_fonts/],
             );

sub _build_fonts {
    my $self = shift;
    return Text::Amuse::Compile::Fonts->new($self->fontspec_file);
}

has tokens => (is => 'lazy', isa => ArrayRef[Object]);

has template => (is => 'ro', isa => Object);
has font_name => (is => 'ro', isa => Str, default => sub { 'DejaVu Serif' });
has language_code => (is => 'ro', isa => Str, default => sub { 'en' });
has coverheight => (is => 'ro', isa => Int, default => sub { 210 });
has coverwidth => (is => 'ro', isa => Int, default => sub { 148 });
has spinewidth => (is => 'ro', isa => Int, default => sub { 0 });
has flapwidth => (is => 'ro', isa => Int, default => sub { 0 });
has wrapwidth => (is => 'ro', isa => Int, default => sub { 0 });
has bleedwidth => (is => 'ro', isa => Int, default => sub { 10 });
has marklength => (is => 'ro', isa => Int, default => sub { 5 });
has foldingmargin => (is => 'ro', isa => Int, default => sub { 0 });

has logger => (is => 'ro', isa => CodeRef, default => sub { sub {} });

sub _build_tokens {
    my $self = shift;
    my $tt = $self->working_template;
    # this is the simple TT one so we just check for the tokens used
    my $body = $tt->slurp_utf8;
    my %tokens;
    my @out;
    while ($body =~ m/\[\%\s*(?:IF\s+)?(([a-z_]+)_(int|muse_str|muse_body|float|file|isbn))\s*\%\]/g) {
        my ($whole, $name, $type) = ($1, $2, $3);
        unless ($tokens{$whole}) {
            my $desc = join(' ', map { ucfirst $_ } split(/_/, $name));
            push @out, Amusecompile::Model::BookCover::Token->new(name => $name,
                                                                  type => $type,
                                                                  full_name => $whole,
                                                                  desc => $desc);
            $tokens{$whole}++;
        }
    }
    return \@out;
}


sub _build_working_template {
    my $self = shift;
    my $wd_template = $self->working_dir->child('cover.tt');
    if (my $template_file = $self->template_file) {
        $template_file->copy($wd_template);
    }
    else {
        my $body = <<'LATEX';
% document class populated by us
\begin{document}
\begin{bookcover}
\bookcovercomponent{normal}{front}[15mm,15mm,15mm,15mm]{
  \begin{minipage}{\partwidth}
  \begin{center}
[% IF author_muse_str %]
{\bfseries\itshape\LARGE [% author_muse_str %]\par\bigskip}
[% END %]
{\bfseries\Huge [% title_muse_str %]\par\bigskip}
[% IF subtitle_muse_str %]
{\bfseries\LARGE [% subtitle_muse_str %]\par\bigskip}
[% END %]
  \end{center}
  \end{minipage}
[% IF image_file %]
\vfill
\begin{center}
\includegraphics[% IF image_width_in_mm_int %][width=[% image_width_in_mm_int %]mm][% ELSE %][width=\partwidth][% END %]{[% image_file %]}
\end{center}
[% END %]
[% IF front_footer_muse_str %]
\vfill
\begin{center}
{\bfseries\large [% front_footer_muse_str %]}
\end{center}
[% END %]
}

\bookcovercomponent{center}{spine}{
  \rotatebox[origin=c]{-90}{\bfseries [% IF author_muse_str %]\emph{[% author_muse_str %]}\quad\quad[% END %]
  [% title_muse_str %]}
}
\bookcovercomponent{normal}{back}[15mm,15mm,15mm,15mm]{
  \begin{center}
  \begin{minipage}{\partwidth}
[% back_text_muse_body %]
\end{minipage}
\end{center}
[% IF isbn_isbn %]
\strut
\vfill
\begin{flushright}
\includegraphics[height=3cm]{[% isbn_isbn %]}
\end{flushright}
[% END %]
}
\end{bookcover}
\end{document}
LATEX
        $wd_template->spew_utf8($body);
    }
    return $wd_template;
}


sub compose_preamble {
    my $self = shift;
    # built in for now
    my @preamble;
    # header
    {
        my @opts = ("12pt", "markcolor=black");
        foreach my $k (qw/
                             coverheight
                             coverwidth
                             spinewidth
                             flapwidth
                             wrapwidth
                             bleedwidth
                             marklength
                         /) {
            push @opts, "$k=" . $self->$k . 'mm';
        }
        foreach my $bool (qw/foldingmargin/) {
            push @opts, "$bool=" . ($self->$bool ? "true" : "false");
        }
        push @preamble, "\\documentclass[" . join(",", @opts) . "]{bookcover}";
    }
    # fonts
    if (my $choice = $self->font_name) {
        if (my @fonts = $self->all_fonts) {
            my ($selected) = grep { $_->name eq $choice } @fonts;
            $selected ||= $fonts[0];
            my $babel_lang = Text::Amuse::Utils::language_mapping()->{$self->language_code || 'en'};
            my $final = Text::Amuse::Compile::Fonts::Selected->new(
                                                                   all_fonts => $self->fonts,
                                                                   size => 12,
                                                                   luatex => 0,
                                                                   main => $selected,
                                                                   mono => $selected,
                                                                   sans => $selected,
                                                                  );
            my $preamble = $final->compose_polyglossia_fontspec_stanza(lang => $babel_lang);
            push @preamble, $preamble;
            push @preamble, "\\frenchspacing";
        }
    }
    push @preamble, "";
    return join("\n", @preamble);
}

sub write_tex_file {
    my $self = shift;
    my %vars;
    foreach my $token (@{ $self->tokens }) {
        $vars{$token->name} = $token->token_value_for_template;
    }
    my $tfile = $self->working_template;
    my $input = $tfile->slurp_utf8;
    my $output;
    $self->logger->("$tfile: $input " . Dumper(\%vars));
    Template::Tiny->new->process(\$input, \%vars, \$output);
    $self->logger->("Output is $output");
    my $outfile = $tfile->parent->child('cover.tex');
    $outfile->spew_utf8($self->compose_preamble, $output);
    return $outfile;
}

sub convert_images_to_cmyk {
    my ($self) = @_;
    my $wd = $self->working_dir;
    # if the profile are provided with the template, convert
    my $rgb = $wd->child('srgb.icc');
    my $cmyk = $wd->child('cmyk.icc');
    my $logger = $self->logger;
    if ($rgb->exists and $cmyk->exists) {
        foreach my $v ($self->tokens) {
            if ($v->token_name =~ m/_file\z/) {
                if (my $basename = $v->token_value_for_template) {
                    if ($basename =~ m/\.(jpe?g)\z/) {
                        my $path = $wd->child($basename);
                        $logger->("Examining $basename\n");
                        my ($in, $out, $err);
                        my @cmd = (identify => -format => '%r', "$path");
                        log_info { "Running " . join(" ", @cmd) };
                        if (run(\@cmd, \$in, \$out, \$err)) {
                            $logger->("Colorspace is $out\n");
                            if ($out =~ m/sRGB/) {
                                $logger->("Converting to CMYK\n");
                                my $tmp = $path->copy($wd->child('tmp.' . $path->basename));
                                @cmd = (convert => "$tmp",
                                        -profile => "$rgb",
                                        -profile => "$cmyk",
                                        "$path");
                                log_info { "Running " . join(" ", @cmd) };
                                run(\@cmd, \$in, \$out, \$err);
                                log_info { "Output: $out $err" };
                            }
                            else {
                                $logger->("Skipping convertion for image with colorspace $out\n");
                            }
                        }
                        else {
                            $logger->("Failure examining $path: $out $err\n");
                        }
                    }
                }
            }
        }
    }
}

sub compile {
    my ($self, $tokens) = @_;
    my $logger = $self->logger;
    my $tex = $self->write_tex_file;
    my $pdf = "$tex";
    $pdf =~ s/\.tex/.pdf/;
    if (-f $pdf) {
        log_info { "Removing $pdf" };
        unlink $pdf or die $!;
    }
    $self->convert_images_to_cmyk;

    # this should happen only in the jobber, where we fork. But in
    # case, return to the original directory.
    my $cwd = getcwd;
    my $wd = $self->working_dir;
    chdir $wd or die "Cannot chdir into $wd";
    my ($in, $out, $err);
    my @run = ("xelatex", '-interaction=nonstopmode', $tex->basename);
    my $ok = run \@run, \$in, \$out, \$err;
    chdir $cwd or die "Cannot chdir back into $cwd";
    # log_info { "Compilation: $out $err" };
    my %res;
    if ($ok and -f $pdf) {
        my $zipdir = Archive::Zip->new;
        if ($zipdir->addTree("$wd", "bookcover-" . $wd->basename) == Archive::Zip::AZ_OK) {
            my $zipfile = $wd->parent->child("bookcover-" . $wd->basename . ".zip");
            if ($zipdir->writeToFileNamed("$zipfile") == Archive::Zip::AZ_OK) {
                %res = (
                        zip_path => "$zipfile",
                        pdf_path => "$pdf"
                       );
            }
            else {
                $logger->("Failed to write zip $zipfile");
            }
        }
        else {
            $logger->("Failed to create zip");
        }
    }
    return {
            stdout => $out,
            stderr => $err,
            %res,
           };
}

sub serialize_object {
    my $self = shift;
    my %out;
    foreach my $m (@{$self->main_dimensions},
                   qw/language_code
                      font_name
                      foldingmargin/) {
        $out{$m} = $self->$m;
    }
    foreach my $token (@{ $self->tokens }) {
        $out{$token->full_name} = $token->value;
    }
    return \%out;
}

sub main_dimensions {
    return [qw/
                  coverheight
                  coverwidth
                  spinewidth
                  flapwidth
                  wrapwidth
                  bleedwidth
                  marklength                  
              /];
}

sub new_from_params {
    my ($class, $internal, $params) = @_;
    my %new;
    foreach my $int (@{ $class->main_dimensions }) {
        my $param = $params->{$int};
        if (defined $param and $param =~ m/\A(0|[1-9][0-9]*)\z/) {
            $new{$param} = $1;
        }
    }
    foreach my $bool (qw/foldingmargin/) {
        $new{$bool} = $params->{$bool} ? 1 : 0;
    }
    foreach my $str (qw/font_name/) {
        $new{$str} = $params->{$str} || 'DejaVu Sans';
        
    }
    my $lang = $params->{language_code};
    if (Text::Amuse::Utils::language_mapping()->{$lang}) {
        $new{language_code} = $lang;
    }
    else {
        $new{language_code} = 'en';
    }
    foreach my $k (%$internal) {
        $new{$k} = $internal->{$k};
    }
    my $bc = $class->new(%new);
    foreach my $token (@{$bc->tokens}) {
        my $v = $params->{$token->full_name};
        $token->value($v) if defined $v;
    }
    return $bc;
}

1;
