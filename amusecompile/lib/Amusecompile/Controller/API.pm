package Amusecompile::Controller::API;
use Mojo::Base 'Mojolicious::Controller', -signatures;
use Data::Dumper::Concise;
use Path::Tiny ();
use DateTime;
use JSON::MaybeXS qw/decode_json/;
use Text::Amuse::Compile::TemplateOptions;

sub check ($self) {
    $self->render(json => { status => 'OK' });
}

sub cleanup ($self) {
    my $jid = $self->minion->enqueue(cleanup => []);
    $self->render(json => { status => 'OK', job_id => $jid });
}

sub check_session ($self) {
    my $sid = $self->param('sid');
    if (my $check = $self->pg->db->select(amc_sessions => ['sid'], { sid => $sid,
                                                                     session_type => 'bookbuilder' })->hash) {
        if ($self->wd->child($check->{sid})->exists) {
            return $self->render(json => { session_id => $sid });
        }
    }
    $self->render(json => { error => "Invalid session" });
}

sub create_session ($self) {
    my $wd = $self->wd;
    $wd->mkdir;
    my $sessiondir = $self->wd->tempdir(CLEANUP => 0);
    $self->log->debug("Creating session");
    my $sid = $sessiondir->basename;
    $self->pg->db->insert(amc_sessions => {
                                           sid => $sid,
                                           session_type => 'bookbuilder',
                                           created => \'NOW()',
                                           last_modified => \'NOW()',
                                          });
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
        if (my $check = $db->select(amc_sessions => ['sid'],
                                    {
                                     sid => $sid,
                                     session_type => 'bookbuilder'
                                    })->hash) {
            if ($check and $check->{sid}) {
                my $stack_sql = 'SELECT MAX(sorting_index) AS idx, SUM(file_size) AS total_size FROM amc_session_files WHERE sid = ?';
                my $stack = $db->query($stack_sql, $sid)->hash;
                my $index = ($stack->{idx} || 0) + 1;
                $self->log->debug(Dumper($stack));
                if ($stack->{total_size} and $stack->{total_size} > (1024 * 1024 * 64)) {
                    return $self->render(json => { status => 'Quota exceeded' });
                }
                if (my $upload = $self->req->upload('muse')) {
                    my $id = $db->insert(amc_session_files => {
                                                               sid => $sid,
                                                               original_filename => $upload->filename,
                                                               sorting_index => $index,
                                                               file_size => $upload->size,
                                                               attributes => { -json => $self->req->body_params->to_hash },
                                                               created => \'NOW()',
                                                               last_modified => \'NOW()',
                                                              },
                                         { returning => 'id' })->hash->{id};
                    my $basename = sprintf('%08d.zip', $id);
                    my $destination = $self->wd->child($sid)->child($basename);
                    $upload->move_to($destination);
                    $self->log->info("Uploaded $destination");
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
        @all = $self->pg->db->select(amc_session_files => undef, { sid => $sid }, { order_by => 'sorting_index' })
          ->expand->hashes->each;
    }
    return \@all;
};

sub list_texts ($self) {
    $self->render(json => { texts => $self->_get_file_list });
}

sub remove_from_list ($self) {
    if (my $sid = $self->param('sid')) {
        if (my $tid = $self->param('tid')) {
            $self->pg->db->delete(amc_session_files => { sid => $sid, id => $tid });
            return $self->render(json => { texts => $self->_get_file_list, status => 'OK' });
        }
    }
    $self->render(json => { error => 'not found' });
}

sub reorder_list ($self) {
    if (my $sid = $self->param('sid')) {
        if (my $move_id = $self->param('move_id')) {
            if (my $to_id = $self->param('to_id')) {
                my $db = $self->pg->db;
                my @pos = map { $_->{id} }
                  $db->select(amc_session_files => [qw/id/], { sid => $sid },
                                        { order_by => 'sorting_index' })->hashes->each;
                my @newpos;
                foreach my $id (@pos) {
                    if ($id != $move_id) {
                        if ($id == $to_id) {
                            push @newpos, $move_id, $to_id;
                        }
                        else {
                            push @newpos, $id;
                        }
                    }
                }
                $self->log->debug(Dumper([\@pos, \@newpos]));
                my $order = 0;
                foreach my $id (@newpos) {
                    $order++;
                    $db->update(amc_session_files => { sorting_index => $order }, { id => $id });
                }
                return $self->render(json => { texts => $self->_get_file_list, status => 'OK' });
            }
        }
    }
    $self->render(json => { error => 'not found' });
}

sub compile ($self) {
    my $db = $self->pg->db;
    if (my $sid = $self->param('sid')) {
        if (my $check = $db->select(amc_sessions => undef, { sid => $sid, session_type => 'bookbuilder' })) {
            my $bbargs = $self->req->body_params->to_hash;
            $self->log->debug(Dumper($bbargs));
            my $jid = $self->minion->enqueue(compile => [ $sid, $bbargs ]);
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
    if (my $session = $self->pg->db->select(amc_sessions => undef,
                                            {
                                             sid => $sid,
                                             session_type => 'bookbuilder',
                                            })->hash) {
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

sub fonts ($self) {
    my $fonts = [];
    if (my $fontspec = $self->fontspec_file) {
        if ($fontspec->exists) {
            $fonts = decode_json($fontspec->slurp_raw);
        }
    }
    $self->render(json => { fonts => $fonts });
}

sub headings ($self) {
    my @options = grep { $_->{desc} } Text::Amuse::Compile::TemplateOptions->all_headings;
    $self->render(json => { headings => \@options });
}

1;
