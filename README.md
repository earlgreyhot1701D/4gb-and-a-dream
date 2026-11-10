# 4 GB and a Dream

**How far can a 4 GB Chromebook go?**

Every build in this repo was made from an HP Chromebook 11a with 4 GB of memory, using [Claude](https://claude.ai) and [GitHub](https://github.com). No IDE. Nothing installed on the laptop. Claude did the building in a cloud workspace and pushed every commit here from the chat.

This is the companion repo for the dev.to article *A Small Laptop Is a Full Build Kit: Bootstrapping with a Chromebook, Claude, and GitHub*. [TODO: link once published]

**Live:** https://earlgreyhot1701d.github.io/4gb-and-a-dream/

## The rounds

| Round | Build | What it shows | Folder |
|---|---|---|---|
| 1 | [Necesito](https://github.com/earlgreyhot1701D/necesito) | A live app with no editor | Its own repo |
| 2 | Papel picado, in 3D | Interactive 3D, drawn by the laptop you're on | `round-2-3d/` |
| 3 | The bootstrapping path | An animated diagram of every step, with a button that drops the Wi-Fi | `round-3-diagram/` |
| 4 | Demo video | Made without video software | Coming soon |

## The kit

| Part | What | Cost |
|---|---|---|
| Laptop | HP Chromebook 11a: MediaTek Kompanio 500, 4 GB of memory | Already owned |
| Browser | Chrome | Free |
| Code and hosting | GitHub and GitHub Pages | Free |
| AI that builds | Claude, working in a cloud workspace | Paid plan |

## Round 2: Papel picado, in 3D

Three strings of papel picado flags swaying across a dusk sky, with warm string lights and stars.

- **Drag** or use the **arrow keys** to spin. **Pinch**, **scroll**, or **+ / −** to zoom.
- A **frame-rate meter** in the corner shows how smoothly your device is drawing it.
- It **pauses when the tab is hidden**, so a background tab costs nothing.
- It respects **reduced motion** settings: no swaying if your device asks for less motion.
- One HTML file and one library: [three.js](https://threejs.org) r128, loaded from cdnjs.

Building happened in the cloud. Drawing happens on your device, so this round is the one that makes a small laptop work.

## Round 3: The bootstrapping path

Six steps from a laptop to a live link, colored by where each one runs: on the laptop, in Claude's cloud workspace, or on GitHub. Only two of the six happen on the laptop.

- **Play, pause, or step through** with the buttons. Captions are read aloud by screen readers.
- **Drop the Wi-Fi** cuts the laptop's link and shows the cloud steps carrying on without it, which is what happened during the Necesito build.
- A glowing **thread** unspools to the current step, so your eye follows the path. Steps behind it fill in, and steps ahead stay dim.
- Styled in the [Clew Labs](https://clewlabs.org) colors. The thread is the clew.
- Plain HTML, CSS, and a little JavaScript. No libraries.
- Respects **reduced motion**: it starts paused and the moving dashes stay still.

## Credits

Idea by [Alex Shev](https://dev.to/alexshev), who asked for the bootstrapping path and a capability table.

Built by [L. Cordero](https://dev.to/earlgreyhot1701d) with Claude (Opus 5.5). I directed and decided. Claude wrote the code.

AI assisted. Human approved. Powered by NLP.

MIT License
