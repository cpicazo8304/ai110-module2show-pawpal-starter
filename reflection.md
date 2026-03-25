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
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
