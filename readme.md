## Overview

An MPV game of mine that I want to quickly get up and running to test and see if it is actually a fun game that people might like (firstly me and family/friends) or not. If it is, then perhaps I'll invest more time in this and create a proper product.

This is an experiment as well, to see how far I can get with almost fully AI-generated code. The idea is that I will let it generate all of the code, and I will review it. But, instead of just giving requirements and acting a non-tech product guy, I give specific commands to what to do exactly. I.e. I design the code such that it is easy to maintain and extend it, and I use AI as a quick typing machine to achieve what I want. I then review the generated code - not to check the correctness, but to ensure that the design has been followed and implemented correctly.

The biggest reason for this approach is to make sure that as the codebase grows, the AI doesn't get tangled on its own low-quality spaghetti code. In my practice, most AIs fail on large codebases, just because it has become a mess over time and every new symbol has unimaginable side effects as well as the logic for a simple business-component is implemented inside many files and components and lacks isolation. Obviously, AI also learned from more of this type of code than anything else, so I can't allow it to become its own worst enemy.

The caveat here is that due to the time constraints, I cannot make sure that all the good practices are followed – hence, I only focus on the things that I think will damage the maintainability the most and can cause this MVP project to fail horribly.


## Links

Technical (AI-generated):
1. [code_architecture.md](docs/code_architecture.md)
1. [game_design.md](docs/game_design.md)

Project Management:
1. [progress.md](docs/progress.md)