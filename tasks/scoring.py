from datetime import date, datetime


def parse_due_date(value):
    if not value:
        return None

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    return None


def calculate_task_score(task_data, strategy="smart_balance"):
    today = date.today()
    score = 0
    reasons = []

    importance = task_data.get("importance", 5) or 5
    try:
        importance = int(importance)
    except (TypeError, ValueError):
        importance = 5

    estimated_hours = task_data.get("estimated_hours", 1) or 1
    try:
        estimated_hours = float(estimated_hours)
    except (TypeError, ValueError):
        estimated_hours = 1

    dependencies = task_data.get("dependencies") or []
    if not isinstance(dependencies, list):
        dependencies = []

    dependents_count = task_data.get("dependents_count", 0) or 0
    try:
        dependents_count = int(dependents_count)
    except (TypeError, ValueError):
        dependents_count = 0

    in_cycle = bool(task_data.get("in_cycle", False))

    due_date = parse_due_date(task_data.get("due_date"))

    if strategy == "fastest_wins":
        urgency_weight = 1.5
        importance_weight = 3
        quick_bonus_factor = 1.5
    elif strategy == "high_impact":
        urgency_weight = 1.5
        importance_weight = 6
        quick_bonus_factor = 1.0
    elif strategy == "deadline_driven":
        urgency_weight = 3
        importance_weight = 4
        quick_bonus_factor = 1.0
    else:  
        urgency_weight = 2
        importance_weight = 5
        quick_bonus_factor = 1.2

    if due_date:
        days_until_due = (due_date - today).days

        if days_until_due < 0:
            base = 100
            bonus = base * urgency_weight / 2
            score += bonus
            reasons.append(f"Overdue task → +{bonus:.0f}")
        elif days_until_due <= 1:
            base = 70
            bonus = base * urgency_weight / 2
            score += bonus
            reasons.append(f"Due within 1 day → +{bonus:.0f}")
        elif days_until_due <= 3:
            base = 50
            bonus = base * urgency_weight / 2
            score += bonus
            reasons.append(f"Due within 3 days → +{bonus:.0f}")
        elif days_until_due <= 7:
            base = 30
            bonus = base * urgency_weight / 2
            score += bonus
            reasons.append(f"Due within 7 days → +{bonus:.0f}")
        else:
            reasons.append("Due later than 7 days → +0")
    else:
        reasons.append("No due date provided → treated as low urgency")

    importance_score = importance * importance_weight
    score += importance_score
    reasons.append(
        f"Importance {importance} × {importance_weight} → +{importance_score}"
    )

    if estimated_hours <= 1:
        quick_bonus = 25 * quick_bonus_factor
        score += quick_bonus
        reasons.append(f"Very quick task (≤1h) → +{quick_bonus:.0f}")
    elif estimated_hours <= 2:
        quick_bonus = 15 * quick_bonus_factor
        score += quick_bonus
        reasons.append(f"Quick task (≤2h) → +{quick_bonus:.0f}")
    elif estimated_hours >= 8:
        penalty = 10
        score -= penalty
        reasons.append(f"Large task (≥8h) → -{penalty}")
    else:
        reasons.append("Medium effort → +0")

    if dependencies:
        dep_penalty = 5 * len(dependencies)
        score -= dep_penalty
        reasons.append(f"{len(dependencies)} dependencies → -{dep_penalty}")
    else:
        score += 5
        reasons.append("No dependencies → +5")

    if dependents_count > 0:
        bonus = 8 * dependents_count
        score += bonus
        reasons.append(
            f"Unblocks {dependents_count} other task(s) → +{bonus}"
        )

    if in_cycle:
        penalty = 30
        score -= penalty
        reasons.append("In circular dependency group → -30 (needs attention)")

    explanation = "; ".join(reasons)
    return round(score, 2), explanation