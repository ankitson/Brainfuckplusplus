Brainfuck++ (now with pretend-threads!)
======================================

Usage:

   echo "whatever input you want" | python ./brainfuck++.py thread1 thread2 thread3 ...

What..... why?
-------------

Because it was a fun project and I got inspired

Ok, but how does it work?
------------------------

Like so: brainfuck++.py takes in one or more arguments, each one being a file containing brainfuck++ code, and runs them simultaneously
in ticks. Each brainfuck command takes one tick to run, so if in one thread you have `>+` and in another you have `<-`, the `>` and `<` get run at the
same time, followed by the `+` and `-` getting run at the same time.

All threads share the same memory array, but act independently otherwise. The brainfuck input character `,` reads data from stdin.
There is checking to make sure:

* Multiple threads aren't editing the same memory space at the same time
* Multiple threads aren't reading from stdin at the same time
* Multiple threads aren't writing to stdout at the same time
* One thread isn't reading from a space being written to by another thread

Is there anything else new?
--------------------------

Yeah, two shiny new commands!

The first is `_`, it literally does nothing. It's simply a placeholder if you want one of your threads to kill time during a tick.

The second is `!`, the sync command. When a thread hits a sync, it will stay at that sync command and not move forward in the command
list until all other threads have hit a sync command as well. Here's an example:

Thread 1:
`+++!`

Thread 2:
`!---`

On the first three ticks thread 1 will be incrementing while thread 2 will be stuck at the sync command. On the fourth tick thread 1 hits 
the sync as well. On the fifth tick thread 2 will do its first decrement, and thread 1 will be out of commands and won't do anything.

So what the hell inspired you to do this?
----------------------------------------

I was playing [SpaceChem](http://spacechemthegame.com/), where you essentially control two running threads by making them run certain commands
at certain times in order to build molecules (although in SpaceChem you have to worry about positioning too; it's a great game and if you
enjoy puzzles you should for sure check it out). I had the thought that I could easily make a similarly functioning language where you have
two completely seperate instruction sets designed to closely interact with each other. Obviously this isn't a new thought, it's basically what
threading is, but I wondered how easy it would be for a language with a very simple instruction set where it would be easy for the programmer to
easily predict the interaction of the two threads.

Why does the main title say "pretend-threads"?
---------------------------------------------

Because a brainfuck++ program only pretends to run two instruction sets at the same time, it's actually single threaded. It could run on a truly
multi-threaded implementation if someone was feeling spry.

What version of python does this work on?
----------------------------------------

My python is 3.2.3, I haven't tested it on anything else.

Your python is bad and you should feel bad
-----------------------------------------

Most of it was written in a single one hour code sprint at two in the morning, sue me.
