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
    $self->plugin(Minion => { Pg => $config->{dbi_connection_string} });
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
    $self->plugin('Minion::Admin' => { route => $admin });
}

1;
