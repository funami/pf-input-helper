#!/usr/bin/perl
use strict;
use warnings;
use FindBin;
use XML::TreePP;
use LWP::Simple;
use Template;
use CGI;
use DateTime;
use JSON::Syck;
use utf8;
my $cgi = CGI->new();

my $rss = "http://picasaweb.google.com/data/feed/base/user/tohoku.anpi?alt=rss&kind=album&hl=ja&access=public";
my $api = "http://picasaweb.google.com/data/feed/api/user/tohoku.anpi?alt=rss&kind=album&hl=ja&access=public";
my $contents = get($api);
my $tpp = XML::TreePP->new( force_array => [qw( item )] );
my $feed = $tpp->parse($contents,);
my $items = $feed->{rss}{channel}{item};

my $tt = Template->new({
               INCLUDE_PATH => "$FindBin::RealBin/templates",
           }) || die $Template::ERROR, "\n";
my @files;
opendir(DIR, "$FindBin::RealBin");
@files = readdir(DIR);
closedir(DIR);


my $file_list = {};
for (@files) {
    my $lastmodified = (stat "$FindBin::RealBin/$_")[9];
    my $dt = DateTime->from_epoch(epoch => $lastmodified);
    $dt->set_time_zone( 'Asia/Tokyo' );
    $file_list->{$_} = {lm => $dt->strftime('%m/%d %H:%M')};
}


my @list;
for (@$items){
    if ($_->{link} ne "https://picasaweb.google.com/tohoku.anpi/DropBox"){
        my $id = $1;
        #my $updated = $_->get('atom:updated') ;
        #my $pub_date = $_->pubDate;
        #$updated =~ s/T/<br \/>/;
        #$pub_date =~ s/T/<br \/>/;
      #  print "<td><a href=\"".$_->title.".shtml\"><img src=\"" .$_->get('media:group/media:thumbnail@url')."\" style=\"height:40px\"></a></td>\n";
      #  print "<td><a href=\"".$_->title.".shtml\">" .$_->title ."</a></td>\n";
      #  print "<td>" . $_->get('media:group/media:description') ."</td>\n";
      #  print "<td style=\"font-size:0.8em\">". $updated ."</td>\n";
      #  print "<td style=\"font-size:0.8em\">". $pub_date ."</td>\n";
        my $last_modified = $_->{'gphoto:timestamp'};
        my $dt = DateTime->from_epoch(epoch=>$_->{'gphoto:timestamp'}/1000);
        $dt->set_time_zone( 'Asia/Tokyo' );
        $last_modified = $dt->strftime('%m/%d');
        my $data = {};
        my $data_file = "$FindBin::RealBin/".$_->{title}.".dat";
        #print $data_file . "\n";
        $data = eval{JSON::Syck::LoadFile($data_file)} if (-f $data_file); 
        push @list,{
            title => $_->{title},
            ththumbnail => $_->{'media:group'}{'media:thumbnail'}{'-url'},
            description => Encode::encode_utf8($_->{description}),
            numphotos => $_->{'gphoto:numphotos'},
            last_modified => $last_modified,
            list_made => (-f "$FindBin::RealBin/".$_->{title}.".shtml") ? 1:0,
            check_dt => $file_list->{$_->{title}.".shtml"}{lm},
            data => $data,
        }; 
    }
}

my $vars = {
    rss => $rss ,
    items => \@list,
};
print $cgi->header(-type=>'text/html' , -charset=>'utf-8'); 
my $output = $tt->process('index.tt',$vars)
               || die $tt->error(), "\n";
