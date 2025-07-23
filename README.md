# 💖 6c75 Fast Uploader: Your Speedy Clip Companion! 💖

Hey there, fellow clip enthusiasts! 👋 Are you tired of manually uploading your awesome gaming moments or funny videos? Wish there was a magical little helper to whisk them away to your favorite sharing platform with a snap? ✨

Look no further! The **6c75 Fast Uploader** is here to sprinkle some automation fairy dust on your workflow! 🧚‍♀️ This adorable Python script is designed to make your life easier by automatically finding your latest video clips and sending them off using ShareX. How sweet is that? 🍬

## What's Inside This Little Treasure? 🎁

This charming tool comes packed with some delightful features:

*   **Auto-Magic Uploads!** 🪄 It sniffs out your freshest video (MP4, MKV, MOV, AVI, WMV) and gets it ready for its grand debut.
*   **ShareX Sidekick!** 🤝 Works hand-in-hand with ShareX to send your clips to your preferred host (like `ezhost` – how convenient!).
*   **Cutesy Config GUI!** 🎀 A super-friendly graphical interface (powered by Tkinter) lets you tweak settings like your ShareX host, toast notification position, and duration. It's as easy as pie! 🥧
*   **Folder Fun Facts!** 📊 Get adorable stats about your video folders, including file counts, total sizes, average sizes, and even the most popular video format. Knowledge is power, and also super cute! 💪
*   **Toast Notifications!** 🍞 Get a sweet little pop-up to confirm your upload, so you know your clip is on its way to stardom! 🌟

## How to Get Started (It's a Breeze!) 🌬️

1.  **ShareX is Your Pal:** Make sure you have [ShareX](https://getsharex.com/) installed, as this little script relies on its magic! ✨
2.  **Pop the Script:** Place `6c75_fast_uploader.py` in the directory where you keep your video folders.
3.  **Run and Revel!** Double-click the script, or run it from your terminal. If there's a new video, it'll try to upload it! If not, or if you just want to adjust things, the cute settings window will pop right up! 💖

## Settings You Can Tweak! 🎨

When the settings window appears, you'll find some lovely options:

*   **ShareX Host:** Tell the uploader which ShareX custom uploader to use (e.g., `ezhost`).
*   **Toast Position:** Decide where you want your adorable upload notifications to appear on your screen.
*   **Toast Duration:** How long should your sweet little notification stay on screen? You decide!

## A Little Note on the Magic! 📝

This script is designed to be a helpful little assistant. It looks for the *absolute latest video file* in your current directory and its subfolders. If it finds one that hasn't been uploaded before (it keeps a tiny memory in `fast_uploader.json`!), it'll try to send it off.

## Credits & Hugs! 🤗

Made with love by `6c75/luinbytes` (find more at [github.com/luinbytes](https://github.com/luinbytes)) with a little help from the friendly Gemini CLI! 🤖💖

Enjoy your super-fast, super-cute clip uploads! 🎉
