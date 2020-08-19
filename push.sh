#!/usr/bin/env bash

function get_last_modified_timestamp(){
    if [ "$(uname)"=="Darwin" ]
    then
        modified_date=`stat -f "%Sm" $1`
        modified_stamp=`date -j -f "%b %d %T %Y" "$modified_date" +%s`
    elif [ "$(uname)"=="Linux" ]
    then
        modified_stamp=`stat -c "%Y" $1`
        # modified_date=`date -d @$modified_stamp`
    fi
    echo $modified_stamp
}

posts=()
function list_files() {
    #1st param, the dir name
    #2nd param, the aligning space
    for file in `ls $1`;
    do
        if [ -f "$1/$file" ]; then
            posts=( "${posts[@]}" $1/$file )
            
        fi
    done
}

SECONDS_OF_HALF_DAY=43200
function update_post_status() {
    list_files $1
    for post in ${posts[@]};
    do  
        modified_timestamp=`get_last_modified_timestamp $post`
        time_deltaDays=$[ ($(date +%s) - ${modified_timestamp}) / $SECONDS_OF_HALF_DAY ]
        update_date=`date -r $modified_timestamp +%Y-%m-%d`
        if [ $time_deltaDays -lt 1 ]
        then
            sed -i '' -e 's/^\(date:[[:space:]]*\).*$/\1'$update_date'/' $post
            new_name=`echo $post | sed 's/[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}/'$update_date'/'`
            mv $post $new_name
            echo $time_deltaDays
	    echo $post

            
        
        fi
    done
}

# update post date
POST_DIR=./_posts
update_post_status $POST_DIR

git add .
git commit -m"update on '$update_date'"
git push origin master



