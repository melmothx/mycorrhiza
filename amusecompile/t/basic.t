use Mojo::Base -strict;

use Test::More;
use Test::Mojo;

my $t = Test::Mojo->new('Amusecompile');
$t->get_ok('/minion')->status_is(401)->content_like(qr/Authentication required/i);
done_testing();
