var BASE_URL = "http://127.0.0.1:8000/api/tasks";

function getStrategy() {
  var select = document.getElementById("strategySelect");
  return select && select.value ? select.value : "smart_balance";
}

function parseTasksFromTextarea() {
  var raw = document.getElementById("taskInput").value || "[]";
  try {
    var data = JSON.parse(raw);
    if (!Array.isArray(data)) {
      alert("JSON must be an array of tasks.");
      return null;
    }
    return data;
  } catch (e) {
    console.error("JSON parse error:", e);
    alert("Invalid JSON. Please check your input.");
    return null;
  }
}

function updateTextarea(tasks) {
  document.getElementById("taskInput").value = JSON.stringify(tasks, null, 2);
}

function addTask(event) {
  event.preventDefault();

  var title = document.getElementById("titleInput").value.trim();
  var due = document.getElementById("dueInput").value.trim();
  var hours = document.getElementById("hoursInput").value;
  var importance = document.getElementById("importanceInput").value;
  var depsRaw = document.getElementById("depsInput").value.trim();

  if (!title) {
    alert("Title is required.");
    return;
  }

  var dependencies = [];
  if (depsRaw) {
    dependencies = depsRaw
      .split(",")
      .map(function (s) {
        return s.trim();
      })
      .filter(function (s) {
        return s.length > 0;
      })
      .map(function (s) {
        var n = Number(s);
        return isNaN(n) ? s : n;
      });
  }

  var newTask = {
    title: title,
    due_date: due || null,
    estimated_hours: hours ? Number(hours) : 1,
    importance: importance ? Number(importance) : 5,
    dependencies: dependencies
  };

  var current = parseTasksFromTextarea();
  if (current === null) return;

  current.push(newTask);
  updateTextarea(current);

  // Reset form fields
  document.getElementById("taskForm").reset();
  document.getElementById("hoursInput").value = 1;
  document.getElementById("importanceInput").value = 5;
}

async function analyzeTasks() {
  var tasks = parseTasksFromTextarea();
  if (!tasks) return;

  var strategy = getStrategy();

  try {
    var res = await fetch(BASE_URL + "/analyze/?strategy=" + strategy, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(tasks)
    });

    if (!res.ok) {
      var err = await res.json();
      throw new Error(err.detail || "Request failed");
    }

    var sorted = await res.json();
    document.getElementById("summaryArea").textContent =
      'Analyzed ' + sorted.length + ' task(s) using "' + strategy + '" strategy.';
    displayResults(sorted);
  } catch (err) {
    console.error("Analyze error:", err);
    alert("Failed to analyze tasks: " + err.message);
  }
}

async function suggestTasks() {
  var tasks = parseTasksFromTextarea();
  if (!tasks) return;

  var strategy = getStrategy();

  try {
    var res = await fetch(BASE_URL + "/suggest/?strategy=" + strategy, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(tasks)
    });

    if (!res.ok) {
      var err = await res.json();
      throw new Error(err.detail || "Request failed");
    }

    var data = await res.json();
    var suggested = data.suggested_tasks || [];

    document.getElementById("summaryArea").textContent = data.summary || "";
    displayResults(suggested);
  } catch (err) {
    console.error("Suggest error:", err);
    alert("Failed to suggest tasks: " + err.message);
  }
}

function displayResults(tasks) {
  var container = document.getElementById("results");
  container.innerHTML = "";

  if (!tasks || tasks.length === 0) {
    container.textContent = "No tasks to display.";
    return;
  }

  tasks.forEach(function (task) {
    var card = document.createElement("div");
    card.classList.add("task-card");

    var header = document.createElement("div");
    header.classList.add("task-header");

    var title = document.createElement("div");
    title.classList.add("task-title");
    title.textContent = task.title || "Untitled task";

    var badge = document.createElement("span");
    badge.classList.add("badge");

    var score = typeof task.score === "number" ? task.score : 0;
    var priorityLabel = "Low";
    var priorityClass = "priority-low";

    if (score >= 100) {
      priorityLabel = "High";
      priorityClass = "priority-high";
    } else if (score >= 60) {
      priorityLabel = "Medium";
      priorityClass = "priority-medium";
    }

    badge.textContent = priorityLabel + " (" + score + ")";
    badge.classList.add(priorityClass);

    header.appendChild(title);
    header.appendChild(badge);

    var meta = document.createElement("div");
    meta.classList.add("task-meta");

    var dueText = task.due_date ? task.due_date : "No due date";
    var imp = typeof task.importance !== "undefined" ? task.importance : "-";
    var hours = typeof task.estimated_hours !== "undefined" ? task.estimated_hours : "-";
    var depsCount = Array.isArray(task.dependencies)
      ? task.dependencies.length
      : 0;
    var dependents = typeof task.dependents_count !== "undefined"
      ? task.dependents_count
      : 0;
    var inCycle = task.in_cycle ? "Yes" : "No";

    meta.textContent =
      "Due: " + dueText +
      " | Importance: " + imp +
      " | Hours: " + hours +
      " | Dependencies: " + depsCount +
      " | Blocks: " + dependents +
      " | In cycle: " + inCycle;

    var explanation = document.createElement("div");
    explanation.classList.add("task-explanation");
    explanation.textContent = task.explanation || "";

    card.appendChild(header);
    card.appendChild(meta);
    card.appendChild(explanation);

    container.appendChild(card);
  });
}