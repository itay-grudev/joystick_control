![20210507_032928](https://user-images.githubusercontent.com/2123767/117381465-cffa5c80-aee4-11eb-8e47-0c8790b86ac5.jpg)


## FAQ

### WTF is this `joystick_control` Itay?

Well I recently got a Logitech G X56 HOTAS controller and because it's always on
my desk I decided to give it functions not only when I'm playing a game, like:
* Volume control
* Switching between headphones and speakers and moving existing audio outputs to the corresponding sink
* Individual control of the volume of speakers and headphones (sometimes I'm listening to music while on a call).

### What else can it do?

For now - just that. I add stuff as I need them.

### Why share something this silly then?

You may be able to adapt it for something else. It's kind of universal.

### Why Python?

Why not... It's pretty easy to prototype something like this, and every major Linux distro comes with Python installed.

### Can it do `X`?

Most likely.

### Will it work on Windows?

Uhmm. Yes. The joystick code. The volume control code currently supports only PulseAudio, which is the GNU/Linux audio subsystem. But feel free to add your own implementation and submit an MR.

### Is there a better way to add mappings, but hard-coding them?

Not for now, mostly because I don't need it. If you do - add an issue (or better an MR). A clever mapping system work lovely.

### Can I use it for my stuff?

Yes you can, although I choose to distribute it under GPL so you have to make any changes you make open source. I would like to improve the project over time, so feel free to send me MRs.
