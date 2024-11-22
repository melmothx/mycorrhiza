package Amusecompile::Controller::API;
use Path::Tiny ();
use Mojo::Base 'Mojolicious::Controller', -signatures;


sub check ($self) {
    # Render template "example/welcome.html.ep" with message
    $self->render(json => { status => 'OK' });
}

sub create_session($self) {
    my $wd = $self->wd;
    $wd->mkdir;
    my $sessiondir = $self->wd->tempdir(CLEANUP => 0);
    $self->log->debug("Creating session");
    my $sid = $sessiondir->basename;
    $self->pg->db->query('INSERT INTO amc_sessions (sid, created, last_modified) VALUES(?, NOW(), NOW())', $sid);
    $self->render(json => { session => $sessiondir->basename });
}

1;
