package Amusecompile::Controller::API;
use Mojo::Base 'Mojolicious::Controller', -signatures;
use Data::Dumper::Concise;
use Path::Tiny ();
use DateTime;

sub check ($self) {
    # Render template "example/welcome.html.ep" with message
    $self->render(json => { status => 'OK' });
}

sub create_session ($self) {
    my $wd = $self->wd;
    $wd->mkdir;
    my $sessiondir = $self->wd->tempdir(CLEANUP => 0);
    $self->log->debug("Creating session");
    my $sid = $sessiondir->basename;
    $self->pg->db->query('INSERT INTO amc_sessions (sid, created, last_modified) VALUES(?, NOW(), NOW())', $sid);
    $self->render(json => { session_id => $sid });
}

sub add_file ($self) {
    my $sid = $self->param('sid');
    if ($self->req->is_limit_exceeded) {
        return $self->render(json => { status => 'File is too big.' });
    }
    my $out = {};
    if ($sid) {
        my $db = $self->pg->db;
        if (my $check = $db->query('SELECT sid FROM amc_sessions WHERE sid = ?', $sid)->hash) {
            if ($check and $check->{sid}) {
                my $stack_sql = 'SELECT MAX(sorting_index) AS idx, SUM(file_size) AS total_size FROM amc_session_files WHERE sid = ?';
                my $stack = $db->query($stack_sql, $sid)->hash;
                my $index = ($stack->{idx} || 0) + 1;
                $self->log->debug(Dumper($stack));
                if ($stack->{total_size} and $stack->{total_size} > (1024 * 1024 * 64)) {
                    return $self->render(json => { status => 'Quota exceeded' });
                }
                if (my $upload = $self->req->upload('muse')) {
                    my $file_title = $self->param('title') || '';
                    my $sql =<<'SQL';
INSERT INTO amc_session_files
       (sid, original_filename, sorting_index, file_size, title, created, last_modified)
VALUES (?,   ?,                 ?,             ?,         ?,     NOW(),    NOW()       )
RETURNING id
SQL

                    my $id = $db->query($sql,
                                              $sid, $upload->filename, $index, $upload->size,
                                              $file_title,
                                             )->hash->{id};
                    my $basename = sprintf('%08d.zip', $id);
                    my $destination = $self->wd->child($sid)->child($basename);
                    $upload->move_to($destination);
                    $self->log->info("Uploaded $destination $file_title");
                    $db->update(amc_session_files => { basename => $basename }, { id => $id });
                    $out->{success} = 1;
                    $out->{status} = 'OK';
                    $out->{file_id} = $id;
                }
            }
        }
        else {
            $out->{status} = 'Invalid session id';
        }
    }
    else {
        $out->{status} = 'Missing session id';
    }
    $self->render(json => $out);
}

sub _get_file_list ($self) {
    my @all;
    if (my $sid = $self->param('sid')) {
        @all = $self->pg->db->select(amc_session_files => undef, { sid => $sid }, { order_by => 'sorting_index' })->hashes->each;
    }
    return \@all;
};

sub list_texts ($self) {
    $self->render(json => { texts => $self->_get_file_list });
}

sub compile ($self) {
    my $db = $self->pg->db;
    if (my $sid = $self->param('sid')) {
        if (my $check = $db->select(amc_sessions => undef, { sid => $sid })) {
            my $jid = $self->minion->enqueue(compile => [ $sid ]);
            $db->update(amc_sessions => { job_id => $jid, last_modified => \'NOW()' }, { sid => $sid });
            return $self->render(json => { job_id => $jid });
        }
    }
    return $self->render(json => { error => 'not found' });
}

sub job_status ($self) {
    my $jid = $self->param('jid');
    my $status = "not found";
    if (my $job = $self->minion->job($jid)) {
        $status = $job->info->{state};
    }
    return $self->render(json => {
                                  job_id => $jid,
                                  status => $status,
                                 });
}

sub get_compiled_file ($self) {
    my $sid = $self->param('sid');
    if (my $session = $self->pg->db->query('SELECT * FROM amc_sessions WHERE sid = ?', $sid)->hash) {
        $self->log->info(Dumper($session));
        if ($session->{compiled_file} and -f $session->{compiled_file}) {
            my $data = Path::Tiny::path($session->{compiled_file})->slurp_raw;
            my $now = DateTime->now->strftime('%Y-%m-%d--%H-%M-%S');
            $self->res->headers->content_disposition(qq{attachment; filename="bookbuilder-$now.pdf"});
            return $self->render(data => $data, format => 'pdf');
        }
    }
    return $self->render(text => "Not found", status => 404);
}

1;
