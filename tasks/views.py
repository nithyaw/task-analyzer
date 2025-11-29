import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .scoring import calculate_task_score
from django.shortcuts import render

def home(request):
    return render(request, "index.html")


def normalize_task(raw_task, index):
    task_id = raw_task.get("id", index)
    return {
        "id": task_id,
        "title": raw_task.get("title", f"Task {index + 1}"),
        "due_date": raw_task.get("due_date"),
        "estimated_hours": raw_task.get("estimated_hours", 1),
        "importance": raw_task.get("importance", 5),
        "dependencies": raw_task.get("dependencies", []),
    }


def build_dependency_graph(tasks):
    deps = {}
    dependents_count = {}

    for task in tasks:
        tid = task["id"]
        deps_list = task.get("dependencies", []) or []
        if not isinstance(deps_list, list):
            deps_list = []
        deps[tid] = deps_list

        if tid not in dependents_count:
            dependents_count[tid] = 0

    for task in tasks:
        tid = task["id"]
        for dep_id in task.get("dependencies", []) or []:
            dependents_count.setdefault(dep_id, 0)
            dependents_count[dep_id] += 1

    return deps, dependents_count


def detect_cycles(deps):
    visited = set()
    stack = set()
    in_cycle = set()

    def dfs(node):
        if node in stack:
            in_cycle.update(stack)
            return
        if node in visited:
            return

        visited.add(node)
        stack.add(node)
        for neighbor in deps.get(node, []):
            if neighbor in deps:  
                dfs(neighbor)
        stack.remove(node)

    for node in deps.keys():
        if node not in visited:
            dfs(node)

    return in_cycle


def parse_body(request):
    try:
        body = request.body.decode("utf-8")
        data = json.loads(body)
        if not isinstance(data, list):
            raise ValueError("Expected a list of tasks.")
        return data, None
    except Exception as e:
        return None, str(e)


@csrf_exempt
def analyze_tasks(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Only POST allowed."}, status=405)

    raw_tasks, error = parse_body(request)
    if error:
        return JsonResponse(
            {"detail": "Invalid JSON body.", "error": error}, status=400
        )

    strategy = request.GET.get("strategy", "smart_balance")

    normalized_tasks = [normalize_task(t, i) for i, t in enumerate(raw_tasks)]
    deps_map, dependents_count = build_dependency_graph(normalized_tasks)
    cycle_ids = detect_cycles(deps_map)

    results = []
    for t in normalized_tasks:
        tid = t["id"]
        t["dependents_count"] = dependents_count.get(tid, 0)
        t["in_cycle"] = tid in cycle_ids

        score, explanation = calculate_task_score(t, strategy=strategy)
        t["score"] = score
        t["explanation"] = explanation
        results.append(t)

    results.sort(key=lambda x: x["score"], reverse=True)

    return JsonResponse(results, safe=False)


@csrf_exempt
def suggest_tasks(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Only POST allowed."}, status=405)

    raw_tasks, error = parse_body(request)
    if error:
        return JsonResponse(
            {"detail": "Invalid JSON body.", "error": error}, status=400
        )

    strategy = request.GET.get("strategy", "smart_balance")

    normalized_tasks = [normalize_task(t, i) for i, t in enumerate(raw_tasks)]
    deps_map, dependents_count = build_dependency_graph(normalized_tasks)
    cycle_ids = detect_cycles(deps_map)

    scored = []
    for t in normalized_tasks:
        tid = t["id"]
        t["dependents_count"] = dependents_count.get(tid, 0)
        t["in_cycle"] = tid in cycle_ids

        score, explanation = calculate_task_score(t, strategy=strategy)
        t["score"] = score
        t["explanation"] = explanation
        scored.append(t)

    scored.sort(key=lambda x: x["score"], reverse=True)
    top_three = scored[:3]

    lines = []
    for i, task in enumerate(top_three, start=1):
        lines.append(
            f"{i}. '{task['title']}' (Score: {task['score']}) – {task['explanation']}"
        )

    summary = " | ".join(lines) if lines else "No tasks provided."

    return JsonResponse(
        {
            "strategy": strategy,
            "suggested_tasks": top_three,
            "summary": summary,
        },
        safe=True,
    )