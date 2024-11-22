use Mojo::Base -strict;

use Test::More;
use Test::Mojo;
use Data::Dumper::Concise;
use YAML qw/LoadFile/;

my $creds = LoadFile('amusecompile.yml');
my $key = $creds->{api_keys}->[0];
my $t = Test::Mojo->new('Amusecompile');
$t->get_ok('/minion')->status_is(401)->content_like(qr/Authentication required/i);
$t->get_ok('/api/v1/check', {})->status_is(401);
$t->get_ok('/api/v1/check', { 'X-AMC-API-Key' => 'rand' })->status_is(401);
$t->post_ok('/api/v1/create-session', { 'X-AMC-API-Key' => 'rand' })->status_is(401);
my $h = { 'X-AMC-API-Key' => $key };
$t->get_ok('/api/v1/check', $h)->status_is(200)->json_is({ status => 'OK' });
$t->post_ok('/api/v1/create-session', $h)->status_is(200)->json_has('/session', "Session id returned");
diag Dumper($t->tx->res->json);
done_testing();
