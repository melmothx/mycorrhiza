use Mojo::Base -strict;

use Test::More;
use Test::Mojo;
use Data::Dumper::Concise;
use YAML qw/LoadFile/;
use Path::Tiny;

my $creds = LoadFile('amusecompile.yml');
my $key = $creds->{api_keys}->[0];
my $t = Test::Mojo->new('Amusecompile');
$t->get_ok('/minion')->status_is(401)->content_like(qr/Authentication required/i);
$t->get_ok('/api/v1/check', {})->status_is(401);
$t->get_ok('/api/v1/check', { 'X-AMC-API-Key' => 'rand' })->status_is(401);
$t->post_ok('/api/v1/create-session', { 'X-AMC-API-Key' => 'rand' })->status_is(401);
my $h = { 'X-AMC-API-Key' => $key };
$t->get_ok('/api/v1/check', $h)->status_is(200)->json_is({ status => 'OK' });
$t->post_ok('/api/v1/create-session', $h)->status_is(200)->json_has('/session_id', "Session id returned");
diag Dumper($t->tx->res->json);
my $sid = $t->tx->res->json->{session_id};
$t->post_ok("/api/v1/add/$sid")->status_is(401);
$t->post_ok("/api/v1/add/xyz", $h)->status_is(200)->json_hasnt('/success', "Random id is not a success");
diag Dumper($t->tx->res->json);
$t->post_ok("/api/v1/add/0", $h)->status_is(200)->json_hasnt('/success', "Random id is not a success");
diag Dumper($t->tx->res->json);

foreach my $i (1,2,3) {
    $t->post_ok("/api/v1/add/$sid", $h, form => {
                                                 muse => { file => 't/testfiles/install.zip' },
                                                 title => "Test Text $i"
                                                })->status_is(200)->json_is('/success', 1, "Created OK");
    diag Dumper($t->tx->res->json);
    my $expected_file = path('muse', $sid, sprintf('%03d.zip', $i));
    ok $expected_file->exists, "$expected_file exists";
}

$t->get_ok("/api/v1/list/$sid", $h)->status_is(200)->json_is('/texts/2/title', 'Test Text 3');
diag Dumper($t->tx->res->json);
$t->post_ok("/api/v1/compile/$sid", $h)->status_is(200);
diag Dumper($t->tx->res->json);
my $jid = $t->tx->res->json->{job_id};
$t->get_ok("/api/v1/job-status/$jid", $h)->status_is(200)->json_is('/status', 'inactive');
diag Dumper($t->tx->res->json);
$t->app->minion->perform_jobs_in_foreground;
# check again
$t->get_ok("/api/v1/job-status/$jid", $h)->status_is(200)->json_is('/status', 'finished');
diag Dumper($t->tx->res->json);
diag Dumper($t->app->minion->job($jid)->info);




done_testing();
