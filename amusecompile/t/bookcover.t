#!perl

BEGIN {
    $ENV{PATH} = "$ENV{PATH}:/opt/amusewiki-texlive/current/bin/arch";
}

use strict;
use warnings;
use Test::More;
use Path::Tiny;
use Amusecompile::Model::BookCover;
use Amusecompile::Model::BookCover::Token;
use Data::Dumper::Concise;

my $bc = Amusecompile::Model::BookCover->new(
                                             fontspec_file => path("fontspec.json"),
                                             working_dir => Path::Tiny->tempdir,
                                             font_name => "DejaVu Serif",
                                            );
ok -f $bc->fontspec_file;
ok $bc->fonts;
ok $bc->serif_fonts;
ok $bc->mono_fonts;
ok $bc->sans_fonts;
ok $bc->all_fonts;
diag $bc->working_dir;
diag Dumper($bc->serialize_object);

my $other = Amusecompile::Model::BookCover->new_from_params({
                                                             fontspec_file => path("fontspec.json"),
                                                             working_dir => Path::Tiny->tempdir,
                                                             logger => sub { diag @_ },
                                                            },
                                                            $bc->serialize_object);
ok $other;
ok $bc->working_template->exists;
ok $bc->compose_preamble;
diag Dumper($bc->tokens);
diag Dumper($other->tokens);

my $res = $other->compile;
diag Dumper($res);

my $token = Amusecompile::Model::BookCover::Token->new(name => 'isbn_isbn',
                                                       type => 'isbn',
                                                       desc => 'isbn',
                                                       wd => $bc->working_dir);
$token->value('978-88-99757-60-1');
my $isbn_string = $token->token_value_for_template;
ok $bc->working_dir->child($isbn_string)->exists, "$isbn_string exists";

done_testing;


