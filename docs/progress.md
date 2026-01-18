## ToDo Notes

1. Actions should be executed as part of update loop & instead of being called by each other, they should be scheduled in a queue that the game loop will use to invoke actions.
   * Also means that Level should become Scene and everything should be a Scene, even menus and other screens
1. Lift pickup & scheduling logic
   1. Test correctness. For example, if a customer is next to an open lift that HE WAS allocated, then he should enter it - currently sometimes lift moves without taking the customer in, although he is standing in front of it
   1. Add automation options like: (a) Smart, where the lift goes to the latest scheduled on its current direction and then starts delivering customers, (b) NoAutomation, where Lift prioritizes assigned pickups, and always goes to pick up customers that were assigned to it - in the order which they were assigned. Need to think about the automation options
1. Make the lifts data customizable via configs similar to the spawn locations other level-related data.
   * Additionally, we need to add other configurations like speed and levels that it won't stop (e.g. available only for delivering from 0 to top 2 floors only)

## Other Game Mechanics That Might Be Good (maybe for later)

1. Game Modes
   * A mode, where the X next customers are shown with the timers next to them as when they will come and from where (perhaps this queue can be displayed on top of the spawn location itself?).
   * A mode where there's a penalty limit after which the game ends. The amount of successful deliveries becomes the goal in this case
   * A random mode, based on a visible seed, to be able to reproduce. Finishes after X customers or Y seconds/minutes.
1. All of the above in a real-time online or with a shared online leaderboard.

## VISION

1. All this is done for the sole purpose of actually testing the gameplay and understanding if it would be a fun game or not!
1. I also want to publish this in some sort of community, let's say itch.io? For initial feedback