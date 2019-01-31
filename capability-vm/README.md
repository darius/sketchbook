Draft of a virtual machine intended to support writing a toy
capability OS. The general idea was, you'd write user programs in a
language kinda like Forth which would map directly to VM instructions.
My experience coding for my Forth dialect Tusl was nice enough that
this seems a reasonable goal, saving us from having to
implement/target any fancier language to the capability VM.

(The OS itself, in my vague plans, was not be implemented as Forth
code on the VM, but instead in the VM's implementation language along
with the VM. The logical gymnastics of kernel-versus-user-code seemed
like a distraction from the stuff I wanted to learn here.)

This particular sketch of a Forth dialect was not feeling very
promising of fun to code with, at the point I set it aside.
