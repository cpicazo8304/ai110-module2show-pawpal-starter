# PawPal+ Project Reflection

## 1. System Design

# Three main actions a user could do: 

-A user could add their and their pet's info.
-A user could add events that have different time lengths and priorities.
-A user could see a visualization of their plan.


**a. Initial design**

- Briefly describe your initial UML design.

The UML class diagram for PawPal+ consists of six main classes: User, Pet, Task, DailyPlan, Scheduler, and Constraint.

- User represents the pet owner with attributes like name, pet, and preferences, and methods to update preferences and get pet info.
- Pet represents the pet with name, type, and optional age, and a method to get info.
- Task represents care tasks with type, duration, priority, and preferred time, and methods to update priority and duration.
- DailyPlan represents a day's plan with a list of tasks, total time, and constraints, and methods to manage tasks and calculate time.
- Scheduler generates plans using tasks and constraints, with methods to sort tasks, apply constraints, and explain plans.
- Constraint defines rules like max time and preferred times, with methods to check and apply constraints.

Relationships include User having a Pet, DailyPlan containing Tasks and Constraints, and Scheduler managing Tasks, using Constraints, and generating DailyPlans.

- What classes did you include, and what responsibilities did you assign to each?

I included the User, Pet, Task, DailyPlan, Scheduler, and Constraints classes. User is for the pet owner. Pet is for the pet being cared for. Task represents a single task. DailyPlan is the plan for the day. Scheduler is responsible for generating the daily plan. Constraints holds the rules the Scheduler must follow.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, I asked Copilot to see if I was missing anything or if it could recommend some additions that could work, and it suggested to included a Constraints class that would help with flow of the code. This would make classes like DailyPlan and Scheduler to not have more methods and attributes than it needed.

I also had changes to the time constraint. I wanted to include a more natural time rather than just "afternoon, morning, etc.".

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

The constraints the scheduler considers is mainly the time constraint. I have the user be required to name all their available times throughout the day and also the time length of each of this free openings. I used these variables to determine if a task could fit into the user's schedule.

- How did you decide which constraints mattered most?

I thought that 'times available' would be the most realistic and important constraint. It helps organize the day well for the scheduler. "Priority" does make sense like feeding should be before a certain other task. However, I found that time naturally handles this already. Since tasks are sorted chronologically before being added to the plan, scheduling a feeding at 8:00 AM and a walk at 9:00 AM effectively enforces priority through time alone, without needing a separate priority field.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

The scheduler prioritizes simplicity by using time availability as the only hard constraint, leaving out a formal priority system. This means the user is fully responsible for deciding when tasks happen. There is no built-in logic to enforce that.

- Why is that tradeoff reasonable for this scenario?

For a daily pet care scheduler, tasks tend to be routine and predictable, so most users will naturally schedule them in a sensible order without needing the app to enforce it. Keeping the constraint model simple also makes the scheduler easier to understand.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

-I mainly used it as a debugger. This was a project that had a simple concept but came with lots of parts and features. So, making sure everything was working and not having a single feature break other features was important. Copilot and Claude helped a lot making suggestions and debugging my code.

- What kinds of prompts or questions were most helpful?

The most helpful was having the AI apply comments to where the changes were made (mainly for Claude outside of VS code). Copilot able to do this on its own since it is embedded into the VS code platform, but Claude being able to label the locations of fixes, made it easier for me to check over the changes and approve them.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

I wanted to compare ChatGPT with Copilot and Claude, but it would suggest high-level libraries that I don't know about, so I would just ignore it, and move on to just the ideas I was trying to suggest and implement in my own way. 

- How did you evaluate or verify what the AI suggested?

With my known knowledge, I analyze the code before making any changes to see if it made sense, then I did an additional check of looking at how it worked in the app. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

I tested the sorting, filtering, automated recurring tasks, conflict detection, and completion filtering. 

- Why were these tests important?

These tests were important because they tested the more advanced behaviors that are more susceptible to mistakes and logical errors. Also, they are the backbone to this app. If any of these behaviors don't work, to can break the whole system, so making sure they are working well is significant.

**b. Confidence**

- How confident are you that your scheduler works correctly?

I am fairly confident because of how I organized it. By splitting into two classes essentially (DailyPlan and Scheduler), it made it easier to organize the different methods. 

- What edge cases would you test next if you had more time?

I would probably test if my conflict detection system not only looks at conflicting tasks of the same pet but also between pets. This could give a good idea of how advanced the conflict detection system is. 

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am most satisfied about how I handle the multiple pets scenario. I knew I had to have different tabs for each pet, but didn't know how to, but Copilot helped me with some methods streamlit has that allows for this, which makes it much easier. Once I had implemented it, I was really happy with how the app was looking. 

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would try to move some of the logic from my DailyPlan class to my Scheduler class. I think I can make a lot of that work in the Scheduler. Then again, DailyPlan does help my code be more readable, which is really important for looking back at your code and understanding what you had done or what the AI had helped you with. But, I did find certain things like adding or removing tasks tough, so maybe moving that to Scheduler or handling this concept better would have made it easier for me. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that organization, brainstorming, and visualization is very important. If you don't fully understand what you are doing, then maybe the structure is too complex. Being okay with deleting some features to build on simpler ones is much better than keeping on adding more.


**Reflect on AI Strategy:** 

- Specifically describe your experience with VS Code Copilot:

VS Code Copilot did excellent in providing a very well made skeleton. I usually didn't want to do large amounts of code so I won't fall behind in understanding the code and the main features, but it helped debugging, fixing my code, suggesting improvements, etc.

- Which Copilot features were most effective for building your scheduler?

Agent and edit mode did well in suggesting methods that could either add to the ones I came up with or improve on some of them.

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.

AI tools in general seem to struggle with errors undelined by the pylance, so I usually just figure those out on my own, by backtracking and looking through the code and asking AI about different libraries (which is where it helped but not with fully understanding what was going on). 

- How did using separate chat sessions for different phases help you stay organized?

It helped know where to ask certain questions. If I was focusing on a certain file, I would go to one chat, and if I was working on another, I would go to the other chat. If I needed to go back and check what Copilot said, it was easier to find. Sometimes, these sessions can get very long if you keep on asking questions (especially when it doesn't give what you want) so utilizing different sessions helped.

- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.

I learned to repeatedly check on the code and see if it worked, made changes when needed, debugged properly, and only ask AI for specific implementations rather than broad implementations.