package Amusecompile::Model::BookBuilder;

use utf8;
use strict;
use warnings;
use Moo;
use Path::Tiny;
use Types::Standard qw/Str ArrayRef HashRef Object CodeRef/;
use Archive::Zip qw( :ERROR_CODES :CONSTANTS );
use Text::Amuse::Compile;
use Data::Dumper::Concise;
use Cwd;

has working_directory => (is => 'ro', isa => Object, required => 1);

has file_list => (is => 'ro', isa => ArrayRef[HashRef], required => 1);

has logger => (is => 'ro', isa => CodeRef, default => sub { sub {} });

sub unpack_files {
    my $self = shift;
    my $wd = $self->working_directory;
    my @muse_list;
    foreach my $f (@{ $self->file_list }) {
        if ($f->{original_filename} =~ m/([0-9a-z-]+)\.zip/) {
            my $musename = $1;
            my $zipfile = $wd->child($f->{basename});
            my $zip = Archive::Zip->new;
            if ($zip->read("$zipfile") == AZ_OK) {
                $self->logger->("Extracting $zipfile $musename to $wd");
                $zip->extractTree($musename, "$wd");
                my $musefile = $wd->child($musename . '.muse');
                if ($musefile->exists) {
                    $self->logger->("Adding $musefile");
                    push @muse_list, { path => $musefile };
                    $zipfile->remove;
                }
            }
        }
    }
    return \@muse_list;
}

sub session_id {
    shift->working_directory->basename;
}

sub compile {
    my $self = shift;
    if (my @muse_files = @{$self->unpack_files}) {
        $self->logger->(Dumper(\@muse_files));
        my $homedir = getcwd();
        my $c = Text::Amuse::Compile->new(pdf => 1);
        my $outfile;
        if (@muse_files == 1) {
            my $file = $muse_files[0]{path}->stringify;
            $c->compile($file);
            $file =~ s/\.muse$/.pdf/;
            $outfile = path($file);
            
        }
        else {
            my $target = {
                          path => $self->working_directory->stringify,
                          files => [ map { $_->{path}->stringify } @muse_files ],
                          name => $self->session_id,
                          title => "My collection",
                         };
            $c->compile($target);
            $outfile = $self->working_directory->child($self->session_id . ".pdf");
        }
        die "cwd changed. This is a bug" if getcwd() ne $homedir;
        if ($outfile and -f $outfile) {
            return $outfile;
        }
    }
    return;
}

1;

