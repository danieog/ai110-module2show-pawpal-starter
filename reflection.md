# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
    Three core actions that my app should do is let users is add a pet and themselves, add walks and/or any other aspects of their schedule, and add tasks. I would like to have a class dedicated to having pet information, schedule events and any tasks respectively. 
    Building blocks:
        Attritbutes:
        - Owners
        - Tasks
        - Pets
        - Schedules
        Methods:
        - Adding/editing tasks
        - Adding/removing pets to owners
        - Adding information about pets and owners
        - Adjusting the schedule with new tasks
        - Sending reminders about each task
        - Sorting tasks by due dates

**c. Mermaid class diagram**

```mermaid
classDiagram
    class Owner {
        +pets: List~Pet~
        +tasks: List~Task~
        +schedules: List~Scheduler~
        +addOwnerInfo(name, contact)
        +addPet(pet: Pet)
        +removePet(pet: Pet)
    }

    class Pet {
        +name: string
        +species: string
        +age: int
        +addPetInfo(info)
    }

    class Task {
        +title: string
        +dueDate: datetime
        +status: string
        +addTask(taskInfo)
        +editTask(taskInfo)
    }

    class Scheduler {
        +tasks: List~Task~
        +adjustSchedule(task: Task)
        +sendReminder(task: Task)
        +sortTasksByDueDate()
    }

    Owner "1" --> "0..*" Pet : owns
    Owner "1" --> "0..*" Task : manages
    Owner "1" --> "0..*" Scheduler : uses
    Scheduler "1" --> "0..*" Task : schedules
    Pet "1" --> "0..*" Task : needs
```

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
My design did change during implemention, since I _____.

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
