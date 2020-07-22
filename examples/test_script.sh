files_list=( "a.txt" "b.txt" "c and space.txt" )
GREETING=Yoooooo
echo_greeting() {
    echo $1
}
for i in "${files_list[@]}"; do
    if [ -f "$i" ]; then
        head -n5 "$i" | grep $GREETING >> all_greetings.txt
    else 
        echo_greeting $GREETING
    fi
done