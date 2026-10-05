/**
 * Interactive Mock Interview Simulator Tool
 */

const INTERVIEW_QUESTION_BANK = {
  dsa: [
    {
      q: "How would you detect a cycle in a singly linked list with O(1) auxiliary memory?",
      topic: "Linked Lists & Pointers",
      hints: "Think about two pointers traversing at different speeds (Floyd's Cycle-Finding Algorithm).",
      modelAnswer: "Use Floyd's Tortoise and Hare algorithm: Initialize slow and fast pointers to head. Move slow by 1 step, fast by 2 steps. If fast equals slow at any point, a cycle exists. If fast or fast.next reaches null, no cycle exists. Time complexity is O(N), Space complexity is O(1)."
    },
    {
      q: "Explain how you would design an LRU (Least Recently Used) Cache supporting get() and put() in O(1) time.",
      topic: "System & Data Structure Design",
      hints: "Combine a hash map for fast key lookup with a doubly linked list for maintaining order of access.",
      modelAnswer: "Use a Doubly Linked List paired with a Hash Map. The Hash Map stores keys mapping to node pointers (giving O(1) lookup). The Doubly Linked List keeps the access frequency order: most recently accessed at head, least recently used at tail. Removing from tail and inserting at head are both O(1) pointer updates."
    },
    {
      q: "What is the difference between BFS and DFS traversal on a graph, and when should you prefer BFS over DFS?",
      topic: "Graphs & Trees",
      hints: "Consider shortest path in unweighted graphs vs memory depth and cycle detection.",
      modelAnswer: "BFS visits neighbors level by level using a queue, guaranteeing the shortest path in unweighted graphs. DFS explores paths deeply using recursion or a stack. Prefer BFS for finding shortest paths, nearest neighbors, or connected components within small radius. Prefer DFS for maze solving, topological sorting, or memory-constrained scenarios."
    }
  ],
  backend: [
    {
      q: "What are database indexes, how do B-Trees optimize SELECT queries, and what is the trade-off on INSERTs?",
      topic: "Databases & SQL Optimization",
      hints: "Think about binary search across balanced multi-way tree blocks vs index update overhead on writes.",
      modelAnswer: "An index is an auxiliary data structure (typically a balanced B-Tree or B+ Tree) that stores sorted keys and row pointers. It reduces search complexity from an O(N) full table scan to O(log N). The trade-off is that every INSERT, UPDATE, or DELETE must also rewrite and rebalance the B-Tree indexes, adding write latency and consuming extra disk storage."
    },
    {
      q: "Explain the difference between SQL transactions' ACID properties and NoSQL's BASE principles.",
      topic: "Database Architecture",
      hints: "Strict consistency vs high availability and eventual consistency in distributed systems.",
      modelAnswer: "ACID (Atomicity, Consistency, Isolation, Durability) guarantees strict transactional safety, suitable for banking and core placement data. BASE (Basically Available, Soft state, Eventual consistency) prioritizes high availability and partition tolerance over immediate consistency in horizontally scaled distributed systems."
    }
  ],
  hr: [
    {
      q: "Tell me about a time you faced a difficult conflict in a team project. How did you resolve it?",
      topic: "Behavioral & Conflict Resolution",
      hints: "Structure your response using the STAR method: Situation, Task, Action, Result.",
      modelAnswer: "Use the STAR technique: Describe the specific project (Situation), your responsibility (Task), the empathetic, communication-driven steps you took to listen and find consensus (Action), and the measurable positive outcome such as on-time delivery or high project score (Result)."
    },
    {
      q: "Why do you want to join our company, and where do you see your career heading in the next 3 to 5 years?",
      topic: "Company Fit & Career Aspirations",
      hints: "Highlight alignment with the company's tech stack, engineering culture, and your desire to grow from IC to technical lead.",
      modelAnswer: "Align your personal skills (e.g., Python, full-stack systems, performance engineering) with their mission. Mention your enthusiasm to contribute as a high-impact software engineer, master scalable system architectures, and progressively mentor incoming juniors while contributing to critical infrastructure."
    }
  ]
};

document.addEventListener('DOMContentLoaded', () => {
  const startBtn = document.getElementById('btn-start-mock');
  if (!startBtn) return;

  const topicSelect = document.getElementById('mock-topic-select');
  const sessionBox = document.getElementById('mock-session-box');
  const questionText = document.getElementById('mock-question-text');
  const topicBadge = document.getElementById('mock-topic-badge');
  const timerDisplay = document.getElementById('mock-timer-display');
  const nextBtn = document.getElementById('btn-next-question');
  const hintBtn = document.getElementById('btn-show-hint');
  const hintBox = document.getElementById('mock-hint-box');
  const modelAnswerBtn = document.getElementById('btn-show-model-answer');
  const modelAnswerBox = document.getElementById('mock-model-answer-box');

  let currentQuestions = [];
  let currentIndex = 0;
  let timerInterval = null;
  let secondsRemaining = 180; // 3 minutes per question

  startBtn.addEventListener('click', () => {
    const topic = topicSelect ? topicSelect.value : 'dsa';
    currentQuestions = INTERVIEW_QUESTION_BANK[topic] || INTERVIEW_QUESTION_BANK['dsa'];
    currentIndex = 0;
    
    sessionBox.style.display = 'block';
    sessionBox.scrollIntoView({ behavior: 'smooth' });
    loadQuestion(0);
  });

  function loadQuestion(index) {
    if (index >= currentQuestions.length) {
      alert("Congratulations! You have completed all questions for this mock interview session.");
      clearInterval(timerInterval);
      return;
    }

    const q = currentQuestions[index];
    questionText.textContent = q.q;
    topicBadge.textContent = q.topic;
    
    // Reset hints & answer boxes
    if (hintBox) {
      hintBox.style.display = 'none';
      hintBox.textContent = q.hints;
    }
    if (modelAnswerBox) {
      modelAnswerBox.style.display = 'none';
      modelAnswerBox.textContent = q.modelAnswer;
    }

    // Reset Timer (180s)
    clearInterval(timerInterval);
    secondsRemaining = 180;
    updateTimerText();

    timerInterval = setInterval(() => {
      secondsRemaining--;
      updateTimerText();
      if (secondsRemaining <= 0) {
        clearInterval(timerInterval);
        alert("Time is up for this question! Review the model answer before moving forward.");
      }
    }, 1000);
  }

  function updateTimerText() {
    if (!timerDisplay) return;
    const mins = Math.floor(secondsRemaining / 60);
    const secs = secondsRemaining % 60;
    timerDisplay.textContent = `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    if (secondsRemaining < 30) {
      timerDisplay.style.color = '#f43f5e';
    } else {
      timerDisplay.style.color = '#38bdf8';
    }
  }

  if (hintBtn) {
    hintBtn.addEventListener('click', () => {
      if (hintBox) hintBox.style.display = hintBox.style.display === 'block' ? 'none' : 'block';
    });
  }

  if (modelAnswerBtn) {
    modelAnswerBtn.addEventListener('click', () => {
      if (modelAnswerBox) modelAnswerBox.style.display = modelAnswerBox.style.display === 'block' ? 'none' : 'block';
    });
  }

  if (nextBtn) {
    nextBtn.addEventListener('click', () => {
      currentIndex++;
      loadQuestion(currentIndex);
    });
  }
});
