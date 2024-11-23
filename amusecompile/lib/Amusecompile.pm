package Amusecompile;
use utf8;
use strict;
use warnings;
use Mojo::Base 'Mojolicious', -signatures;
use Mojo::Pg;
use Mojo::Util 'secure_compare';
use Path::Tiny;
use Data::Dumper::Concise;


# This method will run once at server start
sub startup ($self) {
    # Load configuration from config file
    my $config = $self->plugin('NotYAMLConfig');
    # Configure the application
    $self->helper(log => sub {
                      state $log = Mojo::Log->new;
                  });
    $self->log->info("Starting up with " . Dumper($config));
    $self->secrets($config->{secrets}) if $config->{secrets};
    $self->helper(pg => sub {
                      state $pg = Mojo::Pg->new($config->{dbi_connection_string});
                  });
    $self->helper(wd => sub {
                      state $wd = path($config->{working_directory} || 'muse')->absolute;
                  });
    $self->plugin(Minion => { Pg => $config->{dbi_connection_string} });
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
    $api->post('/create-session')->to('API#create_session')->name('api_create_session');
    $api->post('/add/:sid')->to('API#add_file')->name('api_add_file');
    $self->plugin('Minion::Admin' => { route => $admin });
}

1;
