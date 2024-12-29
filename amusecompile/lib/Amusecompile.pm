package Amusecompile;
use utf8;
use strict;
use warnings;
use Mojo::Base 'Mojolicious', -signatures;
use Mojo::Pg;
use Mojo::Util 'secure_compare';
use Path::Tiny;
use Data::Dumper::Concise;
use Text::Amuse::Compile::Fonts::Import;

BEGIN {
    $ENV{PATH} = "$ENV{PATH}:/opt/amusewiki-texlive/current/bin/arch";
}

# This method will run once at server start
sub startup ($self) {
    # Load configuration from config file
    my $config = $self->plugin('NotYAMLConfig');
    # Configure the application
    $self->helper(log => sub {
                      state $log = Mojo::Log->new;
                  });
    # $self->log->info("Starting up with " . Dumper($config));
    $self->secrets($config->{secrets}) if $config->{secrets};
    $self->helper(pg => sub {
                      state $pg = Mojo::Pg->new($config->{dbi_connection_string});
                  });
    $self->helper(wd => sub {
                      state $wd = path($config->{working_directory} || 'muse')->absolute;
                  });
    $self->plugin(Minion => { Pg => $config->{dbi_connection_string} });
    $self->plugin('Amusecompile::Task::Compile');
    my $fontspec = path($config->{fontspec_file} || 'fontspec.json')->absolute;
    unless ($fontspec->exists) {
        $self->log->info("Generating $fontspec");
        Text::Amuse::Compile::Fonts::Import->new(output => "$fontspec")->import_and_save;
    }
    $self->helper(fontspec_file => sub { state $fontspec = $fontspec; });
    $self->pg->migrations->from_file('migrations.sql')->migrate;
    $self->max_request_size(1024 * 1024 * 32);
    my $r = $self->routes;
    my $admin = $r->under('/minion' => sub ($c) {
                              $c->log->debug("In minion route");
                              if (my $user_info = $c->req->url->to_abs->userinfo) {
                                  if (my $credentials = $self->config('admin_passwords')) {
                                      my $passed = 0;
                                    CREDENTIAL:
                                      foreach my $cred (@$credentials) {
                                          if (secure_compare($user_info, $cred)) {
                                              $passed = 1;
                                              last CREDENTIAL;
                                          }
                                      }
                                      return 1 if $passed;
                                  }
                              }
                              $c->log->debug("Not passed, rendering auth");
                              $c->res->headers->www_authenticate('Basic');
                              $c->render(text => 'Authentication required!', status => 401);
                              return undef;
                          });
    my $api = $r->under('/api/v1', sub ($c) {
                            if (my $token = $c->req->headers->header('X-AMC-API-Key')) {
                                if (grep { $_ eq $token } @{$self->config('api_keys') || []}) {
                                    $c->log->debug("Valid Token");
                                    return 1;
                                }
                                else {
                                    $c->log->debug("Invalid Token");
                                }
                            }
                            else {
                                $c->log->debug("Missing Token");
                            }
                            $c->render(text => 'Authentication required!', status => 401);
                            return undef;
                        });
    $api->get('/check')->to('API#check')->name('api_check');
    $api->get('/fonts')->to('API#fonts')->name('api_fonts');
    $api->get('/headings')->to('API#headings')->name('api_headings');
    $api->post('/create-session')->to('API#create_session')->name('api_create_session');
    $api->post('/add/:sid')->to('API#add_file')->name('api_add_file');
    $api->get('/list/:sid')->to('API#list_texts')->name('api_list_texts');
    $api->post('/compile/:sid')->to('API#compile')->name('api_compile');
    $api->post('/list/:sid/remove/:tid')->to('API#remove_from_list')->name('api_remove_from_list');
    $api->post('/list/:sid/reorder/:move_id/:to_id')->to('API#reorder_list')->name('api_reorder_list');
    $api->get('/job-status/:jid')->to('API#job_status')->name('api_job_status');
    $api->get('/compile/:sid')->to('API#get_compiled_file')->name('api_get_compiled_file');
    $self->plugin('Minion::Admin' => { route => $admin });
}

1;
