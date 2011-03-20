#!/usr/bin/perl
use warnings;
use strict;
use LWP::Simple;
use XML::FeedPP;
use HTML::Scrubber;
use Template;
use CGI;
use FindBin;
use DateTime;
use Encode;
use Data::Dumper;


my $cgi = CGI->new();
my $id = $cgi->param('id') || '5584621473184252017,5584654012091048097,5584061561972296753,5584167979985669457,5584268762865923713,5583781275770007857,5583884024494116753,5583944651672966417';
#$id = '5584654012091048097';
my $top = "http://picasaweb.google.com/data/feed/base/user/tohoku.anpi?alt=rss&kind=album&hl=ja&access=public";
for my $roop (1 .. 100){
    print DateTime->now() . " start $roop times\n";
    my $contents = get($top);
    my $feed = XML::FeedPP->new($contents);
    my @list = $feed->get_item();

    my @ids = split(/,/,$id);
    my $loop = 0;
    for (@list){
        #print "$_\n";
        #&create_page($_);
        $_->guid() =~ /albumid\/(\d+)/;
        if ($_->link() ne "https://picasaweb.google.com/tohoku.anpi/DropBox"){
            $id = $1;
            print DateTime->now() . " " . $id."\t".$_->title ."\n";

            &create_page($id);
        }
        $loop++;
        last if ($loop > 10);
    }

    sleep(10);
}


sub create_page {
    my $id = shift;
    my $url = "http://picasaweb.google.com/data/feed/base/user/tohoku.anpi/albumid/$id?alt=rss&kind=photo&hl=ja";

    my $contents = get($url);
    my $scrubber = HTML::Scrubber->new();

    my $feed = XML::FeedPP->new($contents);

    my @list = $feed->get_item();
    my @out = (); 
    my @pf = ();
    for my $item (@list){
            #print $item->link() . "\n";
            #print $item->title() ."\n";
            my $photo_url = $item->guid()."&kind=comment";        
            $photo_url =~ s/entry/feed/;
            $photo_url =~ s/https/http/;
            #print $photo_url . "\n";
            my $tpp = XML::TreePP->new(force_array =>['item']);
            my $tree = $tpp->parsehttp( GET => $photo_url );
            #print Dumper $tree->{rss}{channel}{item};
            my $thu = $item->get('media:group/media:thumbnail@url');
            my $out_item = {                 
                    pf_flag => 0,
                    pf_comment => '-',
                    photo_url => $item->guid(),
                    title => Encode::encode_utf8($item->title()),
                    link => $item->link(),
                    image => $thu,  
            };  
            for (@{$tree->{rss}{channel}{item}}){
                    my $cmt = $scrubber->scrub($_->{description});
                    my $cm = Encode::encode_utf8($cmt);
                    if ($cmt =~ /[PＰ][ＦF].*(完了|開始|登録|終了)/){
                            $out_item->{pf_flag} = 1;
                            $out_item->{pf_comment} = $cmt;
                    }   
                    if (!$out_item->{pf_flag}){
                        $out_item->{pf_comment} = $cmt;
                    }
            }   
            if ($out_item->{pf_flag}){
                push @out,$out_item;
            }else{
                push @pf,$out_item;
            }
    }

    my $title = $feed->title();
    my $vars = {now => DateTime->now( time_zone=>'Asia/Tokyo') ,title => $title, link => $feed->link() ,no_pf => \@pf,pf => \@out};
    my $tt = Template->new({
                   INCLUDE_PATH => "$FindBin::RealBin/templates",
               }) || die $Template::ERROR, "\n";

    my $output;
    $tt->process('list.tt',$vars,"$FindBin::RealBin/$title.shtml")
                   || die $tt->error(), "\n";

}
