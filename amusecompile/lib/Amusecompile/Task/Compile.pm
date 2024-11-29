package Amusecompile::Task::Compile;
use strict;
use warnings;
use Mojo::Base 'Mojolicious::Plugin';
use Amusecompile::Model::BookBuilder;

sub register {
    my ($self, $app) = @_;
    $app->minion->add_task(compile => sub {
                               my ($job, $sid) = @_;
                               my $logger = $job->app->log->info("Compiling $sid");
                               my $db = $job->app->pg->db;
                               my $wd = $job->app->wd;
                               my @all = $db->select(amc_session_files => undef, { sid => $sid },
                                                     { order_by => 'sorting_index' })->hashes->each;
                               my @logs;
                               my $c = Amusecompile::Model::BookBuilder->new(working_directory => $wd->child($sid),
                                                                             logger => sub { push @logs, @_ },
                                                                             file_list => \@all);
                               my $update = {
                                             last_modified => \'NOW()',
                                             logs => { -json => \@logs },
                                            };
                               if (my $outfile = $c->compile) {
                                   $update->{compiled_file} = "$outfile";
                               }
                               $db->update(amc_sessions => $update, { sid => $sid });
                           });
}

1;
