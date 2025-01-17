package Amusecompile::Task::Compile;
use strict;
use warnings;
use Mojo::Base 'Mojolicious::Plugin';
use Amusecompile::Model::BookBuilder;
use Amusecompile::Model::BookCover;
use Data::Dumper::Concise;

sub register {
    my ($self, $app) = @_;
    $app->minion->add_task(compile => sub {
                               my ($job, $sid, $bbargs) = @_;
                               my $logger = $job->app->log;
                               $logger->info("Compiling $sid");
                               my $db = $job->app->pg->db;
                               my $wd = $job->app->wd;
                               my @all = $db->select(amc_session_files => undef, { sid => $sid },
                                                     { order_by => 'sorting_index' })->hashes->each;
                               my @logs;
                               my $c = Amusecompile::Model::BookBuilder->new(working_directory => $wd->child($sid),
                                                                             bbargs => $bbargs,
                                                                             logger => sub { push @logs, @_ },
                                                                             file_list => \@all);
                               my $update = {
                                             last_modified => \'NOW()',
                                             logs => { -json => \@logs },
                                            };
                               if (my $outfile = $c->compile) {
                                   $update->{compiled_file} = "$outfile";
                               }
                               $logger->info("Updating record: " . Dumper($update));
                               $db->update(amc_sessions => $update, { sid => $sid });
                           });
    $app->minion->add_task(coverbuild => sub {
                               my ($job, $args) = @_;
                               my $logger = $job->app->log;
                               if (my $sid = $args->{session_id}) {
                                   my $wd = $job->app->wd->child($sid);
                                   if ($wd->exists) {
                                       my @logs;
                                       $logger->info("Compiling $sid" . Dumper($args));
                                       my $c = Amusecompile::Model::BookCover
                                         ->new_from_params({
                                                            fontspec_file => $job->app->fontspec_file,
                                                            working_dir => $wd,
                                                            logger => sub { push @logs, @_ }
                                                           },
                                                           $args);
                                       my $res = $c->compile;
                                       my $update = {
                                                     last_modified => \'NOW()',
                                                     logs => { -json => \@logs },
                                                    };
                                       if ($res->{pdf_path}) {
                                           $update->{compiled_file} = $res->{pdf_path};
                                       }
                                       $job->app->pg->db->update(amc_sessions => $update, { sid => $sid });
                                       $logger->info("Updated $sid with " . Dumper($update));
                                       return;
                                   }
                               }
                               $logger->info("Invalid session");
                           });
    $app->minion->add_task(cleanup => sub {
                               my ($job) = @_;
                               my $db = $job->app->pg->db;
                               my $wd = $job->app->wd;
                               my $logger = $job->app->log;
                               my @stale = map { $_->{sid} }
                                 $db->delete(amc_sessions => { last_modified => { '<',  \"(NOW() - INTERVAL '1 week')" } },
                                             { returning => 'sid' })->hashes->each;
                               my $removed = 0;
                               foreach my $sid (@stale) {
                                   my $stale_tree = $wd->child($sid);
                                   if ($stale_tree->exists) {
                                       $logger->info("Removing $stale_tree");
                                       $stale_tree->remove_tree;
                                       $removed++;
                                   }
                               }
                               my %valid = map { $_->{sid} => 1 } $db->select(amc_sessions => [qw/sid/])->hashes->each;
                               foreach my $tree ($wd->children) {
                                   if (-d $tree) {
                                       unless ($valid{$tree->basename}) {
                                           $logger->info("Removing $tree, not found in the DB");
                                           $tree->remove_tree;
                                           $removed++;
                                       }
                                   }
                               }
                               $logger->info("Removed $removed trees");
                           });
}

1;
