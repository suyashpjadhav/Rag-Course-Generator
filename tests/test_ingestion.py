from ingestion.ingestion import (
    load_youtube,
    load_audio,
    load_pdf,
    load_pptx,
    load_manual_transcript
)


# Test Block
if __name__ == "__main__":
    # audio test
    audio_path = "C:\\Users\\BIT\\Downloads\\Charlie Puth - How Long [Official Video] - Charlie Puth"
    audio_doc = load_audio(audio_path)
    if audio_doc:
        print("Sample audio transcript:\n", audio_doc.page_content[:400])
    
    # youtube test
    video_url = "https://www.youtube.com/watch?v=-moW9jvvMr4"
    yt_doc = load_youtube(video_url)
    if yt_doc and yt_doc.page_content.strip():
        print("Sample YouTube transcript:\n", yt_doc.page_content[:400])
    else:
        print("No transcript available for this video.")

    # manual transcript input
    manual_text = """to determine if a given set of
parentheses is valid this is a very
basic problem but at the same time it is
very very important because it has a lot
of different applications and it is
asked in a lot of different ways the
underlying concept however Remains the
Same One such sample problem is
available on lead code so let's see what
we can do about it Hello friends welcome
back to my Channel first I will explain
you the problem statement and we will
look at some sample test cases going
forward I want to quickly go over what
do you actually mean by valid
parenthesis and then we will try to
approach the problem gradually we will
take the help of a stack data structure
and then arrive at an efficient solution
as usual we will also do a dry run off
the code so that you can understand and
visualize how all of this is actually
working in action without further Ado
let's get
[Music]
started first of all let us try to make
Problem Statement
sure that we're understanding the
problem statement correctly in this
problem you are given a string that has
both the opening and closing brackets of
all the different types so you have
curly braces you have the normal
brackets and you have the square
brackets as well correct and now you
have to determine which of these strings
are valid so when it comes to valid
parenthesis what is the rule that you
should know the Only Rule that you
should know is that if you are opening a
certain kind of parentheses then you
have to close it as well and you have to
close all of these brackets in the same
order in which you are opening them so
if you're opening the normal brackets
first then you have to close them first
as well in the second example if you are
opening the square brackets first then
you open the curly brackets first then
first of all you have to close the curly
brackets and only then you can close the
square brackets so that is what a valid
parenthesis actually mean so in this
problem let us say you have these sample
test cases for the first test case you
can see that we open a normal bracket
and we close it so I can say that for
the first test case this string is valid
and I will return a true correct if you
look at the second test case now I open
a square bracket first and then I open a
curly bracket after that if you check I
close my curly bracket as well so so far
so good move ahead now I open a normal
parenthesis and then I close it as well
so this is is also valid and now what
are you left with you are left with one
more square bracket and you close it so
this string is also valid so once again
you return a true for the third test
case what do you do you open a normal
bracket first and now before you can
close any other bracket first of all you
have to close this one but what are we
doing over here we close a square
bracket first and this is not valid so
for this particular test case you need
to return false as your answer so if you
feel that the problem treatment is now
even clear to you feel free to first try
it out otherwise let us dive into the
solution before you start working out a
Understand valid parentheses
solution you must first try to
understand why these problems are
important and what are its applications
for example you might have seen these
kind of equations right and if I ask you
that go ahead and solve it how do you
approach this you do not just jump on it
right you will try to analyze this
string and then determine that hey this
is an inner bracket and that is what I
have to solve First Once I solve this
then I will look at some other bracket
and then I will start looking at all of
these outer brackets as well so this is
why valid parentheses are very important
they tell you the order in which you
have to go about solving your problem if
this string was invalid let us say
instead of this string you had a curly
braces over here right then how do you
you solve this problem it is not
possible Right This is not telling you
anything so that is why these problems
are really important and you will find
them in a lot of interviews basically
what you can now do is you can get rid
of all of these variables and all of
these operators so ultimately your
equation translates to a string like
this and you just have to determine if
this string has valid parentheses or not
if you try to approach this problem in a
Brute Force way how would you go about
it you would Traverse this string and
then you will try to solve this
innermost bracket first so what I'm
doing is I'm traversing the string and I
get all of these opening brackets right
next if you move ahead you see a closing
bracket over here right and now you go
back and check hey where did I find the
opening bracket you found it over here
so you know that okay this is the
portion that I have to solve so for a
root Force approach you will start to
move from the front until you get a
closing bracket as soon as you get a
closing bracket you move backward and
try to find the opening bracket you
found this pair right so you will remove
it from your string and now your problem
becomes this you got rid of one set of
brackets once again you will do the same
approach right you will start to look
ahead and then you will find a closing
bracket once again you go back to see
hey where is my opening bracket you
found this and then once again you will
eliminate this set of brackets so now
you get this string you will keep on
doing this ahead and ultimately if all
brackets are gone yes the string was
valid otherwise you will have one or the
other dangling brackets and that is how
you can say that hey this string is not
valid so this is a Brute Force approach
and it will work every time but you will
end up taking a lot of time just to
analyze your string again and again
correct so definitely it can be done in
a better way if you try to notice when
you are traversing your string and as
soon as you find a closing bracket what
do you look for you look for the opening
bracket right so you will look for the
most recent bracket that you had
encountered and that gives you a hint
what does that mean it means the last
character you just encountered that is
last in first out and it gives you the
hint of a stack data structure if you're
new to stack data structures I would
highly recommend you to pause this video
and look at my introductory video on
Stacks first but if you're aware with
them let us move ahead and take
advantage of the stack data structure to
come up with a very efficient solution
Using stacks for efficiency
okay so now I have a stack data
structure and I have the same string
with me you have to determine if this
string has valid parentheses or not one
way to approach this problem will be
that you start traversing the string
from the beginning and what is the first
character that you get you get an
opening bracket right so if your string
has to be valid and if you get a opening
square bracket then definitely you will
want a closing square bracket as well
correct so what you do is as soon as you
get a opening square bracket just add a
closing square bracket to your stack and
now move ahead now you get a opening
curly bracket and if your string has to
be valid then there should be one
closing curly bracket as well correct so
I will add a closing curly bracket to my
stack as well just wait for it a little
while and all of it will make sense to
you now move ahead what do you see you
see a normal opening bracket over here
right and for your string to be valid
you should have a closing normal bracket
also right and if you notice what are we
doing over here we got all of these
brackets in this order right and in our
stack I am storing this order I'm
preserving this order so what happens
next I see a closing bracket this time
as soon as you see a closing bracket you
need to search hey do I have opening
brackets for it now look in your stack
if you pop an element what do you find
you find a closing bracket that means
there was one opening bracket as well
right so it simply means that this set
has been taken care of so what I will do
is I will just remove this element from
my stack and now just move ahead once
again you see a opening square bracket
an opening square bracket means there
has to be a closing square bracket also
so just add it to the stack so basically
if you're getting any opening bracket
just add its reverse closing bracket to
the stack and now you have a closing
bracket as soon as you see a closing
bracket just look at the top element in
your stack the top element is the same
it means that hey I was able to find a
pair so once again just remove this now
move ahead what is the next element it
is a closing curly bracket look in your
stack you have your closing curly
bracket over here so just remove this
element once again so far so good what
happens now you get a opening normal
bracket so add a closing normal bracket
to your stack move ahead you get a
normal closing bracket so look in your
stack it is the same so just pop this
element and you can move ahead you get
the last element and that is a closing
bracket and if you look in your stack
you have the closing square bracket as
well they both are same so you simply
remove it from the stack if you notice
you have traversed the entire string and
your stack is also empty that means all
of the brackets are taken care of so if
this condition is true if you reach the
end of the string and your stack is
empty you return a true so if you notice
in just one scan of the string you were
able to determine if you have valid
parenthesis or not similarly let us look
at one example where the parentheses are
not valid what will happen then you have
a opening bracket so I will add a
closing bracket in here correct the next
one is a opening curly braces so I add a
closing curly braces the next is a
normal parenthesis so I add a closing
parenthesis move ahead now you see a
closing parenthesis over here and on
your stack also you have a closing
parenthesis so well and good you remove
this now move ahead you get a opening
square bracket so you add equivalent
closing bracket over here move ahead now
you see a closing curly bracket but if
you check your stack you have a closing
square bracket and these two are not the
same that simply tells you that one of
the brackets did not close properly or
one of the brackets did not open
properly so as soon as these two
elements do not match simply stop over
there you can say that this string is
invalid and return false as your answer
now based upon this idea let us quickly
do a dry around of the code and see how
it works in action on the left side of
Dry-run of Code
your screen you have the actual code to
implement this solution and on the right
I have a sample string that is passed in
as a input parameter to the function is
valid so beginning off with the dry run
what is the first thing that we do first
of all we create a character stack and
this will store all of my parenthesis
moving ahead what do we do now we start
a fall Loop that will iterate over each
of these characters in my given string
and what do we do over here we check
each of these characters so if I get any
of the opening parentheses then I will
add its equivalent closing parentheses
to my stack so if I have a square
bracket then I will add the closing
square bracket to my stack if I have a
opening curly brace then I will add the
closing curly brace to my stack so for
the first three elements I will add
their equivalent closing brackets to my
stack now look at the next step what
happens if you get any other character
than the opening bracket so let let us
say I get a character that is a closing
bracket right it won't match any of
these conditions so what do we do we try
to pop from the stack and on popping if
I find the same element then well and
good just pop the stack and continue on
otherwise you can simply return a false
so for this particular scenario as soon
as you pop they both are same so the
Stag gets popped out and your Loop will
run once again once again you encounter
this opening bracket so you will add a
equivalent closing bracket over here so
this Loop will go on and at any instant
if the closing bracket does not match
the top of the stack then you will
simply return a false or at any moment
if your stack is not empty at the very
end then also you can simply return a
false because it means one or the other
parenthesis did not either open or close
correctly the time complexity of this
solution is order of n because you only
do one iteration to Traverse through the
entire array and the space complexity of
this solution is also order of n because
you need that extra space to store all
of the elements in your stack I hope I
was able to simplify the problem and its
solution for you as for my final
Final Thoughts
thoughts I just want to say that this
problem has a lot of different
applications for example right now you
just have to determine if this set of
parentheses are valid then there can be
an extension that you have inserted all
the variables and some operators as well
then how do you determine if it is a
valid string going forward someone can
ask you okay what is the maximum depth
of the nesting of the parenthesis that
you can find similarly you can also be
asked that okay what is the minimum
number of parentheses that you have to
remove to make this a valid parentheses
string so all of these problems are
related and they all take the help of
the stack data structure so let me know
what all such problems you come across
also let me know what problems have you
found while going throughout the video
tell me everything in the comment
section below and it will be helpful for
anyone else also who is watching the
video as a reminder if you found this
video helpful please do consider
subscribing to my channel and share this
video with your friends also a huge
shout out to all the members who support
my channel this really keeps me going
also I want to give you a quick update
as I will be releasing my playlist on
all the introductory concept of graphs
so stay tuned and until next time

"""
    manual_doc = load_manual_transcript(manual_text)
    if manual_doc:
        print("Sample Manual Text:\n", manual_doc.page_content[:400])

    # pdf test
    pdf_docs = load_pdf("C:\\Users\\BIT\\Downloads\\SE\\software_Engg_Chapter_01.pdf")
    if pdf_docs:
        print("Sample PDF text:\n", pdf_docs[0].page_content[:400])

    # ppt test
    ppt_docs = load_pptx("C:\\Users\\BIT\\Downloads\\NLP\\NLP-Slides.pptx")
    if ppt_docs:
        print("Sample PPT text:\n", ppt_docs[0].page_content[:400])
