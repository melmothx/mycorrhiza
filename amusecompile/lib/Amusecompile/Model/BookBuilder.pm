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

has bbargs => (is => 'ro', isa => HashRef, default => sub { +{} });

sub unpack_files {
    my $self = shift;
    my $wd = $self->working_directory;
    my @muse_list;
    foreach my $f (@{ $self->file_list }) {
        if ($f->{original_filename} =~ m/([0-9a-z-]+)\.zip/) {
            my $musename = $1;
            my $zipfile = $wd->child($f->{basename});
            my $zip = Archive::Zip->new;
            if (-f $zipfile and $zip->read("$zipfile") == AZ_OK) {
                $self->logger->("Extracting $zipfile $musename to $wd");
                $zip->extractTree($musename, "$wd");
                my $musefile = $wd->child($musename . '.muse');
                if ($musefile->exists) {
                    $self->logger->("Adding $musefile");
                    push @muse_list, { path => $musefile };
                    # $zipfile->remove;
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
        # $self->logger->(Dumper(\@muse_files));
        my $homedir = getcwd();
        my $bbargs = $self->bbargs;
        my %extra = map { $_ => $bbargs->{$_} }
          grep { defined $bbargs->{$_} } (qw/papersize
                                             mainfont
                                             sansfont
                                             monofont
                                             fontsize
                                             areaset_width
                                             areaset_height
                                             geometry_top_margin
                                             geometry_outer_margin
                                             bcor
                                             division
                                             twoside
                                             opening
                                             linespacing
                                             parindent
                                             tex_tolerance
                                             tex_emergencystretch
                                             notoc
                                             nofinalpage
                                             nocoverpage
                                             body_only
                                             impressum
                                             sansfontsections
                                             nobold
                                             start_with_empty_page
                                             ignore_cover
                                             continuefootnotes
                                             centerchapter
                                             centersection
                                             headings
                                            /);
        $self->logger->("Options are " . Dumper(\%extra));
        my $c = Text::Amuse::Compile->new(pdf => 1, extra => \%extra);
        my $outfile;
        if (@muse_files == 1) {
            my $file = $muse_files[0]{path}->stringify;
            $c->compile($file);
            $file =~ s/\.muse$/.pdf/;
            $outfile = path($file);
        }
        else {
            my %vheader = map { $_ => $bbargs->{$_} // ''} (qw/title author subtitle date notes source/);
            $vheader{title} ||= "My collection";
            my $target = {
                          path => $self->working_directory->stringify,
                          files => [ map { $_->{path}->stringify } @muse_files ],
                          name => $self->session_id,
                          %vheader,
                         };
            $self->logger->("Compiling " . Dumper($target));
            $c->compile($target);
            $outfile = $self->working_directory->child($self->session_id . ".pdf");
        }
        die "cwd changed. This is a bug" if getcwd() ne $homedir;
        if ($outfile and -f $outfile) {
            $self->logger->("Created $outfile");
            if (my $imposition_schema = $bbargs->{imposition_schema}) {
                my %imposer_options = (
                                       file => "$outfile",
                                       suffix => '_imp',
                                       schema => $imposition_schema,
                                       cover => $bbargs->{fill_signature} || 0,
                                       $bbargs->{signature} ? (signature => $bbargs->{signature}) : (),
                                      );
                if ($bbargs->{crop_papersize}) {
                    $imposer_options{paper} = $bbargs->{crop_papersize};
                    $imposer_options{paper_thickness} = $bbargs->{crop_paper_thickness} || 0;
                }
                $self->logger->("Imposing $outfile with " . Dumper(\%imposer_options));
                my $imposer = PDF::Imposition->new(%imposer_options);
                $imposer->impose;
                my $imposed_file = $imposer->outfile;
                undef $imposer;
                # overwrite the original pdf, we can get another one any time
                rename $imposed_file, $outfile or die "Could not move $imposed_file to $outfile $!";
            }
            return $outfile;
        }
        else {
            die "$outfile not created";
        }
    }
    return;
}

1;

